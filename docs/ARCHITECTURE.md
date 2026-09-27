# NexaRAG Architecture

## End-to-end flow

User
→ Streamlit UI
→ File ingestion
→ Text extraction
→ Chunking
→ Sentence Transformer embeddings
→ Chroma vector database
→ Semantic retrieval
→ Hybrid scoring
→ Context assembly
→ Gemini
→ Grounded response
→ Source display

## Component responsibilities

- app.py: UI and user workflow
- document_loader.py: PDF/DOCX/TXT extraction
- chunking.py: overlapping text chunks
- embeddings.py: semantic vectors
- vector_store.py: persistent vector storage and retrieval
- hybrid_retrieval.py: semantic + lexical score combination
- rag_pipeline.py: orchestration
- llm.py: Gemini generation
- evaluation.py: lightweight retrieval checks

## Why this is RAG

Retrieval happens before generation. The LLM receives retrieved external context rather than answering only from its pretrained knowledge.

## Hallucination control

NexaRAG instructs the LLM to:

- use supplied context
- avoid unsupported facts
- say when evidence is missing
- expose source metadata

These controls reduce unsupported answers but do not guarantee perfect factuality.
