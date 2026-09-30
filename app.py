import os
import streamlit as st
from dotenv import load_dotenv
from src.document_loader import load_uploaded_file
from src.rag_pipeline import answer_question, build_index, clear_index, delete_document, list_documents, run_document_task, stats, scan_knowledge_health, heal_knowledge_health
from src.evaluation import answer_quality_label

load_dotenv()
st.set_page_config(page_title="NexaRAG", page_icon="🧠", layout="wide")


def get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None


if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed" not in st.session_state:
    st.session_state.indexed = stats()["chunks"] > 0
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "health_report" not in st.session_state:
    st.session_state.health_report = None

st.title("🧠 NexaRAG")
st.caption("Self-healing RAG knowledge platform for hackathons, research and domain assistants.")

with st.sidebar:
    st.header("📚 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, PPTX or TXT",
        type=["pdf", "docx", "pptx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if st.button("🚀 Add to Knowledge Base", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Upload at least one document.")
        else:
            try:
                with st.spinner("Extracting, OCR-ing, chunking, embedding and indexing..."):
                    documents = []
                    for file in uploaded_files:
                        documents.extend(load_uploaded_file(file))
                    count = build_index(documents)
                st.session_state.indexed = stats()["chunks"] > 0
                st.session_state.messages = []
                st.session_state.health_report = None
                st.success(f"Added {count} new chunks. Existing knowledge was preserved.")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    st.header("🩺 Self-Healing Knowledge")
    st.caption("The Knowledge Integrity Agent checks for contradictions, duplicates and weak evidence before retrieval is affected.")

    if st.button("🔍 Scan Knowledge Health", use_container_width=True):
        if not st.session_state.indexed:
            st.error("Add documents first.")
        else:
            with st.spinner("Knowledge Integrity Agent is checking the knowledge base..."):
                try:
                    st.session_state.health_report = scan_knowledge_health(limit=60)
                except Exception as exc:
                    st.error(str(exc))

    report = st.session_state.health_report
    if report:
        score = report.get("health_score", 0)
        status = report.get("status", "unknown")
        st.metric("Knowledge Health", f"{score}/100")
        if status == "healthy":
            st.success(f"Healthy • {report.get('checked_chunks', 0)} chunks checked")
        else:
            st.warning(f"Repair recommended • {len(report.get('issues', []))} integrity issue(s)")

        if report.get("issues"):
            for number, issue in enumerate(report["issues"], 1):
                with st.expander(f"Issue {number}: {issue.get('type', 'integrity').replace('_', ' ').title()}"):
                    st.write(issue.get("reason", "No explanation provided."))
                    st.caption(f"Confidence: {issue.get('confidence', 0):.0%}")
                    st.caption(f"Repair action: {issue.get('repair', 'review')}")

            if st.button("🛠️ Heal Knowledge Base", type="primary", use_container_width=True):
                with st.spinner("Applying safe repairs and quarantining superseded evidence..."):
                    try:
                        result = heal_knowledge_health(report)
                        st.session_state.health_report = scan_knowledge_health(limit=60)
                        if result["repaired_count"]:
                            st.success(f"Healed {result['repaired_count']} chunk(s). Superseded evidence is preserved in quarantine and removed from normal retrieval.")
                        else:
                            st.info("No automatic repair was safe enough to apply. Issues remain available for review.")
                    except Exception as exc:
                        st.error(str(exc))

    st.divider()
    st.header("🗂️ Documents")
    docs = list_documents()
    if docs:
        for doc in docs:
            quarantine_note = f" • {doc['quarantined']} quarantined" if doc.get("quarantined") else ""
            st.write(f"**{doc['source']}**")
            st.caption(f"{doc['chunks']} chunks • {doc['pages']} pages • {doc['methods']}{quarantine_note}")
            if st.button("Remove", key=f"remove_{doc['source']}"):
                delete_document(doc["source"])
                st.session_state.indexed = stats()["chunks"] > 0
                st.session_state.messages = []
                st.session_state.health_report = None
                st.rerun()
    else:
        st.caption("No documents indexed yet.")

    if st.button("🗑️ Clear Entire Knowledge Base", use_container_width=True):
        clear_index()
        st.session_state.indexed = False
        st.session_state.messages = []
        st.session_state.health_report = None
        st.rerun()

    st.divider()
    st.header("🎯 Domain")
    domain = st.selectbox("Choose a hackathon mode", [
        "Universal",
        "Education",
        "Healthcare",
        "Legal",
        "Recruitment",
        "Finance",
        "Enterprise",
        "Research",
    ])

    st.header("🧰 AI Tools")
    mode = st.selectbox("Choose a mode", [
        "Chat with Documents",
        "Summarize Documents",
        "Generate Questions",
        "Extract Key Insights",
        "Compare Documents",
    ])

    if get_setting("GEMINI_API_KEY"):
        st.success("Gemini API connected")
    else:
        st.warning("Add GEMINI_API_KEY to Streamlit Secrets.")

    metrics = stats()
    st.metric("Documents", metrics["documents"])
    st.metric("Active chunks", metrics["chunks"])
    st.metric("Quarantined chunks", metrics.get("quarantined", 0))
    st.metric("Session feedback", len(st.session_state.feedback))


domain_prompts = {
    "Universal": "Answer using the supplied documents.",
    "Education": "Act as an academic assistant. Emphasize definitions, concepts, requirements, exam-relevant points and practice questions.",
    "Healthcare": "Act as a document-grounded healthcare information assistant. Do not diagnose. Clearly distinguish document facts from general guidance.",
    "Legal": "Act as a document-grounded legal information assistant. Explain clauses and obligations from the documents and avoid unsupported legal conclusions.",
    "Recruitment": "Act as a recruitment knowledge assistant. Extract skills, requirements, qualifications and evidence from the supplied documents.",
    "Finance": "Act as a document-grounded financial information assistant. Preserve figures, dates, assumptions and caveats exactly as supported by the documents.",
    "Enterprise": "Act as an enterprise knowledge assistant. Prioritize policies, procedures, owners, requirements, risks and action items.",
    "Research": "Act as a research assistant. Distinguish findings, methodology, limitations, evidence and open questions.",
}

if mode == "Chat with Documents":
    st.markdown(f"### 💬 {domain} Knowledge Assistant")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your knowledge base...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving, reranking and generating..."):
                try:
                    history = st.session_state.messages[:-1]
                    enriched_question = f"{domain_prompts[domain]}\n\nUser question: {question}"
                    answer, sources, results, retrieval = answer_question(enriched_question, history)
                    st.markdown(answer)
                    st.caption(f"{answer_quality_label(retrieval)} • Coverage: {retrieval['coverage']}")
                    with st.expander("📖 Sources & Retrieval"):
                        for item in results:
                            st.write(f"{item['source']} — page {item['page']} — semantic {item['score']} — lexical {item.get('lexical_score', 0)} — hybrid {item.get('hybrid_score', item['score'])}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("👍 Helpful", key=f"helpful_{len(st.session_state.messages)}"):
                            st.session_state.feedback.append({"question": question, "rating": "helpful"})
                            st.success("Feedback recorded for this session.")
                    with c2:
                        if st.button("👎 Needs improvement", key=f"improve_{len(st.session_state.messages)}"):
                            st.session_state.feedback.append({"question": question, "rating": "needs_improvement"})
                            st.info("Feedback recorded for this session.")
                except Exception as exc:
                    st.error(str(exc))
else:
    task_map = {
        "Summarize Documents": "Create an executive summary. Include main topics, important facts, conclusions and actionable points.",
        "Generate Questions": "Generate 10 useful questions and answers from the documents. Mix easy, medium and challenging questions.",
        "Extract Key Insights": "Extract important insights, facts, risks, opportunities, requirements and unanswered questions.",
        "Compare Documents": "Compare the available documents. Identify similarities, differences, conflicting information and unique points.",
    }
    st.info(task_map[mode])
    if st.button(f"Run {mode}", type="primary"):
        if not st.session_state.indexed:
            st.error("Add documents first.")
        else:
            with st.spinner("Analyzing the knowledge base..."):
                try:
                    result, sources = run_document_task(task_map[mode])
                    st.markdown(result)
                    with st.expander("📖 Sources"):
                        for source in sources:
                            st.write(source)
                except Exception as exc:
                    st.error(str(exc))

st.divider()
st.caption("NexaRAG • Self-Healing Knowledge • RAG • Hybrid Retrieval • Gemini • Chroma • Sentence Transformers • OCR")
