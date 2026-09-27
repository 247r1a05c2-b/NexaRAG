import os
import time
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
    primary = get_setting("GEMINI_MODEL") or "gemini-3.5-flash-lite"
    models = [primary, "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    models = list(dict.fromkeys(models))
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer only from the supplied context."""

    last_error = None

    for model in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:
                last_error = exc
                if "503" not in str(exc) and "UNAVAILABLE" not in str(exc):
                    raise
                time.sleep(2)

    raise RuntimeError(
        f"Gemini is temporarily unavailable. Please try again in a moment. Details: {last_error}"
    )
