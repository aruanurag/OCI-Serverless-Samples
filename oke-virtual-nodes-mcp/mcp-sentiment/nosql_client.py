import oci
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from oci.retry import DEFAULT_RETRY_STRATEGY

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_nosql_client():
    """Initialize and return the OCI NoSQL client based on environment."""
    is_dev_env = os.environ.get("ENVIRONMENT", "").lower() == "dev"
    
    if is_dev_env:
        logger.debug("Loading OCI configuration for Dev environment")
        config = oci.config.from_file()
        config["connection_timeout"] = 10.0
        config["read_timeout"] = 120.0
        logger.debug(f"OCI config loaded: {config.get('region')}")
        logger.debug("Initializing NoSQL client with config")
        return oci.nosql.NosqlClient(config)
    else:
        logger.debug("Loading OCI signer for non-Dev environment")
        signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()
        region = os.environ.get("OCI_REGION", "us-ashburn-1")
        logger.debug("Initializing NoSQL client with signer")
        return oci.nosql.NosqlClient(
            config={"region": region},
            signer=signer)

def get_compartment_id() -> str:
    """Get the compartment ID from environment variables."""
    compartment_id = os.environ.get("COMPARTMENT_ID")
    if not compartment_id:
        raise ValueError("COMPARTMENT_ID environment variable is required")
    return compartment_id

def get_table_name() -> str:
    """Get the table name from environment variables with default fallback."""
    return os.environ.get("NOSQL_TABLE_NAME", "sentiment_analysis_results")

