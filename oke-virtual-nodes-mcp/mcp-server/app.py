import os
from fastmcp import FastMCP
from tools.text_analysis import analyze_text
from tools.classify_document import classify_document
from tools.nosql_client import get_customer_by_email, get_customer_id_by_email, seed_customer_info_table, seed_order_info_table, get_open_orders
import json
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from tools.notification_client import issue_refund_for_order

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

@mcp.tool
def get_customer_info(email: str) -> str:
    """
    Get customer information based on email.

    Args:
        email (str): The customer's email

    Returns:
        str: JSON string of customer details
    """
    result = get_customer_by_email(email)
    return json.dumps(result)

@mcp.tool
def get_customer_id(email: str) -> str:
    """
    Get customer ID based on email.

    Args:
        email (str): The customer's email

    Returns:
        str: JSON string with customer ID
    """
    result = get_customer_id_by_email(email)
    return json.dumps(result)

@mcp.tool
def get_open_orders_by_customer_id(customerId: str) -> str:
    """
    Get all the open orders for the customerId.

    Args:
        customerId (str): The customerId from the customer_info table. 

    Returns:
        str: JSON string with All open orders
    """
    result = get_open_orders(customerId)
    return json.dumps(result)

@mcp.tool
def initiate_refund_for_order_id(orderId: str) -> str:
    """
    Cancels the order and initiates a refund process for the given order ID.

    Args:
        order_id (str): Unique identifier for the order to be cancelled and refunded.

    Returns:
        str: A JSON string containing:
            - status (str): "success" or "failure"
            - order_id (str): The order ID processed
            - message (str): Description of the result

    Example:
        response = initiate_refund_for_order_id("ORD12345")
        # response: '{"status": "success", "order_id": "ORD12345", "message": "Refund initiated successfully."}'
    """
    result = issue_refund_for_order(orderId)
    return json.dumps(result)

# Health endpoint for k8s probes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
       
    seed_customer_info_table()
    seed_order_info_table()
    # Expose Streamable HTTP transport so clients can connect over the network.
    # MCP endpoint will be available at http://<host>:<port>/mcp/
    mcp.run(transport="http", host=HOST, port=PORT)