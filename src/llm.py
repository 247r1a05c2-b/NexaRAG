import os
from google import genai

SYSTEM_PROMPT = """You are NexaRAG, a document-grounded AI assistant.
Answer the user's question using the supplied context.
If the answer is not supported by the context, say that it was not found
in the uploaded documents. Do not invent facts."""

def generate_answer(question, context):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer only from the supplied context."""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
    )

    return response.text
