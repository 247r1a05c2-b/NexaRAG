# NexaRAG evaluation plan

This is an experiment protocol, not a results report. Do not add accuracy claims until the evaluation has been run and raw outputs have been retained.

## Research questions

1. Does local retrieval return the evidence needed to answer a question?
2. Does grounded generation stay within the retrieved evidence?
3. How does the current lexical token-overlap retriever compare with stronger retrieval baselines?

## Dataset design

Build a small versioned set of questions over documents that you have permission to use. For each question, record:
- The expected answer or required facts
- The supporting document and passage identifiers
- Whether the answer is unanswerable from the supplied corpus
- Any acceptable alternative answers

Keep test documents separate from development examples. Do not use private documents or API keys in a public test set.

## Baselines

- No retrieval / context-only baseline
- Current lexical token-overlap retrieval
- TF-IDF retrieval
- Embedding-based retrieval (only after implementing and pinning it)

Use the same questions and corpus for all methods.

## Metrics

- Recall@k and MRR for evidence retrieval
- Answer correctness against the reference facts
- Evidence support / faithfulness, manually reviewed on a sample
- Citation correctness for external-search answers
- Abstention quality on unanswerable questions
- Latency and provider cost where available

Separate retrieval quality from generation quality. Report test-set size, metric definitions, model/version, prompts, parameters, and failure examples.

## Current implementation note

The local retriever currently uses lexical token overlap and JSONL storage. Do not describe it as embedding-based or ChromaDB-backed unless that implementation is added and verified. The optional Gemini external-search path is a separate mode and should be evaluated separately.

## Reproducibility checklist

- [ ] Version the corpus and expected-answer file.
- [ ] Keep a fixed test split.
- [ ] Store raw retrieved passages and generated answers.
- [ ] Include empty-context and unanswerable questions.
- [ ] Publish results only after an actual run.
