import pytest
from src.triage_agent import triage_ticket, TriageResult

def test_triage_p1_authentication():
    ticket = {
        "subject": "Critical SAML SSO login failure OAuth_401",
        "body": "All employees are unable to log in via Okta SAML. Production outage! We will cancel our account if not fixed."
    }
    result = triage_ticket(ticket)
    assert isinstance(result, TriageResult)
    assert result.product_area == "Authentication"
    assert result.urgency == "P1"
    assert result.matched_kb_doc == "auth_sso.md"
    assert "auth_sso.md" in result.draft_response
    assert result.recommended_responder_team != ""

def test_triage_billing_p3():
    ticket = {
        "subject": "Invoice dispute for last month overage",
        "body": "We noticed a $500 overage charge on invoice INV-2026-99. Can you review?"
    }
    result = triage_ticket(ticket)
    assert result.product_area == "Billing & Plans"
    assert result.issue_category in ["Billing Dispute", "Bug Report"]
    assert result.urgency in ["P2", "P3", "P4"]

def test_triage_raw_string_input():
    raw_text = "Webhook deliveries timing out with 504 Gateway Timeout errors."
    result = triage_ticket(raw_text)
    assert result.product_area == "Webhooks"
    assert result.matched_kb_doc == "webhook_deliveries.md"
