import oci
import json
import logging
import os
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def poll_queue_and_insert_to_nosql():
    """
    Polls an OCI Queue and inserts messages into a NoSQL table using Resource Principal authentication.
    """
    try:
        # Initialize Resource Principal signer
        signer = oci.auth.signers.get_resource_principals_signer()
        
        # Get configuration from environment variables
        region = os.environ.get("OCI_REGION", "us-ashburn-1")
        queue_ocid = os.environ.get("QUEUE_OCID")
        table_ocid = os.environ.get("TABLE_OCID")
        
        if not queue_ocid:
            raise ValueError("QUEUE_OCID not found in environment variables")
        if not table_ocid:
            raise ValueError("TABLE_OCID not found in environment variables")
        
        # Initialize Queue client with explicit endpoint
        queue_endpoint = f"https://cell-1.queue.messaging.{region}.oci.oraclecloud.com"
        logger.info(f"Configuring QueueClient with endpoint: {queue_endpoint}")
        queue_client = oci.queue.QueueClient(
            config={"region": region},
            service_endpoint=queue_endpoint,
            signer=signer
        )
        
        # Initialize QueueAdminClient for administrative operations
        queue_admin_client = oci.queue.QueueAdminClient(
            config={"region": region},
            signer=signer
        )
        
        # Initialize NoSQL client
        nosql_client = oci.nosql.NosqlClient(
            config={"region": region},
            signer=signer
        )
        
        # Verify queue existence
        try:
            # pylint: disable=no-member
            queue_response = queue_admin_client.get_queue(queue_id=queue_ocid)
            logger.info(f"Queue {queue_ocid} is accessible: Status {queue_response.status}")
        except oci.exceptions.ServiceError as e:
            logger.error(f"Failed to access queue {queue_ocid}: {e.message}, Status: {e.status}, Code: {e.code}, Request ID: {e.request_id}")
            raise
        
        # Polling loop
        while True:
            try:
                # Read messages from the queue
                messages_response = queue_client.get_messages(
                    queue_id=queue_ocid,
                    visibility_in_seconds=60,  # Time message is invisible after reading
                    timeout_in_seconds=30     # Wait time for messages
                )
                
                if messages_response.status != 200 or not messages_response.data.messages:
                    logger.info(f"No messages found in queue {queue_ocid}")
                    time.sleep(10)  # Wait before polling again
                    continue
                
                # Process each message
                for message in messages_response.data.messages:
                    logger.info(f"Processing message ID: {message.id}")
                    
                    # Log raw message content for debugging
                    logger.debug(f"Raw message content: {message.content}")
                    
                    # Parse message content as JSON (no base64 decoding)
                    try:
                        payload = json.loads(message.content)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parsing error for message {message.id}: {str(e)}")
                        continue
                    
                    # Validate payload structure
                    if not isinstance(payload, dict) or "data" not in payload:
                        logger.error(f"Invalid payload format for message {message.id}: 'data' key is missing")
                        continue
                    if not all(key in payload["data"] for key in ["order_id", "customer_id", "amount"]):
                        logger.error(f"Invalid payload for message {message.id}: 'order_id', 'customer_id', and 'amount' are required in 'data'")
                        continue
                    
                    # Prepare NoSQL record
                    record = {
                        "order_id": payload["data"]["order_id"],
                        "customer_id": payload["data"]["customer_id"],
                        "amount": payload["data"]["amount"],
                        "created_at": datetime.utcnow().isoformat()
                    }
                    
                    # Insert record into NoSQL table
                    try:
                        update_row_details = oci.nosql.models.UpdateRowDetails(
                            value=record,
                            option="IF_ABSENT"  # Only insert if the row doesn't exist
                        )
                        nosql_response = nosql_client.update_row(
                            table_name_or_id=table_ocid,
                            update_row_details=update_row_details
                        )
                        
                        if nosql_response.status == 200:
                            logger.info(f"Successfully inserted record into table {table_ocid} for message {message.id}")
                            
                            # Delete the processed message from the queue
                            queue_client.delete_message(
                                queue_id=queue_ocid,
                                message_receipt=message.receipt
                            )
                            logger.info(f"Deleted message {message.id} from queue {queue_ocid}")
                        else:
                            logger.error(f"Failed to insert record into table {table_ocid} for message {message.id}: {nosql_response.status}")
                    except oci.exceptions.ServiceError as e:
                        logger.error(f"NoSQL error for message {message.id}: {e.message}, Status: {e.status}, Code: {e.code}, Request ID: {e.request_id}")
                        continue
                
                # Sleep briefly to avoid overwhelming the queue
                time.sleep(1)
                
            except oci.exceptions.ServiceError as e:
                logger.error(f"Queue service error: {e.message}, Status: {e.status}, Code: {e.code}, Request ID: {e.request_id}")
                time.sleep(10)  # Wait before retrying
                continue
            
            except Exception as e:
                logger.error(f"Unexpected error while polling queue: {str(e)}")
                time.sleep(10)  # Wait before retrying
                continue
                
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        poll_queue_and_insert_to_nosql()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        exit(1)