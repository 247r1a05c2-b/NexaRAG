import os

import streamlit as st
from dotenv import load_dotenv

from src.document_loader import load_uploaded_file
from src.rag_pipeline import (
    answer_question,
    audit_history,
    build_index,
    clear_index,
    delete_document,
    heal_knowledge_health,
    list_documents,
    restore_knowledge_chunk,
    run_document_task,
    scan_knowledge_health,
    stats,
)
from src.evaluation import answer_quality_label

load_dotenv()
st.set_page_config(page_title="NexaRAG Self-Healing KB", page_icon="🧠", layout="wide")


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

st.title("🧠 NexaRAG — Self-Healing Knowledge Base")
st.caption("Detect → Verify → Heal → Retrieve → Audit")

with st.sidebar:
    st.header("📚 Knowledge Ingestion")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, PPTX or TXT",
        type=["pdf", "docx", "pptx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
    auto_scan = st.checkbox("Run integrity scan after ingestion", value=True)

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
                st.session_state.health_report = scan_knowledge_health() if auto_scan else None
                st.success(f"Added {count} new chunks. Existing evidence and provenance were preserved.")
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    st.header("🩺 Knowledge Integrity")
    if st.button("🔍 Scan Knowledge Health", use_container_width=True):
        if not st.session_state.indexed:
            st.error("Add documents first.")
        else:
            with st.spinner("Integrity Agent is auditing the knowledge base..."):
                try:
                    st.session_state.health_report = scan_knowledge_health()
                except Exception as exc:
                    st.error(str(exc))

    report = st.session_state.health_report
    if report:
        score = report.get("health_score", 0)
        st.metric("Knowledge Health", f"{score}/100")
        st.caption(
            f"Checked {report.get('checked_chunks', 0)} active chunks • "
            f"{report.get('auto_healable', 0)} auto-healable • "
            f"{report.get('human_review', 0)} human-review"
        )
        if report.get("status") == "healthy":
            st.success("No integrity issues detected.")
        else:
            st.warning(f"{len(report.get('issues', []))} integrity issue(s) detected.")

        review_indexes = []
        for number, issue in enumerate(report.get("issues", [])):
            label = issue.get("type", "integrity").replace("_", " ").title()
            with st.expander(f"Issue {number + 1}: {label}"):
                st.write(issue.get("reason", "No explanation provided."))
                st.caption(
                    f"Confidence: {issue.get('confidence', 0):.0%} • "
                    f"Action: {issue.get('repair', 'review')} • "
                    f"Chunks: {', '.join(issue.get('chunk_ids', []))}"
                )
                if issue.get("repair") == "review":
                    review_indexes.append(number)

        if report.get("issues"):
            if st.button("🛠️ Apply Safe Repairs", type="primary", use_container_width=True):
                with st.spinner("Applying only high-confidence repairs..."):
                    try:
                        result = heal_knowledge_health(report)
                        st.session_state.health_report = scan_knowledge_health()
                        st.success(f"Repaired {result['repaired_count']} chunk(s). Evidence was quarantined, not deleted.")
                    except Exception as exc:
                        st.error(str(exc))

        for index in review_indexes:
            issue = report["issues"][index]
            if st.button(f"Approve repair for Issue {index + 1}", key=f"approve_{index}"):
                try:
                    result = heal_knowledge_health(report, approved_issue_indexes=[index])
                    st.session_state.health_report = scan_knowledge_health()
                    st.success(f"Human-approved repair applied: {result['repaired_count']} chunk(s).")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    st.divider()
    st.header("🗂️ Documents & Lineage")
    docs = list_documents()
    for doc in docs:
        quarantine_note = f" • {doc.get('quarantined', 0)} quarantined" if doc.get("quarantined") else ""
        review_note = f" • {doc.get('review', 0)} review" if doc.get("review") else ""
        st.write(f"**{doc['source']}**")
        st.caption(f"{doc['chunks']} chunks • {doc['pages']} pages • {doc['methods']}{quarantine_note}{review_note}")
        if st.button("Remove", key=f"remove_{doc['source']}"):
            delete_document(doc["source"])
            st.session_state.indexed = stats()["chunks"] > 0
            st.session_state.messages = []
            st.session_state.health_report = None
            st.rerun()

    if st.button("🗑️ Clear Entire Knowledge Base", use_container_width=True):
        clear_index()
        st.session_state.indexed = False
        st.session_state.messages = []
        st.session_state.health_report = None
        st.rerun()

    st.divider()
    st.header("🎯 Domain")
    domain = st.selectbox("Choose a mode", ["Universal", "Education", "Healthcare", "Legal", "Recruitment", "Finance", "Enterprise", "Research"])

    st.header("🧰 AI Tools")
    mode = st.selectbox("Choose a mode", ["Chat with Documents", "Summarize Documents", "Generate Questions", "Extract Key Insights", "Compare Documents"])

    if get_setting("GEMINI_API_KEY"):
        st.success("Gemini API connected")
    else:
        st.warning("Add GEMINI_API_KEY to Streamlit Secrets.")

    metrics = stats()
    st.metric("Active chunks", metrics["chunks"])
    st.metric("Quarantined", metrics.get("quarantined", 0))
    st.metric("Human review", metrics.get("review", 0))
    st.metric("Total stored", metrics.get("total_chunks", 0))

    with st.expander("🧾 Audit History"):
        for event in audit_history(20):
            st.caption(f"{event['timestamp']} • {event['event']}")
            st.code(event["details"], language="text")


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

    question = st.chat_input("Ask a question about your self-healing knowledge base...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving active evidence and generating..."):
                try:
                    history = st.session_state.messages[:-1]
                    enriched_question = f"{domain_prompts[domain]}\n\nUser question: {question}"
                    answer, sources, results, retrieval = answer_question(enriched_question, history)
                    st.markdown(answer)
                    st.caption(f"{answer_quality_label(retrieval)} • Coverage: {retrieval['coverage']}")
                    with st.expander("📖 Sources, provenance & retrieval"):
                        for item in results:
                            st.write(
                                f"{item['source']} — page {item['page']} — version {item.get('version', '1')} — "
                                f"semantic {item['score']} — hybrid {item.get('hybrid_score', item['score'])}"
                            )
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("👍 Helpful", key=f"helpful_{len(st.session_state.messages)}"):
                            st.session_state.feedback.append({"question": question, "rating": "helpful"})
                    with c2:
                        if st.button("👎 Needs improvement", key=f"improve_{len(st.session_state.messages)}"):
                            st.session_state.feedback.append({"question": question, "rating": "needs_improvement"})
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
            with st.spinner("Analyzing active knowledge..."):
                try:
                    result, sources = run_document_task(task_map[mode])
                    st.markdown(result)
                    with st.expander("📖 Sources"):
                        for source in sources:
                            st.write(source)
                except Exception as exc:
                    st.error(str(exc))

st.divider()
st.caption("NexaRAG • Self-Healing Knowledge • Provenance • Human-in-the-loop • Auditability • RAG • Hybrid Retrieval • Gemini • Chroma • OCR")
