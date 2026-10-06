# vera
An Adaptive Self-Evolving Retrieval-Augmented Generation (RAG) System

> An AI question-answering system that doesn't just generate answers — it verifies them, scores its own confidence, and is architected to learn from its mistakes.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

---

## Overview

Conventional Retrieval-Augmented Generation (RAG) systems retrieve relevant content and generate an answer — with no mechanism to verify whether that answer is actually correct, no way to communicate confidence, and no process for learning from mistakes. Vera addresses this directly.

Vera is a RAG system built on top of a large language model (Claude / NVIDIA-hosted models) that **independently verifies every generated answer against its source material**, assigns a **quantifiable trust score**, and **automatically retries retrieval** when confidence is low — before an answer ever reaches the user. It is designed, not as a replacement for the underlying LLM, but as a trust and verification engineering layer on top of one — following the same architectural philosophy used by companies like Galileo, Braintrust, and Fiddler AI in production LLM observability.

---

## Objectives

1. Design and implement a document-based retrieval pipeline capable of generating source-grounded answers.
2. Develop an independent verification mechanism that checks every generated answer against its source and assigns a measurable trust score.
3. Build an automated evaluation framework using a curated test set to objectively measure system accuracy.
4. Implement a self-improvement mechanism that identifies failure patterns and adjusts the system to improve future performance.
5. Demonstrate measurable improvement in answer accuracy across evaluation cycles.

---

## System Architecture

Vera is structured into four functional layers:
┌─────────────────────┐
│ 1. Ingestion & │ PDF upload → text extraction → chunking →
│ Retrieval │ embeddings → vector storage (Qdrant / pgvector)
└──────────┬───────────┘
▼
┌─────────────────────┐
│ 2. Generation & │ LLM generates answer from retrieved context →
│ Verification │ independent AI call fact-checks the answer →
│ │ trust score assigned → auto-retry if score is low
└──────────┬───────────┘
▼
┌─────────────────────┐
│ 3. Evaluation │ Automated testing against a golden question set →
│ │ failure logging → failure categorization
└──────────┬───────────┘
▼
┌─────────────────────┐
│ 4. Self-Improvement │ Analyze failure patterns → adjust pipeline →
│ (in progress) │ re-validate against evaluation set → keep or revert
└─────────────────────┘

**Layer 1 — Ingestion & Retrieval:** Any user-uploaded PDF is read, split into overlapping chunks, converted into vector embeddings, and stored for semantic search. Implemented and benchmarked across two vector databases (Qdrant and pgvector) with identical retrieval accuracy confirmed in testing.

**Layer 2 — Generation & Verification:** An LLM generates an answer strictly from retrieved context. A second, independent model call verifies every claim in that answer against the source, assigns a trust score (0–100), and triggers a broader retrieval attempt if the score falls below threshold — demonstrated live with a real query recovering from a 20/100 to 100/100 trust score via automatic retry.

**Layer 3 — Evaluation:** A curated golden test set is used to automatically score system accuracy. Failures are logged with full context and classified by root cause (retrieval issue, generation issue, or genuinely missing information).

**Layer 4 — Self-Improvement:** *(in progress)* The measurement infrastructure — failure logging and categorization — is complete and operational. The fully automated loop that detects recurring failure patterns, adjusts pipeline configuration, and validates improvements before retaining them is the current focus of development.

---

## Features

- 📄 **Document upload** — users can upload any PDF and ask questions grounded in its content
- 🔍 **Semantic retrieval** — meaning-based search, not keyword matching
- ✅ **Independent answer verification** — a second AI pass fact-checks every response
- 📊 **Trust scoring** — every answer ships with a transparent, numeric confidence score and citation trail
- 🔁 **Automatic re-retrieval** — low-confidence answers trigger a broader context search before being finalized
- 🧪 **Automated evaluation framework** — accuracy testing against a golden question set, with failure logging and categorization
- 💬 **Custom chat interface** — a polished, Streamlit-based UI for uploading documents and asking questions interactively

---

## Technology Used

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| LLM / AI | Claude API (Anthropic), NVIDIA NIM (development/testing) |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Document Processing | pypdf, LangChain Text Splitters |
| Vector Databases | Qdrant, PostgreSQL (pgvector) |
| Interface | Streamlit |
| Infrastructure | Docker (containerized Qdrant & pgvector) |
| Version Control | Git, GitHub |

---

## Project Structure
vera/
├── app.py # Streamlit chat interface with document upload
├── ingestion.py # PDF reading, chunking, embedding, storage
├── generate_answer.py # Answer generation, verification, trust scoring
├── evaluate.py # Automated evaluation framework
├── golden_test_set.py # Curated test questions for evaluation
├── ingest_pgvector.py # pgvector ingestion (comparison database)
├── search_test.py # Qdrant retrieval testing
├── search_test_pgvector.py # pgvector retrieval testing
├── verify_test.py # Verification layer test suite
├── requirements.txt
└── README.md


---

## Current Status

| Component | Status |
|---|---|
| Ingestion & Retrieval (dual database) | ✅ Complete |
| Generation & Verification | ✅ Complete |
| Trust Scoring & Auto-Retry | ✅ Complete |
| Document Upload Interface | ✅ Complete |
| Evaluation Framework | ✅ Complete |
| Failure Logging & Categorization | ✅ Complete |
| Automated Self-Improvement Loop | 🔧 In Progress |
| REST API Backend (FastAPI) | ⏳ Planned |
| Containerized Deployment | ⏳ Planned |

---

## Getting Started

### Prerequisites
- Python 3.12+
- Docker Desktop
- An Anthropic API key and/or NVIDIA NIM API key

### Setup
```bash
git clone https://github.com/Shakti-111/vera.git
cd vera
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:
ANTHROPIC_API_KEY= my key XXXX
NVIDIA_API_KEY= my key XXXX

Start the vector databases:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
docker run -d --name pgvector-db -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 pgvector/pgvector:pg16
```

Run the app:
```bash
streamlit run app.py
```

---

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built using Anthropic's Claude API and NVIDIA's NIM platform for LLM access, Qdrant and pgvector for vector storage, and Streamlit for the interface.