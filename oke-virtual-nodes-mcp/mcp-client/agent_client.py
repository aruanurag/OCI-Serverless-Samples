#agent_client.py

# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOCIGenAI(
            model_id="<Your model OCID>",
            service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",  # Replace with your endpoint
            compartment_id="<Your compartment OCID>",
            model_kwargs={"temperature": 0.7, "max_tokens": 500},
            auth_type="API_KEY",
            auth_profile="DEFAULT",
            provider="cohere"
        )

# server_params = StdioServerParameters(
#     command="python",
#     # Make sure to update to the full absolute path to your rag_server.py file
#     args=["rag_server.py"],
# )
client = MultiServerMCPClient(
    {
        "tools_server": {
            "transport": "streamable_http",
            "url": "http://<Your MCP Server IP>:80/mcp/" #http://127.0.0.1:7860/gradio_api/mcp/",  # Replace with your MCP server URL
        },
    }
)



async def main():
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    sentiment_response = await agent.ainvoke({"messages": "Analyze the sentiment of the following text: 'What's in a name? That which we call a rose by any other word would smell as sweet.'"})
    print(sentiment_response)

if __name__ == "__main__":
    asyncio.run(main())