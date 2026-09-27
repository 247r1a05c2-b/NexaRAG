import os
import streamlit as st
from dotenv import load_dotenv
from src.document_loader import load_uploaded_file
from src.rag_pipeline import answer_question, build_index, clear_index, run_document_task, stats

load_dotenv()
st.set_page_config(page_title="NexaRAG", page_icon="🧠", layout="wide")

def get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed" not in st.session_state:
    st.session_state.indexed = False

st.title("🧠 NexaRAG")
st.caption("Hackathon-ready RAG workspace for documents, research and knowledge assistants.")

with st.sidebar:
    st.header("📚 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if st.button("🚀 Process Documents", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Upload at least one document.")
        else:
            with st.spinner("Extracting, chunking, embedding and indexing..."):
                documents = []
                for file in uploaded_files:
                    documents.extend(load_uploaded_file(file))
                count = build_index(documents)
            st.session_state.indexed = True
            st.session_state.messages = []
            st.success(f"Indexed {count} chunks from {len(uploaded_files)} file(s).")

    if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
        clear_index()
        st.session_state.indexed = False
        st.session_state.messages = []
        st.success("Knowledge base cleared.")

    st.divider()
    st.header("🧰 AI Tools")
    mode = st.selectbox("Choose a mode", [
        "Chat with Documents",
        "Summarize Documents",
        "Generate Questions",
        "Extract Key Insights",
        "Compare Documents",
    ])

    if get_setting("GEMINI_API_KEY"):
        st.success("Gemini API connected")
    else:
        st.warning("Add GEMINI_API_KEY to Streamlit Secrets.")

    if st.session_state.indexed:
        st.metric("Indexed chunks", stats()["chunks"])

if mode == "Chat with Documents":
    st.markdown("### 💬 Chat with Documents")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your documents...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating..."):
                try:
                    history = st.session_state.messages[:-1]
                    answer, sources, results = answer_question(question, history)
                    st.markdown(answer)
                    with st.expander("📖 Sources & Retrieval"):
                        for item in results:
                            st.write(f"{item['source']} — page {item['page']} — semantic {item['score']} — hybrid {item.get('hybrid_score', item['score'])}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.caption(f"Retrieval coverage: {retrieval["coverage"]}")
                except Exception as exc:
                    st.error(str(exc))
else:
    task_map = {
        "Summarize Documents": "Create an executive summary. Include main topics, important facts, conclusions and actionable points.",
        "Generate Questions": "Generate 10 useful questions and answers from the documents. Mix easy, medium and challenging questions.",
        "Extract Key Insights": "Extract important insights, facts, risks, opportunities, requirements and unanswered questions.",
        "Compare Documents": "Compare the available documents. Identify similarities, differences, conflicting information and unique points.",
    }
    st.info(task_map[mode])
    if st.button(f"Run {mode}", type="primary"):
        if not st.session_state.indexed:
            st.error("Process documents first.")
        else:
            with st.spinner("Analyzing your knowledge base..."):
                try:
                    result, sources = run_document_task(task_map[mode])
                    st.markdown(result)
                    with st.expander("📖 Sources"):
                        for source in sources:
                            st.write(source)
                except Exception as exc:
                    st.error(str(exc))

st.divider()
st.caption("NexaRAG • Retrieval-Augmented Generation • Gemini • Chroma • Sentence Transformers")
