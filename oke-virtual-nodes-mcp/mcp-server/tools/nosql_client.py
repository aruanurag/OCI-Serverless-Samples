import oci
import logging
import os
import json
from datetime import datetime, timedelta
import random
from typing import Dict, Any, Optional, List
from oci.retry import DEFAULT_RETRY_STRATEGY
import uuid

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

def get_order_table_name() -> str:
    """Get the table name from environment variables with default fallback."""
    return os.environ.get("ORDER_TABLE_NAME", "order_info")

def get_customer_table_name() -> str:
    """Get the table name from environment variables with default fallback."""
    return os.environ.get("CUSTOMER_TABLE_NAME", "customer_info")

    

def seed_customer_info_table():
    """Seed the table with 20 sample customer records."""
    logger.info("Seeding customer info table with 20 records")
    
    # Sample data
    customer_ids = [
        "CUST01", "CUST02", "CUST03", "CUST04", "CUST05",
        "CUST06", "CUST07", "CUST08", "CUST09", "CUST10",
        "CUST11", "CUST12", "CUST13", "CUST14", "CUST15",
        "CUST16", "CUST17", "CUST18", "CUST19", "CUST20"
    ]
    sample_names = [
        "John Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis",
        "David Evans", "Eve Foster", "Frank Green", "Grace Harris", "Henry Irving",
        "Ivy Jackson", "Jack King", "Karen Lee", "Larry Miller", "Mary Nelson",
        "Nancy Owens", "Oliver Parker", "Paula Quinn", "Quincy Roberts", "Rachel Scott"
    ]
    sample_addresses = [
        "123 Main St", "456 Elm St", "789 Oak St", "101 Pine St", "202 Maple St",
        "303 Birch St", "404 Cedar St", "505 Walnut St", "606 Chestnut St", "707 Ash St",
        "808 Beech St", "909 Cherry St", "1010 Dogwood St", "1111 Elm St", "1212 Fir St",
        "1313 Grape St", "1414 Holly St", "1515 Ivy St", "1616 Juniper St", "1717 Kiwi St"
    ]
    sample_emails = [
        "john@example.com", "jane@example.com", "alice@example.com", "bob@example.com", "charlie@example.com",
        "david@example.com", "eve@example.com", "frank@example.com", "grace@example.com", "henry@example.com",
        "ivy@example.com", "jack@example.com", "karen@example.com", "larry@example.com", "mary@example.com",
        "nancy@example.com", "oliver@example.com", "paula@example.com", "quincy@example.com", "rachel@example.com"
    ]
    sample_phones = [
        "123-456-7890", "234-567-8901", "345-678-9012", "456-789-0123", "567-890-1234",
        "678-901-2345", "789-012-3456", "890-123-4567", "901-234-5678", "012-345-6789",
        "123-456-7891", "234-567-8902", "345-678-9013", "456-789-0124", "567-890-1235",
        "678-901-2346", "789-012-3457", "890-123-4568", "901-234-5679", "012-345-6790"
    ]
    table_name = get_customer_table_name()
    nosql_client = create_nosql_client()
    compartment_id = get_compartment_id()
    for i in range(20):        
        row_data = {
            "customerId": customer_ids[i],
            "name": sample_names[i],
            "address": sample_addresses[i],
            "email": sample_emails[i],
            "phone": sample_phones[i]
        }
        
        try:
            nosql_client.update_row(
                
                table_name_or_id=table_name,
                update_row_details=oci.nosql.models.UpdateRowDetails(
                    value=row_data,
                    compartment_id=compartment_id,
                    is_get_return_row=True
                ),
                retry_strategy=DEFAULT_RETRY_STRATEGY
            )
            logger.debug(f"Inserted record for {sample_names[i]} with ID: {customer_ids[i]}")
        except Exception as e:
            logger.error(f"Error inserting seed record {i+1}: {str(e)}")
    
    logger.info("Seeding completed")

def random_date(days_back=30):
    """Generate a random datetime within the last `days_back` days."""
    return datetime.now() - timedelta(days=random.randint(0, days_back))

