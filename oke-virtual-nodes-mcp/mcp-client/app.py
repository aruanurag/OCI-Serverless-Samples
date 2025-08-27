import gradio as gr
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import logging
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize LLM
logger.info("Initializing OCI Generative AI model")
try:
    llm = ChatOCIGenAI(
        model_id="cohere.command-latest",
        service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
        compartment_id="<compartment ocid>",
        model_kwargs={"temperature": 0.7, "max_tokens": 500},
        auth_type="API_KEY",
        auth_profile="DEFAULT",
        provider="cohere"
    )
    logger.info("LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {str(e)}")
    raise

# Initialize client
logger.info("Initializing MultiServerMCPClient")
try:
    client = MultiServerMCPClient(
        {
            "tools_server": {
                "transport": "streamable_http",
                "url": "http://0.0.0.0:8080/mcp/",
                "timeout": 30.0,
            },
        }
    )
    logger.info("Client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize client: {str(e)}")
    raise

async def get_agent_response(message, history):
    """Process user message and return agent response"""
    logger.info(f"Processing message: {message}")
    try:
        logger.debug("Fetching tools from client")
        tools = await client.get_tools()
        logger.debug(f"Retrieved {len(tools)} tools")
        
        logger.debug("Creating react agent")
        agent = create_react_agent(llm, tools)
        logger.debug("Invoking agent")
        response = await agent.ainvoke({"messages": message})
        
        logger.info("Agent response generated successfully")
        return response['messages'][-1].content if isinstance(response['messages'], list) else str(response)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"

async def chat_interface(message, history):
    """Gradio async chat interface function"""
    logger.debug(f"Chat interface received message: {message}")
    response = await get_agent_response(message, history)
    logger.debug(f"Chat interface returning response: {response}")
    return response

def main():
    """Create and launch Gradio UI"""
    logger.info("Starting Gradio UI")
    try:
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
        logger.info("Launching Gradio interface")
        interface.launch()
        logger.info("Gradio interface launched successfully")
    except Exception as e:
        logger.error(f"Failed to launch Gradio UI: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()