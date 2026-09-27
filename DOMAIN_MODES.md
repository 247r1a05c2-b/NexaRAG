# NexaRAG Domain Modes

The RAG engine stays the same. For a hackathon, change the domain instructions and UI workflow.

| Domain | Input | Main workflow | Output |
|---|---|---|---|
| Education | Notes, syllabus, papers | Ask + summarize + generate questions | Answers, study plan, MCQs |
| Healthcare | Reports, guidelines | Retrieve evidence + summarize | Grounded report summary |
| Legal | Contracts, policies | Compare + extract clauses | Clause analysis |
| Recruitment | Resumes, job descriptions | Match + compare | Candidate insights |
| Finance | Reports, policies | Retrieve + compare | Decision brief |
| Enterprise | Internal documents | Knowledge chat | Cited answers |
| Research | Papers | Summarize + compare | Literature insights |
| Government | Schemes, notices | Search + explain | Citizen-friendly answers |

## Hackathon rule

Do not rebuild the RAG engine for every title.

Keep:

1. ingestion
2. chunking
3. embeddings
4. vector search
5. retrieval
6. LLM generation

Change:

1. domain prompt
2. input validation
3. output format
4. UI labels
5. domain-specific features
