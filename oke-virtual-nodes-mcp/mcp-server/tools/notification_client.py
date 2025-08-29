import oci
import logging
import os
import json
from datetime import datetime, timedelta
import random
from typing import Dict, Any, Optional, List
from oci.retry import DEFAULT_RETRY_STRATEGY
import uuid
from oci.ons.models import MessageDetails

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_notification_client():
    """Initialize and return the OCI NoSQL client based on environment."""
    is_dev_env = os.environ.get("ENVIRONMENT", "").lower() == "dev"
    
    if is_dev_env:
        logger.debug("Loading OCI configuration for Dev environment")
        config = oci.config.from_file()
        config["connection_timeout"] = 10.0
        config["read_timeout"] = 120.0
        logger.debug(f"OCI config loaded: {config.get('region')}")
        logger.debug("Initializing NoSQL client with config")
        return oci.ons.NotificationDataPlaneClient(config)
    else:
        logger.debug("Loading OCI signer for non-Dev environment")
        signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()
        region = os.environ.get("OCI_REGION", "us-ashburn-1")
        logger.debug("Initializing NoSQL client with signer")
        return oci.ons.NotificationDataPlaneClient(
            config={"region": region},
            signer=signer)
    
def get_topic_id() -> str:
    """Get the compartment ID from environment variables."""
    topic_id = os.environ.get("NOTIFICATION_TOPIC_ID")
    if not topic_id:
        raise ValueError("NOTIFICATION_TOPIC_ID environment variable is required")
    return topic_id
    
def issue_refund_for_order(order_id: str) -> Dict[str, Any]:
    """
    Initiate refund for orderid.
    
    Args:
        order_id (str): Order ID
        
    Returns:
        bool: success or error
    """
    logger.info(f"Initiatint refund for OrderId: {order_id}")
    
    try:
        topic_id = get_topic_id()
        
        # Set subject and message
        subject = "Refund Issued"
        message = f"Hello, this is a inform you that your Order number: {order_id}! is cancelled."
        
        # Publish the message
        publish_details = MessageDetails(
            title=subject,
            body=message
        )
        notification_client = create_notification_client()
        response = notification_client.publish_message(
            topic_id,
            message_details=publish_details
        )

        logger.info("Message published. Message ID: %s", response.data.message_id)
        return {
            "success": True,
            "orderId": order_id,
            "message": "Order cancelled successfully"
        }
                
    except Exception as e:
        logger.error(f"Error cancelling order: {order_id} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to cancel order"
        }