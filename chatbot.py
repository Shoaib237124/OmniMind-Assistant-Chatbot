import os
import shutil
import sqlite3
import uvicorn
import aiosqlite
from contextlib import asynccontextmanager
from typing import Annotated, TypedDict, List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool

# Vector DB & Document Loaders for RAG
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

from tools.web_search import web_search
from tools.weather import get_weather
from tools.stock import get_stock_price
from mcp_client import MCPManager

load_dotenv()

# --- 1. Vector Store Setup (RAG) ---
CHROMA_PATH = "chroma_db"
embeddings = FastEmbedEmbeddings()
vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

from typing import Optional

@tool
def retrieve_uploaded_documents(query: str, filename: Optional[str] = None) -> str:
    """Useful for answering questions based on user uploaded documents or PDFs.
    
    Args:
        query: The search term or question about the document context.
        filename: Optional exact filename to restrict search to a specific document.
    """
    # Build ChromaDB metadata filter if a specific filename is requested
    search_kwargs = {}
    if filename:
        search_kwargs["filter"] = {"source": filename}
        
    results = vectorstore.similarity_search(query, k=4, **search_kwargs)
    
    if not results:
        return f"No relevant context found in uploaded documents{' for file: ' + filename if filename else ''}."
    
    context = "\n\n".join([
        f"--- Chunk (Source: {doc.metadata.get('source', 'Unknown')}) ---\n{doc.page_content}" 
        for doc in results
    ])
    return f"Retrieved Document Context:\n{context}"

# --- Graph Definition ---
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = """
You are a versatile, intelligent AI assistant equipped with GitHub MCP tools, RAG document search, and general tools (web search, weather, stock prices).
1. For general conversation or coding help, answer directly.
2. For real-time data, uploaded documents, or GitHub operations, use the appropriate tools.
3. When answering questions about uploaded files, rely strictly on context from the `retrieve_uploaded_documents` tool.
"""

# Global storage for compiled graph and connection
graph_app = None
db_conn = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph_app, db_conn
    print("🚀 Initializing MCP Tools and Database Connection...")
    
    mcp_tools = await MCPManager.get_tools()
    all_tools = [web_search, get_weather, get_stock_price, retrieve_uploaded_documents] + mcp_tools

    # Recommended model endpoint: llama-3.3-70b-versatile or llama-3.1-8b-instant to avoid TPM limits
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    llm_with_tools = llm.bind_tools(all_tools, tool_choice="auto")

    async def chat_node(state: ChatState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    builder = StateGraph(ChatState)
    builder.add_node("chat_node", chat_node)
    builder.add_node("tools", ToolNode(all_tools, handle_tool_errors=True))

    builder.add_edge(START, "chat_node")
    builder.add_conditional_edges("chat_node", tools_condition)
    builder.add_edge("tools", "chat_node")

    # Persistent Async SQLite Saver
    db_conn = await aiosqlite.connect("chatbot.db")
    checkpointer = AsyncSqliteSaver(db_conn)
    await checkpointer.setup()

    graph_app = builder.compile(checkpointer=checkpointer)
    print("✅ LangGraph Server Initialized Successfully.")
    yield
    
    print("🧹 Closing Database Connections...")
    await db_conn.close()

app = FastAPI(title="LangGraph Chatbot Server", lifespan=lifespan)

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

# --- Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not graph_app:
        raise HTTPException(status_code=500, detail="Graph engine not initialized")

    config = {"configurable": {"thread_id": req.thread_id}}
    
    state_result = await graph_app.ainvoke(
        {"messages": [HumanMessage(content=req.message)]},
        config=config
    )
    
    messages = state_result.get("messages", [])
    ai_response = ""
    if messages and isinstance(messages[-1], AIMessage):
        ai_response = messages[-1].content

    return ChatResponse(response=ai_response)

# --- NEW RAG UPLOAD ENDPOINT ---
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        if file.filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(temp_file_path)
        else:
            loader = TextLoader(temp_file_path)
            
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        splits = text_splitter.split_documents(docs)
        
        # Attach source metadata to each split chunk
        for split in splits:
            split.metadata["source"] = file.filename
        
        vectorstore.add_documents(splits)
        return {"filename": file.filename, "status": "Indexed", "chunks": len(splits)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/threads/{thread_id}/history")
async def get_history(thread_id: str):
    if not graph_app:
        raise HTTPException(status_code=500, detail="Graph engine not initialized")

    config = {"configurable": {"thread_id": thread_id}}
    state = await graph_app.aget_state(config)
    messages = state.values.get("messages", [])
    
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage)) and msg.content:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})
            
    return {"messages": formatted_messages}

@app.get("/threads")
def list_threads():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    threads = []
    seen = set()
    try:
        cursor.execute("SELECT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        for row in rows:
            thread_id = row[0]
            if thread_id not in seen:
                seen.add(thread_id)
                threads.append(thread_id)
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()
    return {"threads": threads[::-1]}

@app.delete("/threads/{thread_id}")
def delete_thread_endpoint(thread_id: str):
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM writes WHERE thread_id=?", (thread_id,))
        cursor.execute("DELETE FROM checkpoints WHERE thread_id=?", (thread_id,))
        conn.commit()
    finally:
        conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run("chatbot:app", host="127.0.0.1", port=8000, reload=False)