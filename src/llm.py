import os
import time
import streamlit as st
from google import genai

SYSTEM_PROMPT = """You are NexaRAG, a grounded knowledge assistant.
Use only the supplied retrieved context for document-grounded claims.
Never invent facts, citations, names, numbers, dates, policies, or sources.
If the retrieved context is insufficient, explicitly say that the documents do not provide enough information.
Distinguish facts found in the documents from reasonable suggestions.
Cite supporting sources in the form [Source: filename, page N] when page information is available.
Be concise, structured, and useful."""


def get_setting(name, default=None):
    value = os.getenv(name)
    if value:
        return value
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return default

def generate_text(prompt):
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from Streamlit Secrets.")

    client = genai.Client(api_key=api_key)
    primary = get_setting("GEMINI_MODEL", "gemini-3.8-flash")
    models = list(dict.fromkeys([primary, "gemini-2.5-flash-lite", "gemini-3.8-flash"]))
    last_error = None

    for model in models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                if not response.text:
                    raise RuntimeError("Gemini returned an empty response.")
                return response.text
            except Exception as exc:
                last_error = exc
                message = str(exc).upper()
                if "503" not in message and "UNAVAILABLE" not in message and "429" not in message:
                    raise
                time.sleep(2 + attempt * 2)

    raise RuntimeError(f"Gemini is temporarily unavailable. Please try again. Details: {last_error}")

def generate_answer(question, context, history=None):
    history_text = ""
    if history:
        history_text = "\n\nConversation so far:\n" + "\n".join(
            f"{item['role']}: {item['content']}" for item in history[-6:]
        )
    prompt = f"""{SYSTEM_PROMPT}

Task: Answer the user's question from the retrieved context.

Retrieved context:
{context}
{history_text}

User question:
{question}

Return a direct answer and mention the relevant source names when useful."""
    return generate_text(prompt)

def run_task(task, context):
    prompt = f"""{SYSTEM_PROMPT}

Perform this task using the supplied document context.

Task:
{task}

Document context:
{context}

Use headings and bullet points where useful. Do not add information that is not supported by the context."""
    return generate_text(prompt)
