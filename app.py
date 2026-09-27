import os
import streamlit as st
from dotenv import load_dotenv
from src.document_loader import load_uploaded_file
from src.rag_pipeline import build_index, answer_question, clear_index

load_dotenv()
st.set_page_config(page_title="NexaRAG", page_icon="🧠", layout="wide")

st.title("🧠 NexaRAG")
st.caption("Universal AI Knowledge Assistant — ask questions about your own documents.")

if not os.getenv("OPENAI_API_KEY"):
    st.warning("Add your OPENAI_API_KEY to the .env file before asking questions.")

with st.sidebar:
    st.header("Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Process Documents", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Upload at least one document.")
        else:
            with st.spinner("Reading, chunking and indexing your documents..."):
                documents = []
                for file in uploaded_files:
                    documents.extend(load_uploaded_file(file))
                count = build_index(documents)
            st.success(f"Indexed {count} chunks.")

    if st.button("Clear Knowledge Base", use_container_width=True):
        clear_index()
        st.success("Knowledge base cleared.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(source)

question = st.chat_input("Ask something about your uploaded documents...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant information..."):
            try:
                answer, sources = answer_question(question)
                st.markdown(answer)
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.write(source)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as exc:
                error = f"Error: {exc}"
                st.error(error)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error}
                )
