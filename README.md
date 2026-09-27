# 🧠 NexaRAG — Hackathon RAG Platform

NexaRAG is a reusable Retrieval-Augmented Generation platform for building domain-specific GenAI applications during a hackathon.

## Features

- PDF, DOCX and TXT ingestion
- Text extraction and chunking
- Local semantic embeddings
- Chroma vector database
- Similarity retrieval with relevance scores
- Gemini LLM generation
- Conversational document chat
- Source and page traceability
- Document summarization
- Question and answer generation
- Key insight extraction
- Multi-document comparison
- Streamlit deployment
- Retry and model fallback handling

## Architecture

Documents → Text Extraction → Chunking → Embeddings → Chroma → Query Embedding → Top-K Retrieval → Grounded Context → Gemini → Answer + Sources

## Tech stack

- Python
- Streamlit
- Gemini API
- ChromaDB
- Sentence Transformers
- PyPDF
- python-docx

## Setup

Clone the repository, create a virtual environment, install requirements, create a .env file from .env.example, add GEMINI_API_KEY, and run `streamlit run app.py`.

For Streamlit Cloud, add these secrets:

GEMINI_API_KEY = "your_key"
GEMINI_MODEL = "gemini-3.8-flash"

Never commit the API key to GitHub.

## How the RAG works

1. Uploaded files are converted into text.
2. Text is split into overlapping chunks.
3. The embedding model converts chunks into vectors.
4. Chroma stores and searches those vectors.
5. A user question is converted into a vector.
6. The most relevant chunks are retrieved.
7. Retrieved context is sent to Gemini.
8. Gemini generates an answer grounded in that context.
9. Source names and pages are shown to the user.

## Hackathon modes

### Chat with Documents
Ask natural-language questions with conversation history.

### Summarize Documents
Generate an executive-style summary.

### Generate Questions
Create study, interview or evaluation questions from uploaded material.

### Extract Key Insights
Identify facts, risks, opportunities, requirements and open questions.

### Compare Documents
Compare multiple uploaded documents and identify similarities and differences.

## How to adapt it to any hackathon

Keep the RAG core and replace the domain layer.

- Education → syllabus and notes assistant
- Healthcare → medical-document knowledge assistant
- Legal → contract and policy analyzer
- Recruitment → resume and job-description intelligence
- Finance → report and policy analyst
- Enterprise → internal knowledge assistant
- Research → paper analysis assistant
- Government → scheme and document assistant

## Judge explanation

If asked where RAG is, explain: documents are chunked and embedded, stored in Chroma, and semantically retrieved for each query. The retrieved chunks are injected into the Gemini prompt, which generates a grounded response.

If asked why not use only an LLM, explain: the LLM alone does not reliably have access to the user's private documents. RAG gives it relevant external context at query time and lets the system show supporting sources.

## Roadmap

- OCR for scanned documents
- Hybrid BM25 + vector retrieval
- Cross-encoder reranking
- Persistent cloud vector storage
- User authentication
- Evaluation dashboard
- Feedback-based retrieval tuning
- Multimodal document understanding
- Agentic tools and external data connectors
