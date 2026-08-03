import asyncio
from chatbot import init_chatbot
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

async def main():
    print("🚀 Initializing chatbot and loading tools...")
    app = await init_chatbot()
    
    config = {"configurable": {"thread_id": "test_1"}}
    
    user_prompt = "List my GitHub repositories"
    print(f"\n👤 User: {user_prompt}\n" + "-" * 40)

    response = await app.ainvoke(
        {"messages": [HumanMessage(content=user_prompt)]},
        config=config
    )

    for msg in response.get("messages", []):
        role = msg.type.upper()
        
        # Format output based on message type
        if isinstance(msg, HumanMessage):
            continue  # Skip re-printing user message
        elif isinstance(msg, ToolMessage):
            print(f"🛠️ [TOOL RESPONSE - {msg.name}]:\n{msg.content[:200]}...\n")
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tool in msg.tool_calls:
                    print(f"🤖 [AI CALLING TOOL]: {tool['name']} with args {tool['args']}")
            elif msg.content:
                print(f"🤖 [ASSISTANT]:\n{msg.content}\n")

if __name__ == "__main__":
    asyncio.run(main())