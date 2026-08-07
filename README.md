# Technical Support & TAM AI Platform

> **Production-grade AI for Technical Support & Technical Account Management Teams**  
> *US Delivery Internship — Technical Interview Task Round*

---

## 📋 Executive Overview

This repository provides an enterprise-ready AI microservice platform designed for **Technical Support Engineers** (Tier-1/Tier-2) and **Technical Account Managers (TAMs)**. It ingests customer tickets and structured account data to perform automated triage, RAG knowledge retrieval, risk detection, and account health briefing.

### Key Capabilities
- **Task 1: Intelligent Ticket Triage Agent**: Free-text classification, P1–P4 urgency scoring, RAG Knowledge Base doc matching, target team routing, and auto-drafting first responses.
- **Task 2: TAM Account Health Summariser**: Deterministic 3-section account briefs from 90-day ticket history with direct quote risk justifications and real-time streaming support.
- **Task 3: Evaluation Harness**: Systematized eval framework with 10 test cases (including adversarial tests), quality scores (0.0 to 1.0), and 100% pass rate reporting.
- **Task 4: Design Note**: Comprehensive analysis of production failure modes, latency vs quality trade-offs, PII protection, and 10x scaling.
- **Bonus Features (+10 Marks)**: Interactive Streamlit UI web app, token streaming, automated GitHub Actions CI workflow, and prompt versioning registry.

---

## 🛠️ Quickstart & Setup Guide

### 1. Installation
Clone the repository and install dependencies from `requirements.txt`:
```bash
# Clone repository
git clone https://github.com/your-username/us-delivery-internship.git
cd us-delivery-internship

# Install dependencies
pip install -r requirements.txt
```

### 2. Single Entry-Point Commands

#### A. Run FastAPI REST Server (Task 1 & Task 2 APIs)
```bash
python -m src.api
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health check endpoint: `http://localhost:8000/health`

#### B. Launch Streamlit Web UI (Bonus UI Demo)
```bash
streamlit run app.py
```

#### C. Run Pytest Test Suite
```bash
python -m pytest tests/
```

#### D. Run Evaluation Harness & Generate Reports
```bash
python -m src.eval_harness
```

---

## 🎫 Task 1: Intelligent Ticket Triage Agent

### Python API Usage
```python
from src.triage_agent import triage_ticket

ticket = {
    "subject": "[Authentication] SAML SSO login failing with OAuth_401 error",
    "body": "Users are unable to log in via Okta SAML SSO. Error OAuth_401 invalid credentials. We are considering cancelling our account if not fixed!"
}

result = triage_ticket(ticket)
print(result.model_dump_json(indent=2))
```

### Sample Output JSON (`POST /api/v1/triage`)
```json
{
  "ticket_id": null,
  "product_area": "Authentication",
  "issue_category": "Bug Report",
  "urgency": "P1",
  "urgency_reasoning": "Critical outage, security auth failure, or high escalation/churn risk identified in ticket.",
  "matched_kb_doc": "auth_sso.md",
  "kb_relevance_summary": "Matched knowledge base article 'auth_sso.md' (Score: 8). Main topic: # Authentication and Single Sign-On (SSO) Troubleshooting",
  "recommended_responder_team": "Strategic TAM Escalation & Executive Support",
  "draft_response": "Hello,\n\nThank you for reaching out to Technical Support. We have logged your request under [P1] priority and routed it directly to our Strategic TAM Escalation & Executive Support.\n\nBased on your report, this issue aligns with our knowledge base guide 'auth_sso.md'...",
  "prompt_version": "v1.0.0"
}
```

---

## 📊 Task 2: TAM Account Health Summariser

### Python API Usage
```python
from src.tam_summariser import generate_account_brief

brief = generate_account_brief("ACC-001")
print(brief.formatted_markdown_brief)
```

