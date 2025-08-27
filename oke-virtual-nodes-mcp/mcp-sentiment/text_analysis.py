import oci
import logging
import os
from oci.ai_language.models import TextDocument, BatchDetectLanguageSentimentsDetails, BatchDetectLanguageKeyPhrasesDetails
from oci.retry import DEFAULT_RETRY_STRATEGY

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_ai_client():
    """Initialize and return the OCI AI Language client based on environment."""
    is_dev_env = os.environ.get("ENVIRONMENT", "").lower() == "dev"
    
    if is_dev_env:
        logger.debug("Loading OCI configuration for Dev environment")
        config = oci.config.from_file()
        config["connection_timeout"] = 10.0
        config["read_timeout"] = 120.0
        logger.debug(f"OCI config loaded: {config.get('region')}")
        logger.debug("Initializing AI Language client with config")
        return oci.ai_language.AIServiceLanguageClient(config)
    else:
        logger.debug("Loading OCI signer for non-Dev environment")
        signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()
        region = os.environ.get("OCI_REGION", "us-ashburn-1")
        logger.debug("Initializing AI Language client with signer")
        return oci.ai_language.AIServiceLanguageClient(
            config={"region": region},
            signer=signer)

def analyze_text(text: str) -> dict:
    logger.info(f"Starting text analysis for input: {text[:50]}...")  # Log first 50 chars
    try:
        ai_client = create_ai_client()

        logger.debug("Preparing text document")
        text_document = TextDocument(key="input_text", text=text, language_code="en")

        logger.debug("Performing text classification")
        text_classification = ai_client.batch_detect_language_text_classification(
            batch_detect_language_text_classification_details=oci.ai_language.models.BatchDetectLanguageTextClassificationDetails(
                documents=[text_document]
            )
        )
        logger.debug(f"Text classification received: {text_classification.data}")
        
        logger.debug("Performing key phrase extraction")
        key_phrase_details = BatchDetectLanguageKeyPhrasesDetails(documents=[text_document])
        key_phrase_response = ai_client.batch_detect_language_key_phrases(key_phrase_details, retry_strategy=DEFAULT_RETRY_STRATEGY)
        logger.debug(f"Key phrase response received: {key_phrase_response.data}")
        
        result = {
            "text_classification": {
                "label": text_classification.data.documents[0].text_classification[0].label,
                "score": text_classification.data.documents[0].text_classification[0].score
            },
            "key_phrases": [kp.text for kp in key_phrase_response.data.documents[0].key_phrases]
        }
        logger.info("Text analysis completed successfully")
        return result
    except oci.exceptions.ServiceError as e:
        logger.error(f"Service error: {e.message}, Status: {e.status}, Code: {e.code}")
        return {"error": f"Service error: {e.message}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}