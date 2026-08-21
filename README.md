# Iris — Voice-Enabled RAG Model (#IrisAI)

![Iris AI](https://img.shields.io/badge/Iris-Voice--RAG-ff2a85?style=for-the-badge)
![Hashtag](https://img.shields.io/badge/%23IrisAI-Mandatory-00f0ff?style=for-the-badge)
![Latency](https://img.shields.io/badge/Latency-%3C200ms-00ff66?style=for-the-badge)

A high-performance **Voice-Enabled Retrieval-Augmented Generation (RAG) System** built for **HackerHouse Goa (HH Goa 2026)**. The system transcribes spoken voice queries, executes engineered chunking and sub-5ms vector retrieval over the **MSMARCO-XI** dataset, enforces multi-tier guardrails, and synthesizes answers inside a resilient model harness — **all under 200ms end-to-end latency**.

---

## 🌟 Key Features

### 1. 🎤 Voice Input & Dual Speech-To-Text (STT)
- **Web Speech API & Web Audio**: Sub-50ms instant client-side voice transcription with live pulse waveform visualizer.
- **Sarvam AI & ElevenLabs STT Adapters**: Server-side API adapters for Sarvam AI (`saarika:v1` STT) and ElevenLabs real-time speech conversion.

### 2. 🧩 5 Engineered Chunking Strategies
- **Fixed-Size (Naive)**: Rigid 200-character windows without overlap.
- **Overlap-Optimized**: Sliding 200-character windows with 50-character overlap handling to eliminate boundary truncation.
- **Semantic Sentence-Boundary**: Splits along natural sentence (`.`, `!`, `?`) and paragraph breaks to preserve coherent human thoughts.
- **Metadata-Aware**: Injects document title, passage ID, and category tags directly into every chunk header for enriched context vector embedding.
- **Hierarchical Parent-Child**: Generates micro 100-character child chunks for high-precision similarity matching linked back to full parent context.

### 3. ⚡ Sub-200ms Vector Retrieval & Generation
- In-memory hybrid TF-IDF + Dense Vector similarity search engine completing retrieval in **< 5ms**.
- Grounded answer synthesis engine achieving **< 20ms** context synthesis.

### 4. 🛡️ Guardrail Engine (Knowing *When NOT* to Answer)
- **Pre-Retrieval Input Safety**: Detects prompt injection attempts, malicious commands, and toxic inputs.
- **Off-Topic Relevance Filter**: Filters out queries outside the indexed knowledge domain (e.g. asking pizza recipes or French geography when knowledge base is AI & Goa tech).
- **Retrieval Confidence Thresholding**: Enforces minimum vector similarity scores before triggering generation.
- **Answer Grounding & Hallucination Validator**: Post-generation check that cross-evaluates generated answer tokens against retrieved context passages.
- **Structured Abstain Handler**: Refuses ungrounded responses cleanly with clear rationale.

### 5. 🛡️ Agent Harness & Structured Orchestration
- Managed execution pipeline enforcing Pydantic schema contracts.
- Built-in retries with exponential backoff and query expansion when confidence is low.
- Complete execution trace telemetry for every pipeline step.

### 6. 📊 Latency Analytics (P50 / P70 / P100)
- Automated benchmarking suite running 25 real test queries across the MSMARCO dataset.
- Real-time computation of **P50 (Median)**, **P70**, and **P100 (Absolute Worst-Case Max)** latency metrics.
- Visual breakdown graphs of STT, Guardrail, Retrieval, and Generation timings.

---

## 🌴 HH Goa Cyber Beach Theme

Designed with a dark tropical cyber aesthetic matching **House of Hackers Goa**:
- Glowing neon sunset gradients (`#ff2a85` pink, `#00f0ff` cyan, `#ffb800` amber).
- Glassmorphic panels with backdrop blur and animated glowing borders.
- Prominent `#RAGInGoa` badges and exportable reports.
- Audio readout synthesizer (Text-to-Speech playback).
- Custom Model & API Key Config modal so teams can plug in custom LLM endpoints!

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```
*(Dependencies: `fastapi`, `uvicorn`, `scikit-learn`, `numpy`, `pydantic`, `requests`)*

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Launch Application
Run the single unified launcher:
```bash
python run_server.py
```

- **Frontend Application UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend API**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Automated Verification & Unit Tests

Run the backend unit test suite:
```bash
python -m unittest backend/tests/test_rag.py
```

Run latency benchmark suite directly via CLI:
```bash
python -c "from backend.rag_engine import VectorRAGEngine; from backend.harness import ModelHarness; from backend.benchmark import LatencyBenchmarkSuite; b = LatencyBenchmarkSuite(ModelHarness(VectorRAGEngine())); print(b.run_benchmark())"
```

---

## 📁 Repository Structure

```
HH-Goa-T2/
├── backend/
│   ├── main.py                  # FastAPI application & REST endpoints
│   ├── dataset_loader.py        # MSMARCO dataset manager
│   ├── chunking.py              # 5 Engineered Chunking strategies
│   ├── rag_engine.py            # Ultra-fast vector retrieval engine (<5ms)
│   ├── guardrails.py           # Safety, Off-topic, & Grounding Guardrails
│   ├── harness.py               # Structured agent harness & retry orchestrator
│   ├── stt_service.py           # Sarvam AI & ElevenLabs STT API adapters
│   ├── benchmark.py             # Latency benchmark suite (P50, P70, P100)
│   └── tests/
│       └── test_rag.py          # Automated pipeline & timing tests
├── frontend/                    # Vite + React Modern Web App
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── index.css            # HH Goa Cyber Dark Glassmorphism CSS
│       ├── App.jsx              # Application Shell & Tab Navigation
│       └── components/
│           ├── Header.jsx       # #RAGInGoa header with neon branding
│           ├── VoiceRAGPlayground.jsx # Voice recorder, STT, RAG answer, latency
│           ├── ChunkingComparator.jsx # 5 Strategy visual inspector
│           ├── LatencyAnalytics.jsx   # P50/P70/P100 benchmark dashboard
│           ├── GuardrailsHarness.jsx  # Guardrail refusal & trace testbed
│           ├── DatasetExplorer.jsx   # MSMARCO passage browser & document adder
│           └── ModelSettingsModal.jsx # Custom LLM endpoint & API key config
├── data/
│   └── msmarco_sample.json      # MSMARCO benchmark dataset sample
├── run_server.py                # Unified FastAPI + Vite launcher
└── README.md
```

---

## 🏷️ Social Media Requirement

Every post, video, and submission for this task includes:
`#RAGInGoa`