### Sample Output Briefing (`ACC-001`)
```markdown
# TAM Account Brief: Acme Healthcare 1 (ACC-001)

**Tier**: SMB | **MRR**: $2,066 | **Assigned TAM**: TAM_Bob | **Health**: `CRITICAL` | **Renewal**: 2026-12-21

---

### 1. Executive Summary
Acme Healthcare 1 is a SMB tier customer generating $2,066/month in recurring revenue, managed by TAM_Bob. Over the past 90 days, the account logged 4 support tickets, with 3 tickets flagged for churn or escalation signals. The account is currently evaluated as CRITICAL health status with contract renewal set for 2026-12-21. Overall operational activity reflects active product usage alongside specific technical friction points requiring proactive TAM intervention.

---

### 2. Open Risks & Flagged Issues
- **Ticket TCK-0001 [P3]**: HIGH ESCALATION - Subject: `[Billing & Plans] Overage charges on invoice INV-2026-88 - Acme Healthcare 1`
  > **Direct Quote**: "We were charged $2,400 for API overages this month, but our tier includes 500k calls. Please review and issue a refund credit."
- **Ticket TCK-0458 [P1]**: HIGH ESCALATION - Subject: `[API Integrations] SAML SSO login failing with OAuth_401 error - Acme Healthcare 1`
  > **Direct Quote**: "Users in our organization are unable to log in via Okta SAML SSO since 9 AM EST. Error message displayed is OAuth_401 in..."

---

### 3. Recommended Talking Points for TAM
1. Acknowledge recent technical escalations (Ticket TCK-0001) and present root-cause resolution roadmap.
2. Review SLA compliance and discuss custom rate-limit or infrastructure scaling options to prevent future bottlenecks.
3. Review contract renewal timeline (2026-12-21) and align on executive sponsor QBR targets.
4. Offer a dedicated architecture review session with Tier-2 engineering for upcoming migration projects.
```

---

## 🧪 Task 3: Evaluation Harness Summary

Run `python -m src.eval_harness` to generate `eval_report.json` and `eval_report.md`.

| Metric | Result |
|---|---|
| **Total Test Cases** | 10 (5 per task, including 2 Adversarial tests) |
| **Overall Pass Rate** | **100.0%** (10/10 Passed) |
| **Average Quality Score** | **1.0 / 1.0** |
| **Task 1 Triage Pass Rate** | 100.0% |
| **Task 2 Summariser Pass Rate** | 100.0% |

---

## 📄 Task 4: Design Note

*(The complete design note document is available in [`DESIGN_NOTE.md`](DESIGN_NOTE.md))*

### Summary Highlights:
1. **Failure Modes**: Addresses RAG retrieval misses (mitigated via confidence cutoff gates), classification drift (mitigated via multi-stage prompt chaining), and API rate limits (mitigated via local rule fallback and async queues).
2. **Latency vs Quality**: Prioritized 100% output determinism and quote verification over sub-second response times. Proposed background cron pre-aggregation for sub-50ms hard constraints.
3. **Data Sensitivity**: Enforces in-flight PII redaction (NER/regex scrubbing), Zero Data Retention (ZDR) LLM contracts, and role-based field masking.
4. **10x Scaling**: Outlines migration from JSON files to PostgreSQL/AlloyDB ($O(\log N)$), vector DB indexing (Qdrant/HNSW), and Kafka event-driven async processing.

---

## ⭐ Bonus Features Overview

- **+5 Streamlit Thin UI Demo**: Launch with `streamlit run app.py` for live ticket triage, TAM briefing, and eval dashboard.
- **+3 Real-time Token Streaming**: Available via `GET /api/v1/account-brief/{account_id}/stream`.
- **+2 GitHub Actions CI**: Automated `.github/workflows/eval_ci.yml` running unit tests and evaluation harness on push/PR.
- **+2 Centralized Prompt Versioning**: Managed in `src/prompts.py` with version identifier `v1.0.0` and changelog tracking.
