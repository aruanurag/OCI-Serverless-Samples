import oci
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoSQLOperations:
    def __init__(self):
        """Initialize NoSQL operations with OCI configuration."""
        self.config = self._get_oci_config()
        self.nosql_client = None
        self.table_name = os.getenv("NOSQL_TABLE_NAME", "sentiment_analysis_results")
        self.compartment_id = os.getenv("COMPARTMENT_ID")
        
        if not self.compartment_id:
            raise ValueError("COMPARTMENT_ID environment variable is required")
        
        self._initialize_nosql_client()
    
    def _get_oci_config(self) -> Dict[str, Any]:
        """Get OCI configuration from environment variables or config file."""
        # Try to get config from environment variables first
        config = {}
        
        # Check for config file path
        config_file = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
        config_profile = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
        
        try:
            # Try to load from config file
            config = oci.config.from_file(config_file, config_profile)
            logger.info(f"Loaded OCI config from {config_file}")
        except Exception as e:
            logger.warning(f"Could not load OCI config from file: {e}")
            
            # Fallback to environment variables
            config = {
                "tenancy": os.getenv("OCI_TENANCY_ID"),
                "user": os.getenv("OCI_USER_ID"),
                "fingerprint": os.getenv("OCI_FINGERPRINT"),
                "key_file": os.getenv("OCI_KEY_FILE"),
                "region": os.getenv("OCI_REGION", "us-ashburn-1")
            }
            
            # Check if we have the minimum required config
            if not all([config["tenancy"], config["user"], config["fingerprint"], config["key_file"]]):
                raise ValueError("Insufficient OCI configuration. Please set OCI environment variables or provide a valid config file.")
            
            logger.info("Using OCI configuration from environment variables")
        
        return config
    
    def _initialize_nosql_client(self):
        """Initialize the NoSQL client."""
        try:
            self.nosql_client = oci.nosql.NosqlClient(self.config)
            logger.info("NoSQL client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NoSQL client: {e}")
            raise
    
    def create_table_if_not_exists(self) -> bool:
        """Create the sentiment analysis results table if it doesn't exist."""
        try:
            # Check if table exists
            try:
                self.nosql_client.get_table(
                    table_name_or_id=self.table_name,
                    compartment_id=self.compartment_id
                )
                logger.info(f"Table {self.table_name} already exists")
                return True
            except oci.exceptions.ServiceError as e:
                if e.status == 404:
                    # Table doesn't exist, create it
                    pass
                else:
                    raise
            
            # Define table schema
            table_details = oci.nosql.models.CreateTableDetails(
                name=self.table_name,
                compartment_id=self.compartment_id,
                ddl_statement="""
                CREATE TABLE sentiment_analysis_results (
                    id STRING,
                    text_content STRING,
                    sentiment_result STRING,
                    analysis_timestamp STRING,
                    user_id STRING,
                    session_id STRING,
                    PRIMARY KEY (id)
                )
                """
            )
            
            # Create table
            create_response = self.nosql_client.create_table(
                create_table_details=table_details
            )
            
            # Wait for table to be active
            waiter = oci.wait_until(
                self.nosql_client,
                create_response,
                'lifecycle_state',
                'ACTIVE',
                max_wait_seconds=300
            )
            
            logger.info(f"Table {self.table_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return False
    
    def upload_sentiment_result(
        self,
        text_content: str,
        sentiment_result: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload sentiment analysis result to NoSQL table.
        
        Args:
            text_content (str): The original text that was analyzed
            sentiment_result (Dict[str, Any]): The sentiment analysis result
            user_id (str, optional): User identifier
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Upload result with success status and record ID
        """
        try:
            # Ensure table exists
            if not self.create_table_if_not_exists():
                raise Exception("Failed to create or verify table existence")
            
            # Generate unique ID
            import uuid
            record_id = str(uuid.uuid4())
            
            # Prepare row data
            row_data = {
                "id": record_id,
                "text_content": text_content,
                "sentiment_result": json.dumps(sentiment_result),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "anonymous",
                "session_id": session_id or "default"
            }
            
            # Insert row
            insert_response = self.nosql_client.update_row(
                table_name_or_id=self.table_name,
                update_row_details=oci.nosql.models.UpdateRowDetails(
                    value=row_data,
                    is_get_return_row=True
                )
            )
            
            logger.info(f"Successfully uploaded sentiment result with ID: {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
                "timestamp": row_data["analysis_timestamp"],
                "message": "Sentiment result uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to upload sentiment result: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload sentiment result"
            }
    
    def query_sentiment_results(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query sentiment analysis results from the table.
        
        Args:
            user_id (str, optional): Filter by user ID
            session_id (str, optional): Filter by session ID
            limit (int): Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Query results
        """
        try:
            # Build query
            query = f"SELECT * FROM {self.table_name}"
            where_conditions = []
            
            if user_id:
                where_conditions.append(f"user_id = '{user_id}'")
            if session_id:
                where_conditions.append(f"session_id = '{session_id}'")
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            query += f" ORDER BY analysis_timestamp DESC LIMIT {limit}"
            
            # Execute query
            query_response = self.nosql_client.query(
                query=query
            )
            
            results = []
            for row in query_response.data.items:
                # Parse the sentiment_result JSON string back to dict
                sentiment_result = json.loads(row["sentiment_result"])
                results.append({
                    "id": row["id"],
                    "text_content": row["text_content"],
                    "sentiment_result": sentiment_result,
                    "analysis_timestamp": row["analysis_timestamp"],
                    "user_id": row["user_id"],
                    "session_id": row["session_id"]
                })
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to query sentiment results: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to query sentiment results"
            }

# Global instance for use in MCP tools
nosql_ops = None

def get_nosql_ops() -> NoSQLOperations:
    """Get or create a NoSQL operations instance."""
    global nosql_ops
    if nosql_ops is None:
        try:
            nosql_ops = NoSQLOperations()
        except Exception as e:
            logger.error(f"Failed to initialize NoSQL operations: {e}")
            raise
    return nosql_ops
