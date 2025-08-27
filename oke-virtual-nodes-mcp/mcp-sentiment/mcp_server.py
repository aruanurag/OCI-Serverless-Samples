import os
from fastmcp import FastMCP
from text_analysis import analyze_text
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