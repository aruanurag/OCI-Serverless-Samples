# agent_client.py

import gradio as gr
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

# Initialize LLM
llm = ChatOCIGenAI(
    model_id="<Your model OCID>",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="<Your compartment OCID>",
    model_kwargs={"temperature": 0.7, "max_tokens": 500},
    auth_type="API_KEY",
    auth_profile="DEFAULT",
    provider="cohere"
)

# Initialize client
client = MultiServerMCPClient(
    {
        "tools_server": {
            "transport": "streamable_http",
            "url": "<Your IP>:80/mcp/",
        },
    }
)

async def get_agent_response(message, history):
    """Process user message and return agent response"""
    try:
        tools = await client.get_tools()
        agent = create_react_agent(llm, tools)
        response = await agent.ainvoke({"messages": message})
        return response['messages'][-1].content if isinstance(response['messages'], list) else str(response)
    except Exception as e:
        return f"Error processing request: {str(e)}"

async def chat_interface(message, history):
    """Gradio async chat interface function"""
    response = await get_agent_response(message, history)
    return response

def main():
    """Create and launch Gradio UI"""
    interface = gr.ChatInterface(
        fn=chat_interface,
        title="AI Chat Agent",
        description="Interact with the AI agent powered by OCI Generative AI",
        theme="default",
        examples=[
            "Analyze the sentiment of this text: 'What's in a name? That which we call a rose by any other word would smell as sweet.'",
            "What's the weather like today?",
            "Tell me a joke"
        ],
        cache_examples=False
    )
    interface.launch()

if __name__ == "__main__":
    main()