import os
import streamlit as st
from google import genai

SYSTEM_PROMPT = """You are NexaRAG, a document-grounded AI assistant.
Answer the user's question using the supplied context.
If the answer is not supported by the context, say that it was not found
in the uploaded documents. Do not invent facts."""

def get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None

def generate_answer(question, context):
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from Streamlit Secrets.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=get_setting("GEMINI_MODEL") or "gemini-3.8-flash",
        contents=f"""{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer only from the supplied context.""",
    )
    return response.text
