# 🧠 NexaRAG — Self-Healing Adaptive RAG Platform

NexaRAG is a reusable Retrieval-Augmented Generation platform for turning uploaded knowledge into grounded AI assistants. It now includes a **Self-Healing Knowledge Base** that continuously checks indexed evidence for contradictions, duplicates and weak evidence, then safely quarantines superseded conflicting chunks so normal retrieval stays clean while the original evidence remains preserved.

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
- **Knowledge Integrity Agent** for contradiction, duplicate and weak-evidence detection
- **Knowledge Health Score** for the indexed knowledge base
- **Safe self-healing** by quarantining superseded evidence instead of silently deleting it
- Streamlit deployment

## Self-Healing Knowledge Base

The self-healing layer adds an integrity loop around the normal RAG pipeline:

```text
Documents
   ↓
Extraction → Chunking → Embeddings → Chroma
                                      ↓
                           Knowledge Integrity Agent
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
             Healthy evidence                    Integrity issue
                    ↓                                   ↓
              Normal RAG                     Confidence + evidence check
                                                        ↓
                                             Safe repair when justified
                                                        ↓
                                  Quarantine superseded conflicting chunks
                                                        ↓
                                    Clean retrieval + preserved history
```

### Integrity checks

The Knowledge Integrity Agent checks for:
1. Direct factual contradictions between indexed chunks.
2. A newer chunk that clearly supersedes an older conflicting chunk.
3. Duplicate or near-duplicate claims that may create retrieval ambiguity.
4. Weak or incomplete evidence that should not be trusted automatically.

The agent returns structured findings with a confidence threshold. Only high-confidence findings are considered for automatic repair.

### Safe healing

NexaRAG does **not** silently delete evidence. When the agent is sufficiently confident that an older chunk has been superseded, the older chunk is marked `quarantined` with the reason and timestamp. Quarantined evidence is excluded from normal retrieval but remains available in the Chroma store for auditability and review.

This gives the hackathon demo a clear **detect → reason → repair → verify** loop.

## Architecture

```text
Upload
  ↓
PDF/DOCX/PPTX/TXT + OCR
  ↓
Chunking
  ↓
Sentence-Transformer Embeddings
  ↓
Chroma Vector Store
  ↓
Knowledge Integrity Agent
  ├── contradiction detection
  ├── duplicate detection
  ├── weak-evidence detection
  └── confidence scoring
  ↓
Safe Healing / Quarantine
  ↓
Hybrid Retrieval
  ↓
Grounded Context
  ↓
Gemini
  ↓
Answer + Sources + Retrieval Metrics
```

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
6. Run the Knowledge Integrity Agent when requested.
7. Quarantine only high-confidence superseded evidence.
8. Convert the user query into an embedding.
9. Retrieve active candidate chunks.
10. Combine semantic similarity, lexical overlap and retrieval rank.
11. Send the strongest context to Gemini.
12. Generate a grounded answer.
13. Show source, page and retrieval-quality information.

## Hackathon demo flow
1. Upload an older policy or knowledge document.
2. Upload a newer document containing an intentional correction.
3. Click **Scan Knowledge Health**.
4. Show the detected contradiction and confidence.
5. Click **Heal Knowledge Base**.
6. Show that the superseded chunk is quarantined rather than deleted.
7. Ask a question whose answer changed in the newer document.
8. Show that retrieval uses the active evidence and cites the correct source.
9. Open the document list and show the quarantined chunk count.
10. Explain the loop as **Detect → Verify → Heal → Retrieve → Learn**.

## Judge explanation
Traditional RAG can keep accumulating contradictory evidence as new documents are added. NexaRAG adds a knowledge-integrity layer that checks the indexed evidence and prevents high-confidence superseded chunks from contaminating normal retrieval.

The system is intentionally conservative: uncertain conflicts are sent to review instead of being automatically changed. This makes the healing process auditable and reduces the risk of the LLM silently rewriting the knowledge base.

## Important persistence note
The Chroma database is stored in the app's local filesystem. Incremental indexing and quarantine work while that app instance retains its data, but Streamlit Cloud local storage should not be treated as permanent cloud persistence across rebuilds or infrastructure replacement.

For production, connect Chroma or another vector database to managed cloud storage and persist uploaded documents there.

## Future production upgrades
- Managed cloud vector database
- Persistent object storage
- Scheduled background health scans
- External source verification and web connectors
- Human approval workflow for medium-confidence repairs
- Cross-encoder reranking
- Multimodal image/table understanding
- Long-term feedback analytics
- Automated evaluation datasets
- Agentic tools and external connectors
- Role-based access control
