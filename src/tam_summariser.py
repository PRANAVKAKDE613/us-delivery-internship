import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel
from src.prompts import get_prompt

class TAMAccountBrief(BaseModel):
    account_id: str
    company_name: str
    tier: str
    mrr: int
    assigned_tam: str
    health_score: str
    total_tickets_90d: int
    flagged_churn_tickets: int
    executive_summary: str
    open_risks_and_flagged_issues: List[Dict[str, str]]
    recommended_talking_points: List[str]
    formatted_markdown_brief: str
    is_deterministic: bool = True
    prompt_version: str = "v1.0.0"

class TAMSummariserEngine:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.accounts_file = os.path.join(data_dir, "accounts.json")
        self.tickets_file = os.path.join(data_dir, "tickets.json")
        self._load_data()

    def _load_data(self):
        with open(self.accounts_file, "r", encoding="utf-8") as f:
            self.accounts = {acc["account_id"]: acc for acc in json.load(f)}
        
        with open(self.tickets_file, "r", encoding="utf-8") as f:
            self.all_tickets = json.load(f)

    def get_account_tickets_90d(self, account_id: str, anchor_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        acc_tickets = [t for t in self.all_tickets if t.get("account_id") == account_id]
        if not acc_tickets:
            return []

        if anchor_date is None:
            # Use latest ticket date across all tickets as anchor if not specified
            timestamps = [datetime.fromisoformat(t["created_at"]) for t in self.all_tickets if "created_at" in t]
            anchor_date = max(timestamps) if timestamps else datetime.now()

        cutoff_date = anchor_date - timedelta(days=90)
        
        filtered = []
        for t in acc_tickets:
            dt = datetime.fromisoformat(t["created_at"])
            if dt >= cutoff_date:
                filtered.append(t)
        
        # Sort deterministically by created_at descending, then ticket_id
        filtered.sort(key=lambda x: (x.get("created_at", ""), x.get("ticket_id", "")), reverse=True)
        return filtered

    def detect_churn_and_escalation_signals(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        flagged = []
        churn_keywords = [
            "cancelling", "cancel", "competitor", "switch", "termination", 
            "legal", "refund", "breach of sla", "outage", "escalating", "unacceptable"
        ]

        for t in tickets:
            body = t.get("body", "")
            subj = t.get("subject", "")
            full_text = f"{subj}\n{body}"
            
            lines = full_text.split("\n")
            direct_quotes = []
            
            for line in lines:
                line_clean = line.strip()
                if any(kw in line_clean.lower() for kw in churn_keywords):
                    if line_clean and len(line_clean) > 10:
                        direct_quotes.append(f'"{line_clean}"')

            if direct_quotes or t.get("has_churn_signal", False) or t.get("urgency") == "P1":
                quote_text = " | ".join(direct_quotes) if direct_quotes else f'"{body[:120]}..."'
                flagged.append({
                    "ticket_id": t.get("ticket_id", "N/A"),
                    "urgency": t.get("urgency", "P2"),
                    "subject": subj,
                    "direct_quote": quote_text,
                    "risk_level": "CRITICAL CHURN RISK" if "cancelling" in quote_text.lower() or "sla" in quote_text.lower() else "HIGH ESCALATION"
                })

        # Sort deterministically by ticket_id
        flagged.sort(key=lambda x: x["ticket_id"])
        return flagged

    def generate_brief(self, account_id: str) -> TAMAccountBrief:
        if account_id not in self.accounts:
            raise ValueError(f"Account ID '{account_id}' not found in database.")

        acc = self.accounts[account_id]
        tickets_90d = self.get_account_tickets_90d(account_id)
        flagged_risks = self.detect_churn_and_escalation_signals(tickets_90d)

        # 1. Executive Summary (3 to 5 sentences)
        company_name = acc["company_name"]
        tier = acc["tier"]
        mrr = acc["mrr"]
        csm = acc["assigned_tam"]
        health = acc["health_score"]
        
        exec_summary = (
            f"{company_name} is a {tier} tier customer generating ${mrr:,}/month in recurring revenue, managed by {csm}. "
            f"Over the past 90 days, the account logged {len(tickets_90d)} support tickets, with {len(flagged_risks)} tickets flagged for churn or escalation signals. "
            f"The account is currently evaluated as {health} health status with contract renewal set for {acc.get('contract_end_date', 'N/A')}. "
            f"Overall operational activity reflects active product usage alongside specific technical friction points requiring proactive TAM intervention."
        )

        # 2. Open Risks & Flagged Issues
        risks_md = []
        if flagged_risks:
            for r in flagged_risks:
                risks_md.append(f"- **Ticket {r['ticket_id']} [{r['urgency']}]**: {r['risk_level']} - Subject: `{r['subject']}`\n  > **Direct Quote**: {r['direct_quote']}")
        else:
            risks_md.append("- No immediate churn or critical escalation signals detected in the last 90 days.")

        open_risks_text = "\n".join(risks_md)

        # 3. Recommended Talking Points for TAM
        talking_points = []
        if flagged_risks:
            talking_points.append(f"Acknowledge recent technical escalations (Ticket {flagged_risks[0]['ticket_id']}) and present root-cause resolution roadmap.")
            talking_points.append(f"Review SLA compliance and discuss custom rate-limit or infrastructure scaling options to prevent future bottlenecks.")
        else:
            talking_points.append(f"Highlight steady account performance and low ticket volume ({len(tickets_90d)} tickets in 90 days).")
            talking_points.append("Explore opportunities for tier expansion or adopting newly released product integrations.")

        talking_points.append(f"Review contract renewal timeline ({acc.get('contract_end_date', 'N/A')}) and align on executive sponsor QBR targets.")
        talking_points.append(f"Offer a dedicated architecture review session with Tier-2 engineering for upcoming migration projects.")

        talking_points_text = "\n".join([f"{idx+1}. {tp}" for idx, tp in enumerate(talking_points)])

        # Synthesize Markdown Briefing
        md_brief = f"""# TAM Account Brief: {company_name} ({account_id})

**Tier**: {tier} | **MRR**: ${mrr:,} | **Assigned TAM**: {csm} | **Health**: `{health}` | **Renewal**: {acc.get('contract_end_date', 'N/A')}

---

### 1. Executive Summary
{exec_summary}

---

### 2. Open Risks & Flagged Issues
{open_risks_text}

---

### 3. Recommended Talking Points for TAM
{talking_points_text}
"""

        return TAMAccountBrief(
            account_id=account_id,
            company_name=company_name,
            tier=tier,
            mrr=mrr,
            assigned_tam=csm,
            health_score=health,
            total_tickets_90d=len(tickets_90d),
            flagged_churn_tickets=len(flagged_risks),
            executive_summary=exec_summary,
            open_risks_and_flagged_issues=flagged_risks,
            recommended_talking_points=talking_points,
            formatted_markdown_brief=md_brief,
            is_deterministic=True,
            prompt_version="v1.0.0"
        )

    def stream_brief(self, account_id: str) -> Generator[str, None, None]:
        """
        Simulates real-time token streaming for Task 2 UI/API consumption.
        """
        brief = self.generate_brief(account_id)
        lines = brief.formatted_markdown_brief.split("\n")
        for line in lines:
            yield line + "\n"

def generate_account_brief(account_id: str, data_dir: str = "data") -> TAMAccountBrief:
    engine = TAMSummariserEngine(data_dir=data_dir)
    return engine.generate_brief(account_id)

if __name__ == "__main__":
    brief = generate_account_brief("ACC-001")
    print(brief.formatted_markdown_brief)
