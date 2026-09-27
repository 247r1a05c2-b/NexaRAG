# 🧠 NexaRAG — Hackathon-Ready Adaptive RAG Platform

NexaRAG is a reusable Retrieval-Augmented Generation platform for turning uploaded knowledge into grounded AI assistants. The same core can be adapted to education, healthcare, legal, recruitment, finance, enterprise and research hackathon problems.

## What it can do
- PDF, scanned PDF, DOCX, PPTX and TXT ingestion
- OCR fallback for scanned PDF pages
- Table extraction from DOCX/PPTX
- Overlapping document chunking
- Local sentence-transformer embeddings
- Chroma vector database
- Incremental indexing that preserves existing knowledge
- Duplicate chunk protection
- Hybrid semantic + lexical + rank retrieval
- Source diversity during retrieval
- Gemini grounded generation
- Conversational document chat
- Source and page traceability
- Retrieval coverage indicator
- Summarization, question generation, key insights and multi-document comparison
- Document list and individual document removal
- Domain modes for different hackathon themes
- Session-level user feedback
- Streamlit deployment

## Architecture
Documents → Text/PDF/OCR Extraction → Chunking → Embeddings → Chroma → Hybrid Retrieval → Grounded Context → Gemini → Answer + Sources + Retrieval Metrics

## Supported domains
- Education → syllabus, notes and regulation assistant
- Healthcare → document-grounded medical information assistant
- Legal → contract and policy assistant
- Recruitment → resume and job-description intelligence
- Finance → report and policy analyst
- Enterprise → internal knowledge assistant
- Research → paper analysis assistant
- Universal → general knowledge workspace

## Tech stack
- Python
- Streamlit
- Gemini API
- ChromaDB
- Sentence Transformers
- PyPDF
- PyMuPDF
- Tesseract OCR
- python-docx
- python-pptx

## Setup
Install the Python requirements and run the Streamlit app with `streamlit run app.py`.

For Streamlit Cloud, add these secrets:

```toml
GEMINI_API_KEY = "your_key"
GEMINI_MODEL = "gemini-3.8-flash"
```

Never commit the API key to GitHub.

## RAG flow
1. Upload a document.
2. Extract text; use OCR when a PDF page has no extractable text.
3. Split text into overlapping chunks.
4. Convert chunks into embeddings.
5. Store chunks and metadata in Chroma.
6. Convert the user query into an embedding.
7. Retrieve candidate chunks.
8. Combine semantic similarity, lexical overlap and retrieval rank.
9. Prefer diverse document sources.
10. Send the strongest context to Gemini.
11. Generate a grounded answer.
12. Show source, page and retrieval-quality information.

## Important persistence note
The Chroma database is stored in the app's local filesystem. Incremental indexing works while that app instance retains its data, but Streamlit Cloud local storage should not be treated as permanent cloud persistence across rebuilds or infrastructure replacement.

For production, connect Chroma or another vector database to managed cloud storage and persist uploaded documents there.

## Hackathon demo
1. Upload two documents from a chosen domain.
2. Ask a cross-document question.
3. Show retrieved sources and pages.
4. Add a third document without deleting the first two.
5. Ask a new question using the newly added knowledge.
6. Switch domain mode.
7. Run summary or question generation.
8. Show retrieval coverage and user feedback.

## Judge explanation
RAG is the path from uploaded documents through chunking, embeddings, Chroma retrieval, hybrid ranking, grounded context and Gemini generation.

The LLM alone does not automatically know the user's private uploaded documents. RAG supplies relevant external context at query time and gives the system traceable sources.

The same retrieval engine can be reused across hackathon domains; the domain mode changes prompts, tasks, UI language and expected document types.

## Future production upgrades
- Managed cloud vector database
- Persistent object storage
- Authentication and multi-user workspaces
- Cross-encoder reranking
- Multimodal image/table understanding
- Long-term feedback analytics
- Automated evaluation datasets
- Agentic tools and external connectors
- Role-based access control