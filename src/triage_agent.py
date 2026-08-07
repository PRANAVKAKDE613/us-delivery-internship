import os
import json
import re
from typing import Dict, Any, Union, Optional
from pydantic import BaseModel
from src.prompts import get_prompt

class TriageResult(BaseModel):
    ticket_id: Optional[str] = None
    product_area: str
    issue_category: str
    urgency: str
    urgency_reasoning: str
    matched_kb_doc: Optional[str] = None
    kb_relevance_summary: Optional[str] = None
    recommended_responder_team: str
    draft_response: str
    prompt_version: str = "v1.0.0"

class KnowledgeBaseRetriever:
    def __init__(self, kb_dir: str):
        self.kb_dir = kb_dir
        self.articles = {}
        self._load_kb()

    def _load_kb(self):
        if not os.path.exists(self.kb_dir):
            return
        for fname in os.listdir(self.kb_dir):
            if fname.endswith(".md"):
                fpath = os.path.join(self.kb_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    self.articles[fname] = f.read()

    def retrieve_best_match(self, text: str) -> tuple[Optional[str], float, Optional[str]]:
        text_lower = text.lower()
        best_doc = None
        max_score = 0
        best_snippet = None

        for fname, content in self.articles.items():
            words = set(re.findall(r'\w+', content.lower()))
            filtered_words = {w for w in words if len(w) > 3}
            ticket_words = set(re.findall(r'\w+', text_lower))
            
            matches = filtered_words.intersection(ticket_words)
            score = len(matches)
            
            if score > max_score and score >= 2:
                max_score = score
                best_doc = fname
                lines = [l.strip() for l in content.split("\n") if l.strip()]
                best_snippet = lines[0] if lines else content[:100]

        return best_doc, max_score, best_snippet

def classify_ticket_rule_based(subject: str, body: str, kb_doc: Optional[str]) -> Dict[str, Any]:
    text = f"{subject}\n{body}".lower()
    
    # 1. Product Area Classification
    if any(k in text for k in ["sso", "saml", "login", "oauth", "password", "authentication"]):
        product_area = "Authentication"
    elif any(k in text for k in ["rate limit", "429", "api key", "endpoint", "api integrations"]):
        product_area = "API Integrations"
    elif any(k in text for k in ["webhook", "504 gateway", "signature", "event delivery"]):
        product_area = "Webhooks"
    elif any(k in text for k in ["sync", "lag", "replica", "schema drift", "pipeline", "database"]):
        product_area = "Data Sync"
    elif any(k in text for k in ["invoice", "charge", "refund", "billing", "subscription", "overage"]):
        product_area = "Billing & Plans"
    else:
        product_area = "General"

    # 2. Issue Category Classification
    if any(k in text for k in ["charge", "invoice", "refund", "overage", "billing dispute"]):
        category = "Billing Dispute"
    elif any(k in text for k in ["slow", "lag", "latency", "performance", "timeout"]):
        category = "Performance Issue"
    elif any(k in text for k in ["cannot log in", "access denied", "account lock"]):
        category = "Account Access"
    elif any(k in text for k in ["feature", "request", "enhancement", "add support"]):
        category = "Feature Request"
    else:
        category = "Bug Report"

    # 3. Urgency Tier & Reasoning
    is_p1_signal = any(k in text for k in [
        "outage", "p1", "breach of sla", "cancelling", "cancel", "legal", "termination", 
        "down for all users", "refund and switch", "production down", "oauth_401", "switch to competitor"
    ])
    is_p2_signal = any(k in text for k in ["throttled", "rate limit", "429", "sync lag", "504 gateway", "failing", "urgent notice"])
    
    if is_p1_signal:
        urgency = "P1"
        reasoning = "Critical outage, security auth failure, or high escalation/churn risk identified in ticket."
    elif is_p2_signal:
        urgency = "P2"
        reasoning = "Major functionality impaired or significant performance degradation reported."
    elif category in ["Bug Report", "Billing Dispute"]:
        urgency = "P3"
        reasoning = "Standard bug or billing inquiry requiring agent review within 24 hours."
    else:
        urgency = "P4"
        reasoning = "Minor request, feature inquiry, or general question with low business impact."

    # 4. Recommended Responder Team
    if urgency == "P1" and ("cancelling" in text or "cancel" in text or "sla" in text or "legal" in text or "competitor" in text):
        team = "Strategic TAM Escalation & Executive Support"
    elif product_area == "Authentication":
        team = "Tier-2 Security & Auth Support"
    elif product_area in ["API Integrations", "Webhooks", "Data Sync"]:
        team = "Tier-2 Platform & Infra Team"
    elif product_area == "Billing & Plans":
        team = "Billing Ops Team"
    else:
        team = "Tier-1 Technical Support"

    # 5. Draft First-Response Message
    draft = f"""Hello,

Thank you for reaching out to Technical Support. We have logged your request under [{urgency}] priority and routed it directly to our {team}.

"""
    if kb_doc:
        draft += f"Based on your report, this issue aligns with our knowledge base guide '{kb_doc}'. Our team is investigating the root cause and will update you shortly.\n"
    else:
        draft += "Our engineering team is currently reviewing your issue details and logs to resolve this as quickly as possible.\n"

    draft += "\nIf you have any additional logs or context to share, please reply directly to this thread.\n\nBest regards,\nCustomer Technical Support Team"

    return {
        "product_area": product_area,
        "issue_category": category,
        "urgency": urgency,
        "urgency_reasoning": reasoning,
        "recommended_responder_team": team,
        "draft_response": draft
    }

def triage_ticket(ticket_input: Union[str, Dict[str, Any]], kb_dir: str = "data/knowledge_base") -> TriageResult:
    if isinstance(ticket_input, str):
        try:
            parsed = json.loads(ticket_input)
            subject = parsed.get("subject", "Support Inquiry")
            body = parsed.get("body", ticket_input)
            ticket_id = parsed.get("ticket_id", None)
        except Exception:
            subject = ticket_input.split("\n")[0][:80]
            body = ticket_input
            ticket_id = None
    elif isinstance(ticket_input, dict):
        subject = ticket_input.get("subject", "Support Inquiry")
        body = ticket_input.get("body", "")
        ticket_id = ticket_input.get("ticket_id", None)
    else:
        raise ValueError("ticket_input must be a string or dictionary")

    full_text = f"{subject}\n{body}"
    retriever = KnowledgeBaseRetriever(kb_dir=kb_dir)
    matched_doc, score, snippet = retriever.retrieve_best_match(full_text)

    triage_data = classify_ticket_rule_based(subject, body, matched_doc)

    kb_summary = f"Matched knowledge base article '{matched_doc}' (Score: {score}). Main topic: {snippet}" if matched_doc else "No relevant KB doc matched."

    return TriageResult(
        ticket_id=ticket_id,
        product_area=triage_data["product_area"],
        issue_category=triage_data["issue_category"],
        urgency=triage_data["urgency"],
        urgency_reasoning=triage_data["urgency_reasoning"],
        matched_kb_doc=matched_doc,
        kb_relevance_summary=kb_summary if matched_doc else None,
        recommended_responder_team=triage_data["recommended_responder_team"],
        draft_response=triage_data["draft_response"],
        prompt_version="v1.0.0"
    )

if __name__ == "__main__":
    sample_ticket = {
        "subject": "[Authentication] SAML SSO login failing with OAuth_401 error",
        "body": "Users are unable to log in via Okta SAML SSO. Error OAuth_401 invalid client credentials. We are considering cancelling if not resolved!"
    }
    result = triage_ticket(sample_ticket)
    print(json.dumps(result.model_dump(), indent=2))
