import io
import json
import oci
import logging
import base64
from io import BytesIO

from fdk import response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(ctx, data: str = None):
    """
    OCI Function handler to post a message to an OCI Queue using Resource Principal.
    
    Args:
        ctx: Function context
        data: Input data (JSON string)
    
    Returns:
        JSON response indicating success or failure
    """
    try:
        # Initialize Resource Principal signer
        signer = oci.auth.signers.get_resource_principals_signer()

        # Get region from function configuration or default to us-ashburn-1
        region = ctx.Config().get("OCI_REGION", "us-ashburn-1")
        
        # Set endpoint explicitly
        endpoint = f"https://cell-1.queue.messaging.{region}.oci.oraclecloud.com"

        # Initialize Queue client with the correct endpoint
        config = {
            "region": ctx.Config().get("QUEUE_OCID")
        }
        
        # Initialize Queue client
        queue_client = oci.queue.QueueClient(config=config, signer=signer, service_endpoint= endpoint)
        
        # Get queue OCID from function configuration
        queue_ocid = ctx.Config().get("QUEUE_OCID")
        if not queue_ocid:
            raise ValueError("QUEUE_OCID not found in function configuration")
        
        # Handle input data (string or BytesIO)
        if data is None:
            raise ValueError("No payload provided in POST body")
        
        # If data is BytesIO (e.g., from fn invoke), read and decode it
        if isinstance(data, BytesIO):
            data = data.read().decode('utf-8')
        
        # Parse the input as JSON
        payload = json.loads(data)
        
        # Validate payload structure
        if not isinstance(payload, dict) or "data" not in payload:
            raise ValueError("Invalid payload format: 'data' key is missing")
        if not all(key in payload["data"] for key in ["order_id", "customer_id", "amount"]):
            raise ValueError("Invalid payload: 'order_id', 'customer_id', and 'amount' are required in 'data'")
        
        # Convert payload to JSON string and encode as base64
        message_content = json.dumps(payload)
        
        # Prepare message
        message = {
            "content": message_content,
            "contentType": "application/json"
        }
        
        put_messages_details = oci.queue.models.PutMessagesDetails(
            messages=[oci.queue.models.PutMessagesDetailsEntry(content=message["content"])]
        )
        
        response = queue_client.put_messages(
            queue_id=queue_ocid,
            put_messages_details=put_messages_details
        )
        
        # Check response
        if response.status == 200:
            logger.info(f"Successfully posted message to queue {queue_ocid}")
            return {
                "status": "success",
                "messageId": response.data.messages[0].id
            }
        else:
            logger.error(f"Failed to post message: {response.status}")
            return {
                "status": "error",
                "message": f"Failed to post message: {response.status}"
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
