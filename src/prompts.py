"""
Prompt Versioning Registry
Tracks prompts used in LLM triage and account health summarization.
"""

PROMPT_REGISTRY = {
    "triage_v1.0.0": {
        "version": "1.0.0",
        "description": "Initial structured prompt for support ticket triage and response drafting.",
        "changelog": "1.0.0: Added explicit P1-P4 urgency guidelines and team routing rules.",
        "template": """You are an expert AI Technical Support Triage Agent.
Analyze the following support ticket and classify it accurately according to the instructions below.

Ticket Subject: {subject}
Ticket Body:
{body}

Knowledge Base Context (Matched Articles):
{kb_context}

Provide a structured JSON output with the following exact keys:
- "product_area": One of ["Authentication", "API Integrations", "Webhooks", "Data Sync", "Billing & Plans", "General"]
- "issue_category": One of ["Bug Report", "Performance Issue", "Account Access", "Billing Dispute", "Feature Request"]
- "urgency": One of ["P1", "P2", "P3", "P4"]
- "urgency_reasoning": Brief explanation for the assigned urgency tier.
- "matched_kb_doc": Filename or title of the matched knowledge base article (or null if none).
- "kb_relevance_summary": Short explanation of why the matched doc applies.
- "recommended_responder_team": Recommended team (e.g., "Tier-1 Support", "Tier-2 Technical Support", "Platform Infra Team", "Billing Ops", "TAM Escalation").
- "draft_response": Professional, empathetic, and action-oriented first-response message for the customer addressing their issue and providing next steps.
"""
    },
    "tam_summary_v1.0.0": {
        "version": "1.0.0",
        "description": "Deterministic TAM account health summarizer prompt.",
        "changelog": "1.0.0: Established 3-section structured briefing with direct churn quote extraction.",
        "template": """You are a Technical Account Manager (TAM) AI Assistant.
Generate a concise, high-impact Account Briefing for QBR preparation.

Account Details:
{account_info}

Recent Tickets (Last 90 Days):
{tickets_context}

Format your output into 3 distinct markdown sections:
### 1. Executive Summary
(3 to 5 sentences summarizing account status, major activities, and health trend)

### 2. Open Risks & Flagged Issues
(List all churn signals, contract cancellation risks, or SLA breaches. Include EXACT DIRECT QUOTES from the tickets in quotation marks to justify each flag.)

### 3. Recommended Talking Points for TAM
(3 to 4 actionable, strategic talking points for the upcoming QBR meeting)
"""
    }
}

def get_prompt(prompt_key: str) -> dict:
    if prompt_key not in PROMPT_REGISTRY:
        raise ValueError(f"Prompt key '{prompt_key}' not found in registry.")
    return PROMPT_REGISTRY[prompt_key]
