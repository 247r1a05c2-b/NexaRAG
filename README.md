# 🧠 NexaRAG

NexaRAG is a beginner-friendly Retrieval-Augmented Generation (RAG) application that lets users upload documents and ask questions grounded in those documents.

## Architecture

User Question → Query Embedding → Chroma Vector Database → Relevant Document Chunks → LLM → Grounded Answer + Sources

## Features

- PDF, DOCX and TXT upload
- Text extraction
- Document chunking
- Local sentence-transformer embeddings
- Chroma vector database
- Semantic retrieval
- LLM-based grounded answers
- Source/page display
- Streamlit interface

## Run locally

```bash
git clone https://github.com/247r1a05c2-b/NexaRAG.git
cd NexaRAG
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI API key, then run:

```bash
streamlit run app.py
```

Never commit `.env`.

## What to learn

1. LLMs generate language but do not automatically know your private documents.
2. Embeddings convert text into vectors representing semantic meaning.
3. A vector database stores and retrieves those vectors.
4. RAG gives retrieved context to the LLM before generation.
5. Source metadata makes answers traceable.

## Roadmap

- Conversational memory
- Hybrid retrieval
- Reranking
- Document comparison
- Automatic summaries
- Question generation
- OCR
- RAG evaluation
- Authentication and document-level access control
