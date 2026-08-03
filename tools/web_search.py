import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import Field
from tavily import TavilyClient

load_dotenv()

# Initialize Tavily client safely
tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None


@tool
def web_search(query: str = Field(description="The search query string to look up on the web")) -> str:
    """
    Search the web for up-to-date information on recent events, news, or factual facts.
    """
    if not client:
        return "Error: TAVILY_API_KEY is not set in environment variables."

    try:
        response = client.search(
            query=query,
            max_results=2,
            search_depth='advanced',
            include_answer=True
        )
        if response.get("answer"):
            
            return response["answer"]


    except Exception as e:
        return f"Error executing web search: {str(e)}"