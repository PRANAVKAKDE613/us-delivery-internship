# Task 4: Design Note - Technical Architecture & Systems Engineering

**Role**: AI Engineering Team (Technical Support & TAM Platform)  
**Author**: Candidate  
**Target Scope**: Intelligent Support Triage & TAM Account Health Summarizer Systems  

---

## 1. Failure Modes & Production Resiliency

In a production environment supporting hundreds of internal engineers and TAMs, LLM-powered pipelines must handle non-deterministic inputs and external dependencies safely. Below are the top 3 production failure modes, their detection mechanisms, and mitigation strategies:

### 1.1 RAG Retrieval Misses & Hallucinated KB Mapping
- **Failure Mode**: Incoming tickets describing novel edge cases or un-documented bugs cause the RAG retriever to surface irrelevant Knowledge Base (KB) articles or induce LLM hallucination.
- **Detection**: Implement a strict confidence score threshold gate (minimum similarity cutoff score of `0.45`). Track user feedback telemetry (e.g., Support agent clicking "Irrelevant KB doc" in the UI).
- **Mitigation**: If retrieval confidence falls below threshold, the system gracefully falls back to `matched_kb_doc: null` rather than outputting a low-confidence match. Low-confidence queries are automatically queued into a Technical Writing triage pipeline to draft missing KB articles.

### 1.2 Classification Drift on Implicit Churn & Escalation Signals
- **Failure Mode**: Subtle or sarcastic customer churn signals (e.g., *"Guess we will be re-evaluating our vendor stack next quarter"*) bypass basic keyword classifiers, resulting in misclassifying a high-risk P1 ticket as a low-priority P4 ticket.
- **Detection**: Run automated daily regression evaluations using `eval_harness.py`. Monitor telemetry comparing account health score changes against ticket priority assignments.
- **Mitigation**: Utilize a multi-stage prompt chain where Stage 1 extracts customer sentiment and churn intent before Stage 2 assigns urgency. Maintain a human-in-the-loop escalation trigger allowing TAMs to manually override ticket priority.

### 1.3 Upstream LLM Latency Spikes & Rate Limit Failures (HTTP 429)
- **Failure Mode**: External LLM API outages or rate-limit throttling cause ticket processing timeouts during peak support load.
- **Detection**: OpenTelemetry APM monitoring tracking HTTP 5xx error rates, API circuit-breaker trips, and p99 response times exceeding 2,000ms.
- **Mitigation**: Deploy a fallback hierarchy: if the primary LLM API times out (> 1.5s) or returns 429, fall back to an optimized local rule-based classifier engine (`classify_ticket_rule_based`). Decouple processing via asynchronous Celery/Redis worker queues.

---

## 2. Latency vs. Quality Trade-offs

### 2.1 Concrete Trade-off Implemented
In **Task 2 (TAM Account Health Summariser)**, we prioritized **output quality and 100% determinism** over sub-second response times. The engine performs full multi-doc aggregation across 90 days of ticket history, extracts verbatim direct quotes for risk verification, and enforces strict structural validation. This process requires ~200–500ms of synchronous processing per account brief.

### 2.2 Design Adjustments Under Hard Latency Constraints (< 100ms)
If sub-100ms latency were a hard constraint:
1. **Pre-aggregated Summarization Jobs**: Compute and cache account summaries in background cron tasks updated every hour or upon ticket ingestion, converting API calls into instant key-value database reads ($O(1)$ lookup).
2. **Streaming Response Infrastructure**: Utilize FastAPI `StreamingResponse` so clients receive initial tokens within 30ms while subsequent sections render in real-time.
3. **Quantized / Fast Classifier Models**: Replace full LLM passes for Task 1 with fine-tuned local mini models (e.g., SetFit / ONNX quantized DistilBERT) executing inference in < 15ms.

---

## 3. Data Sensitivity & PII Protection

Support tickets and account summaries routinely contain Personally Identifiable Information (PII), API keys, and sensitive financial figures.

### 3.1 Privacy Architecture & Safeguards
1. **In-Flight PII Redaction Pipeline**: Before any ticket body or account text is processed by LLM prompts or vector stores, it passes through a high-speed regex & NER scrubbing engine (e.g., Microsoft Presidio) to redact sensitive entities:
   - Email addresses $\rightarrow$ `[EMAIL_REDACTED]`
   - API Secrets & Tokens $\rightarrow$ `[KEY_REDACTED]`
   - IP Addresses & Credit Cards $\rightarrow$ `[SENSITIVE_DATA_REDACTED]`
2. **Zero Data Retention (ZDR) Compliance**: Enterprise LLM integrations are configured with ZDR policies guaranteeing vendor APIs do not log, persist, or train models on input prompts.
3. **Role-Based Access Control (RBAC)**: Account brief data views are scoped by user tier—preventing Tier-1 support representatives from viewing confidential MRR and contract terms restricted to TAMs.

---

## 4. Scaling Architecture (10× Ticket Volume)

Scaling from 500 tickets to 5,000+ daily tickets exposes specific infrastructural bottlenecks:

### 4.1 System Bottlenecks at 10× Load
- **In-Memory File I/O**: Reading static `tickets.json` and `accounts.json` from disk on every query causes severe CPU and memory saturation.
- **RAG Linear Scanning**: Scanning raw markdown files linearly ($O(N)$) for KB retrieval degrades search performance as the doc count grows.

### 4.2 Production Scaling Roadmap
1. **Database Tier**: Migrate JSON storage to PostgreSQL / AlloyDB with indexed B-Trees on `account_id`, `created_at`, and `urgency` ($O(\log N)$ time complexity).
2. **Vector DB Indexing**: Replace file-based matching with a dedicated Vector DB (Qdrant / pgvector) using HNSW indexing for sub-10ms semantic retrieval.
3. **Event-Driven Async Workers**: Transition synchronous REST endpoints to an event-driven architecture powered by Apache Kafka / AWS SQS, scaling worker nodes horizontally with Kubernetes HPA.
