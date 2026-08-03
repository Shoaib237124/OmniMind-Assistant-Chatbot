import uuid
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="OmniMind Assistant", layout="wide")

# --- Helper Functions ---
def generate_thread_id():
    return str(uuid.uuid4())

def get_all_threads():
    try:
        res = requests.get(f"{BACKEND_URL}/threads")
        if res.status_code == 200:
            return res.json().get("threads", [])
    except requests.exceptions.RequestException:
        pass
    return []

def load_conversation(thread_id):
    try:
        res = requests.get(f"{BACKEND_URL}/threads/{thread_id}/history")
        if res.status_code == 200:
            return res.json().get("messages", [])
    except requests.exceptions.RequestException:
        pass
    return []

def delete_thread_remote(thread_id):
    try:
        requests.delete(f"{BACKEND_URL}/threads/{thread_id}")
    except requests.exceptions.RequestException:
        pass

def add_thread(thread_id, title="New Chat"):
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = {}
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"][thread_id] = title

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []
    add_thread(thread_id)

# --- State Initialization ---
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = {}
    for t_id in get_all_threads():
        msgs = load_conversation(t_id)
        title = "New Chat"
        for m in msgs:
            if m["role"] == "user":
                title = m["content"][:40]
                break
        st.session_state["chat_threads"][t_id] = title

add_thread(st.session_state["thread_id"])

# --- Sidebar ---
st.sidebar.title("Conversations")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.markdown("---")

# --- RAG DOCUMENT UPLOADER SECTION ---
st.sidebar.subheader("📄 Document RAG Upload")
uploaded_file = st.sidebar.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
if uploaded_file is not None:
    if st.sidebar.button("Index Document"):
        with st.sidebar.status("Indexing file..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                res = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
                if res.status_code == 200:
                    st.sidebar.success(f"Indexed {uploaded_file.name} successfully!")
                else:
                    st.sidebar.error("Failed to index file.")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")

for thread_id, title in list(st.session_state["chat_threads"].items())[::-1]:
    col1, col2 = st.sidebar.columns([5, 1])

    with col1:
        if st.button(title, key=f"chat_{thread_id}", use_container_width=True):
            st.session_state["thread_id"] = thread_id
            st.session_state["message_history"] = load_conversation(thread_id)
            st.rerun()

    with col2:
        if st.button("🗑️", key=f"delete_{thread_id}", use_container_width=True):
            delete_thread_remote(thread_id)
            del st.session_state["chat_threads"][thread_id]
            if st.session_state["thread_id"] == thread_id:
                reset_chat()
            st.rerun()

# --- Main UI ---
st.title("AI Assistant")

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here...")

if user_input:
    current_thread = st.session_state["thread_id"]

    if st.session_state["chat_threads"][current_thread] == "New Chat":
        title = user_input.strip()
        st.session_state["chat_threads"][current_thread] = title[:40] + "..." if len(title) > 40 else title

    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and executing tools..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"thread_id": current_thread, "message": user_input},
                    timeout=120
                )
                if response.status_code == 200:
                    ai_message = response.json().get("response", "")
                else:
                    ai_message = f"Error: Server returned status code {response.status_code}"
            except Exception as e:
                ai_message = f"Connection error: {e}"

            st.markdown(ai_message)

    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})