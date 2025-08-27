import oci
import logging
import os
import base64
from oci.ai_document.models import AnalyzeDocumentDetails, DocumentFeature, InlineDocumentContent
from oci.retry import DEFAULT_RETRY_STRATEGY

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_ai_client():
    """Initialize and return the OCI AI Document Understanding client based on environment."""
    is_dev_env = os.environ.get("ENVIRONMENT", "").lower() == "dev"
    
    if is_dev_env:
        logger.debug("Loading OCI configuration for Dev environment")
        config = oci.config.from_file()
        config["connection_timeout"] = 10.0
        config["read_timeout"] = 120.0
        logger.debug(f"OCI config loaded: {config.get('region')}")
        logger.debug("Initializing AI Document Understanding client with config")
        return oci.ai_document.AIServiceDocumentClient(config)
    else:
        logger.debug("Loading OCI signer for non-Dev environment")
        signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()
        region = os.environ.get("OCI_REGION", "us-ashburn-1")
        logger.debug("Initializing AI Document Understanding client with signer")
        return oci.ai_document.AIServiceDocumentClient(
            config={"region": region},
            signer=signer)

def classify_document(file_path: str) -> dict:
    logger.info(f"Starting document classification for file: {file_path}")
    try:
        ai_client = create_ai_client()

        logger.debug("Reading document file")
        with open(file_path, "rb") as f:
            document_data = f.read()
        encoded_data = base64.b64encode(document_data).decode('utf-8')

        logger.debug("Preparing inline document content")
        inline_content = InlineDocumentContent(data=encoded_data)

        logger.debug("Preparing analysis details with DOCUMENT_CLASSIFICATION feature")
        features = [DocumentFeature(feature_type="DOCUMENT_CLASSIFICATION")]
        details = AnalyzeDocumentDetails(document=inline_content, features=features)

        logger.debug("Performing document analysis")
        response = ai_client.analyze_document(analyze_document_details=details, retry_strategy=DEFAULT_RETRY_STRATEGY)
        logger.debug(f"Analysis response received: {response.data}")

        detected_types = response.data.detected_document_types
        result = {
            "document_classifications": [
                {"type": dt.document_type, "confidence": dt.confidence} for dt in detected_types
            ]
        }
        logger.info("Document classification completed successfully")
        return result
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error: {e.message}, Status: {e.status}, Code: {e.code}")
        return {"error": f"Service error: {e.message}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}