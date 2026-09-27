import os
from openai import OpenAI

SYSTEM_PROMPT = """You are NexaRAG, a document-grounded AI assistant.
Answer the user's question using the supplied context.
If the answer is not supported by the context, say that it was not found
in the uploaded documents. Do not invent facts."""

def generate_answer(question, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n\n{context}\n\nQuestion:\n{question}\n\nAnswer only from the supplied context.",
            },
        ],
    )
    return response.choices[0].message.content