def create_table_if_not_exists(table_name: str, compartment_id: str) -> bool:
    """
    Create the sentiment analysis results table if it doesn't exist.
    
    Args:
        table_name (str): Name of the table to create
        compartment_id (str): OCI compartment ID
        
    Returns:
        bool: True if table exists or was created successfully, False otherwise
    """
    try:
        nosql_client = create_nosql_client()
        
        # Check if table exists
        try:
            logger.debug(f"Checking if table {table_name} exists")
            nosql_client.get_table(
                table_name_or_id=table_name,
                compartment_id=compartment_id
            )
            logger.info(f"Table {table_name} already exists")
            return True
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                logger.info(f"Table {table_name} doesn't exist, creating it")
                # Table doesn't exist, create it
                pass
            else:
                logger.error(f"Service error checking table: {e.message}")
                raise
        
        # Define table schema
        table_details = oci.nosql.models.CreateTableDetails(
            name=table_name,
            compartment_id=compartment_id,
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
        
        logger.debug("Creating table with schema")
        # Create table
        create_response = nosql_client.create_table(
            create_table_details=table_details
        )
        
        logger.debug("Waiting for table to become active")
        # Wait for table to be active
        waiter = oci.wait_until(
            nosql_client,
            create_response,
            'lifecycle_state',
            'ACTIVE',
            max_wait_seconds=300
        )
        
        logger.info(f"Table {table_name} created successfully")
        return True
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error creating table: {e.message}, Status: {e.status}, Code: {e.code}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating table: {str(e)}")
        return False

def upload_sentiment_result(
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
    logger.info(f"Starting sentiment result upload for text: {text_content[:50]}...")
    
    try:
        # Get configuration
        compartment_id = get_compartment_id()
        table_name = get_table_name()
        
        # Ensure table exists
        if not create_table_if_not_exists(table_name, compartment_id):
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
        
        logger.debug(f"Preparing to insert row with ID: {record_id}")
        
        # Get NoSQL client
        nosql_client = create_nosql_client()
        
        # Insert row
        insert_response = nosql_client.update_row(
            table_name_or_id=table_name,
            update_row_details=oci.nosql.models.UpdateRowDetails(
                value=row_data,
                is_get_return_row=True
            ),
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        logger.info(f"Successfully uploaded sentiment result with ID: {record_id}")
        
        return {
            "success": True,
            "record_id": record_id,
            "timestamp": row_data["analysis_timestamp"],
            "message": "Sentiment result uploaded successfully"
        }
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error uploading sentiment result: {e.message}, Status: {e.status}, Code: {e.code}")
        return {
            "success": False,
            "error": f"Service error: {e.message}",
            "message": "Failed to upload sentiment result"
        }
    except Exception as e:
        logger.error(f"Unexpected error uploading sentiment result: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to upload sentiment result"
        }

def query_sentiment_results(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Query sentiment analysis results from the table.
    
    Args:
        user_id (str, optional): Filter results by user ID
        session_id (str, optional): Filter results by session ID
        limit (int): Maximum number of results to return
        
    Returns:
        Dict[str, Any]: Query results
    """
    logger.info(f"Starting sentiment results query - user_id: {user_id}, session_id: {session_id}, limit: {limit}")
    
    try:
        # Get configuration
        compartment_id = get_compartment_id()
        table_name = get_table_name()
        
        # Build query
        query = f"SELECT * FROM {table_name}"
        where_conditions = []
        
        if user_id:
            where_conditions.append(f"user_id = '{user_id}'")
        if session_id:
            where_conditions.append(f"session_id = '{session_id}'")
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        query += f" ORDER BY analysis_timestamp DESC LIMIT {limit}"
        
        logger.debug(f"Executing query: {query}")
        
        # Get NoSQL client
        nosql_client = create_nosql_client()
        
        # Execute query
        query_response = nosql_client.query(
            query=query,
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        logger.debug(f"Query response received with {len(query_response.data.items)} items")
        
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
        
        logger.info(f"Successfully queried {len(results)} sentiment results")
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error querying sentiment results: {e.message}, Status: {e.status}, Code: {e.code}")
        return {
            "success": False,
            "error": f"Service error: {e.message}",
            "message": "Failed to query sentiment results"
        }
    except Exception as e:
        logger.error(f"Unexpected error querying sentiment results: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to query sentiment results"
        }

def delete_sentiment_result(record_id: str) -> Dict[str, Any]:
    """
    Delete a specific sentiment analysis result from the table.
    
    Args:
        record_id (str): The ID of the record to delete
        
    Returns:
        Dict[str, Any]: Deletion result with success status
    """
    logger.info(f"Starting deletion of sentiment result with ID: {record_id}")
    
    try:
        # Get configuration
        compartment_id = get_compartment_id()
        table_name = get_table_name()
        
        # Get NoSQL client
        nosql_client = create_nosql_client()
        
        # Delete row
        delete_response = nosql_client.delete_row(
            table_name_or_id=table_name,
            key=[record_id],
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        logger.info(f"Successfully deleted sentiment result with ID: {record_id}")
        
        return {
            "success": True,
            "record_id": record_id,
            "message": "Sentiment result deleted successfully"
        }
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error deleting sentiment result: {e.message}, Status: {e.status}, Code: {e.code}")
        return {
            "success": False,
            "error": f"Service error: {e.message}",
            "message": "Failed to delete sentiment result"
        }
    except Exception as e:
        logger.error(f"Unexpected error deleting sentiment result: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete sentiment result"
        }

def get_table_stats() -> Dict[str, Any]:
    """
    Get statistics about the sentiment analysis results table.
    
    Returns:
        Dict[str, Any]: Table statistics
    """
    logger.info("Getting table statistics")
    
    try:
        # Get configuration
        compartment_id = get_compartment_id()
        table_name = get_table_name()
        
        # Get NoSQL client
        nosql_client = create_nosql_client()
        
        # Get table details
        table_response = nosql_client.get_table(
            table_name_or_id=table_name,
            compartment_id=compartment_id
        )
        
        # Get row count (approximate)
        count_query = f"SELECT COUNT(*) as total FROM {table_name}"
        count_response = nosql_client.query(query=count_query)
        total_rows = count_response.data.items[0]["total"] if count_response.data.items else 0
        
        stats = {
            "success": True,
            "table_name": table_name,
            "compartment_id": compartment_id,
            "lifecycle_state": table_response.data.lifecycle_state,
            "time_created": table_response.data.time_created.isoformat() if table_response.data.time_created else None,
            "time_updated": table_response.data.time_updated.isoformat() if table_response.data.time_updated else None,
            "total_rows": total_rows
        }
        
        logger.info(f"Successfully retrieved table statistics: {total_rows} rows")
        return stats
        
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error getting table stats: {e.message}, Status: {e.status}, Code: {e.code}")
        return {
            "success": False,
            "error": f"Service error: {e.message}",
            "message": "Failed to get table statistics"
        }
    except Exception as e:
        logger.error(f"Unexpected error getting table stats: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get table statistics"
        }
