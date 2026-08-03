# 🤖 OmniMind

> **An Agentic RAG & Multi-Tool AI Assistant Built with LangGraph, FastAPI, and Streamlit**

OmniMind is a production-grade AI assistant that combines **LangGraph**, **Retrieval-Augmented Generation (RAG)**, **Model Context Protocol (MCP)**, and real-time tools into a single intelligent system. It is capable of reasoning, using tools, retrieving information from uploaded documents, interacting with GitHub repositories, and maintaining persistent conversations.

---

## ✨ Features

### 🧠 Agentic AI with LangGraph
- Stateful, cyclic agent workflows powered by **LangGraph**
- Intelligent tool selection based on user intent
- Conditional routing between tools and LLM
- Persistent conversation memory using SQLite checkpoints

### 📚 Retrieval-Augmented Generation (RAG)
- Upload PDF and text documents
- Semantic search using **ChromaDB**
- Fast vector embeddings using **FastEmbed**
- Context-aware question answering from uploaded files

### 🔗 GitHub Integration (MCP)
- GitHub repository interaction using **Model Context Protocol (MCP)**
- Search repositories
- Read files
- Browse project contents
- Query GitHub resources naturally

### 🌐 Real-Time AI Tools
- Live Web Search
- Weather Information
- Stock Market Prices
- Automatic tool invocation using LangGraph

### 💾 Persistent Memory
- SQLite checkpointing
- Resume previous conversations
- Multiple chat sessions
- Delete individual chats
- Automatic conversation history management

### 📊 Observability
- Integrated with **LangSmith**
- Execution tracing
- Agent debugging
- Workflow visualization

### ⚡ Modern Architecture
- FastAPI backend
- Streamlit frontend
- Modular project structure
- Easily extensible tool system

---

# 🏗️ System Architecture

```text
                           ┌──────────────────────────┐
                           │   Streamlit Frontend     │
                           └────────────┬─────────────┘
                                        │
                                  HTTP / REST API
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │     FastAPI Backend      │
                           └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │     LangGraph Agent      │
                           │ State • Routing • Memory │
                           └────────────┬─────────────┘
                                        │
            ┌───────────────┬───────────┼───────────────┬──────────────┐
            ▼               ▼           ▼               ▼              ▼
     ┌────────────┐  ┌───────────┐ ┌──────────┐ ┌────────────┐ ┌────────────┐
     │ Document   │  │ Web Search│ │ Weather  │ │ Stock API  │ │ GitHub MCP │
     │    RAG     │  │   Tool    │ │   Tool   │ │    Tool    │ │   Server   │
     └─────┬──────┘  └───────────┘ └──────────┘ └────────────┘ └────────────┘
           │
           ▼
   ┌─────────────────────┐
   │ ChromaDB + FastEmbed│
   └─────────────────────┘
```

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **LLM Framework** | LangChain |
| **Agent Framework** | LangGraph |
| **LLM Provider** | Groq |
| **Model** | Llama-3.3-70B-Versatile |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **Vector Database** | ChromaDB |
| **Embedding Model** | FastEmbed (BAAI/bge-small-en-v1.5) |
| **Persistence** | SQLite (aiosqlite) |
| **Observability** | LangSmith |
| **Protocols** | Model Context Protocol (MCP) |

---

# 📂 Project Features

- ✅ LangGraph Agent Workflow
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Document Upload & Chat
- ✅ Chroma Vector Database
- ✅ FastEmbed Embeddings
- ✅ GitHub MCP Integration
- ✅ Web Search Tool
- ✅ Weather Tool
- ✅ Stock Price Tool
- ✅ Persistent Chat History
- ✅ Multiple Chat Sessions
- ✅ Delete Conversations
- ✅ LangSmith Tracing
- ✅ FastAPI Backend
- ✅ Streamlit Frontend

---

# 🚀 Getting Started

## Prerequisites

Before running the project, ensure you have:

- Python 3.10+
- Groq API Key
- Tavily API Key
- Weather API Key
- GitHub Personal Access Token (for MCP)

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/OmniMind.git

cd OmniMind
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv

.\.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root.

```env
# Groq
GROQ_API_KEY=your_groq_api_key

# Tavily Search
TAVILY_API_KEY=your_tavily_api_key

# Weather API
WEATHER_API_KEY=your_weather_api_key

# GitHub MCP
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat

# LangSmith (Optional)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=OmniMind
```

---

# ▶️ Running the Application

## Start FastAPI Backend

```bash
uvicorn chatbot:app --host 127.0.0.1 --port 8000 --reload
```

---

## Start Streamlit Frontend

Open another terminal.

```bash
streamlit run app.py
```

---

Open your browser at:

```
http://localhost:8501
```

---

# 👨‍💻 Author

**Muhammad Shoaib**

Software Engineering Student

AI • Machine Learning • Generative AI • Agentic AI

---