def seed_order_info_table():
    """
    Seed the order_info table with sample data for customers.
    Each customer will get 3 random orders.
    """
    print("Seeding order_info table with random sample data...")

    customer_ids = [
        "CUST01", "CUST02", "CUST03", "CUST04", "CUST05",
        "CUST11", "CUST12", "CUST13", "CUST14", "CUST15",
        "CUST16", "CUST17", "CUST18", "CUST19", "CUST20"
    ]
    statuses = ["OPEN", "CLOSED", "SHIPPED", "CANCELLED"]
    table_name = get_order_table_name()
    nosql_client = create_nosql_client()
    compartment_id = get_compartment_id()
    for cust_id in customer_ids:
        for i in range(3):  # 3 orders per customer
            order = {
                "customerId": cust_id,
                "orderId": str(uuid.uuid4()),
                "status": random.choice(statuses),
                "date": random_date().isoformat(),
                "amount": round(random.uniform(20, 500), 2),
            }
            try:
                nosql_client.update_row(
                
                    table_name_or_id=table_name,
                    update_row_details=oci.nosql.models.UpdateRowDetails(
                        value=order,
                        compartment_id=compartment_id,
                        is_get_return_row=True
                    ),
                    retry_strategy=DEFAULT_RETRY_STRATEGY
                )
                logger.debug(f"Inserted record for cust ID: {cust_id}")
            except Exception as e:
                logger.error(f"Error inserting seed record {i+1}: {str(e)}")
    
    logger.info("Seeding completed for order info table")

def get_customer_by_email(email: str) -> Dict[str, Any]:
    """
    Read customer info based on email and return details.
    
    Args:
        email (str): Customer email
        
    Returns:
        Dict[str, Any]: Customer details or error
    """
    logger.info(f"Querying customer by email: {email}")
    
    try:
        compartment_id = get_compartment_id()
        table_name = get_customer_table_name()
        
        query = f"SELECT * FROM {table_name} WHERE email = '{email}'"
        
        nosql_client = create_nosql_client()

        query_details = oci.nosql.models.QueryDetails(
            statement=query,
            compartment_id=compartment_id
        )
        query_response = nosql_client.query(
            query_details=query_details,
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        if not query_response.data.items:
            return {
                "success": False,
                "message": "No customer found with that email"
            }
        
        row = query_response.data.items[0]
        return {
            "success": True,
            "customer": {
                "name": row["name"],
                "address": row["address"],
                "email": row["email"],
                "phone": row["phone"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error querying customer by email: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to query customer"
        }

def get_customer_id_by_email(email: str) -> Dict[str, Any]:
    """
    Get customer ID based on email.
    
    Args:
        email (str): Customer email
        
    Returns:
        Dict[str, Any]: Customer ID or error
    """
    logger.info(f"Querying customer ID by email: {email}")
    
    try:
        compartment_id = get_compartment_id()
        table_name = get_customer_table_name()
        
        query = f"SELECT customerId FROM {table_name} WHERE email = '{email}'"
        
        nosql_client = create_nosql_client()
        query_details = oci.nosql.models.QueryDetails(
            statement=query,
            compartment_id=compartment_id
        )
        query_response = nosql_client.query(
            query_details=query_details,
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        if not query_response.data.items:
            return {
                "success": False,
                "message": "No customer found with that email"
            }
        
        row = query_response.data.items[0]
        return {
            "success": True,
            "customerId": row["customerId"]
        }
        
    except Exception as e:
        logger.error(f"Error querying customer ID by email: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to query customer ID"
        }
    
def get_open_orders(customer_id: str):
    """
    Fetch all open orders for a given customerId.
    """
    logger.info(f"Querying orders for: {customer_id}")
    
    try:
        compartment_id = get_compartment_id()
        table_name = get_order_table_name()
        query = f"SELECT orderId, status, date, amount FROM {table_name} WHERE customerId = '{customer_id}' AND status = 'OPEN'"
        nosql_client = create_nosql_client()
        query_details = oci.nosql.models.QueryDetails(
            statement=query,
            compartment_id=compartment_id
        )
        query_response = nosql_client.query(
            query_details=query_details,
            retry_strategy=DEFAULT_RETRY_STRATEGY
        )
        
        open_orders = []
        for row in query_response.data.items:
            open_orders.append({
                "orderId": row["orderId"],
                "status": row["status"],
                "date": row["date"],
                "amount": row["amount"]
            })

        return open_orders
    except Exception as e:
        logger.error(f"Error querying orders for customer ID : {customer_id}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get orders"
        }

def get_table_stats() -> Dict[str, Any]:
    """
    Get statistics about the customer info table.
    
    Returns:
        Dict[str, Any]: Table statistics
    """
    logger.info("Getting table statistics")
    
    try:
        # Get configuration
        compartment_id = get_compartment_id()
        table_name = get_customer_table_name()
        
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