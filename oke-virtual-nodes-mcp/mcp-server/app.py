import os
from fastmcp import FastMCP
from tools.text_analysis import analyze_text
from tools.classify_document import classify_document
from tools.nosql_client import upload_sentiment_result, query_sentiment_results
import json
from starlette.requests import Request
from starlette.responses import PlainTextResponse

APP_NAME = os.getenv("FASTMCP_APP_NAME", "fastmcp-demo")
PORT = int(os.getenv("FASTMCP_PORT", "8080"))
HOST = os.getenv("FASTMCP_HOST", "0.0.0.0")


mcp = FastMCP(APP_NAME)

@mcp.tool
def sentiment_analysis(text: str) -> str:
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The text to analyze

    Returns:
        str: A JSON string containing text_classification.label text_classification.score and key phrases
    """
    result = analyze_text(text)
    # blob = TextBlob(text)
    # sentiment = blob.sentiment
    
    # result = {
    #     "polarity": round(sentiment.polarity, 2),  # -1 (negative) to 1 (positive)
    #     "subjectivity": round(sentiment.subjectivity, 2),  # 0 (objective) to 1 (subjective)
    #     "assessment": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
    # }

    return json.dumps(result)

@mcp.tool
def document_classification(file_path: str) -> str:
    """
    Classify the given document.

    Args:
        file_path (str): The path to the document file to classify

    Returns:
        str: A JSON string containing document classifications with types and confidences
    """
    result = classify_document(file_path)
    return json.dumps(result)

@mcp.tool
def upload_sentiment_to_nosql(text_content: str, sentiment_result: str, user_id: str = None, session_id: str = None) -> str:
    """
    Upload sentiment analysis result to OCI NoSQL table.

    Args:
        text_content (str): The original text that was analyzed
        sentiment_result (str): The sentiment analysis result as JSON string
        user_id (str, optional): User identifier for tracking
        session_id (str, optional): Session identifier for grouping

    Returns:
        str: A JSON string containing upload result with success status and record ID
    """
    try:
        # Parse the sentiment result if it's a JSON string
        if isinstance(sentiment_result, str):
            sentiment_data = json.loads(sentiment_result)
        else:
            sentiment_data = sentiment_result
        
        # Upload to NoSQL table using the client
        result = upload_sentiment_result(
            text_content=text_content,
            sentiment_result=sentiment_data,
            user_id=user_id,
            session_id=session_id
        )
        
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to upload sentiment result to NoSQL"
        }
        return json.dumps(error_result)

@mcp.tool
def query_sentiment_results(user_id: str = None, session_id: str = None, limit: int = 100) -> str:
    """
    Query sentiment analysis results from OCI NoSQL table.

    Args:
        user_id (str, optional): Filter results by user ID
        session_id (str, optional): Filter results by session ID
        limit (int): Maximum number of results to return (default: 100)

    Returns:
        str: A JSON string containing query results with sentiment analysis data
    """
    try:
        # Query results using the client
        result = query_sentiment_results(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
        
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to query sentiment results from NoSQL"
        }
        return json.dumps(error_result)

@mcp.tool
def analyze_and_store_sentiment(text: str, user_id: str = None, session_id: str = None) -> str:
    """
    Analyze text sentiment and automatically store the result in NoSQL table.

    Args:
        text (str): The text to analyze
        user_id (str, optional): User identifier for tracking
        session_id (str, optional): Session identifier for grouping

    Returns:
        str: A JSON string containing both sentiment analysis and storage result
    """
    try:
        # First, analyze the sentiment
        sentiment_result = analyze_text(text)
        
        # Then, upload to NoSQL using the client
        upload_result = upload_sentiment_result(
            text_content=text,
            sentiment_result=sentiment_result,
            user_id=user_id,
            session_id=session_id
        )
        
        # Combine both results
        combined_result = {
            "sentiment_analysis": sentiment_result,
            "storage_result": upload_result,
            "timestamp": upload_result.get("timestamp") if upload_result.get("success") else None
        }
        
        return json.dumps(combined_result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze and store sentiment"
        }
        return json.dumps(error_result)


def get_weather(text: str) -> str:
    """
    Get the current weather of the given city.

    Args:
        text (str): The name of the city

    Returns:
        str: The city and weather
    """
    result = {"weather": "sunny",
              "city": text}
    return json.dumps(result)


# Health endpoint for k8s probes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
    # Expose Streamable HTTP transport so clients can connect over the network.
    # MCP endpoint will be available at http://<host>:<port>/mcp/
    mcp.run(transport="http", host=HOST, port=PORT)