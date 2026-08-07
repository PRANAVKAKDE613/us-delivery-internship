import json
import os
import random
from datetime import datetime, timedelta

def generate_mock_dataset(base_dir):
    os.makedirs(os.path.join(base_dir, "data", "knowledge_base"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, ".github", "workflows"), exist_ok=True)

    # 1. Knowledge Base Markdown Docs
    kb_docs = {
        "auth_sso.md": """# Authentication and Single Sign-On (SSO) Troubleshooting

## Common Issues & Error Codes
- **Error OAuth_401**: Expired client credentials or invalid secret.
- **SAML Assertion Failed**: IdP metadata mismatch or clock skew between IdP and Service Provider.
- **Session Timeout**: Default session duration is 8 hours. Can be overridden in Org Security Settings.

## Resolution Steps
1. Verify SAML XML certificate expiration.
2. Ensure user email matches the user principal name (UPN) in Active Directory / Okta.
3. For SCIM provisioning failures, trigger a manual sync under Organization Settings > Security.
""",
        "api_rate_limits.md": """# API Rate Limits & Throttling Guidelines

## Standard Limits
- **Starter Plan**: 100 requests / minute
- **Enterprise Plan**: 10,000 requests / minute
- **HTTP 429 Too Many Requests**: Returned when limit is exceeded.

## Best Practices & Solutions
- Implement exponential backoff with jitter on HTTP 429 responses.
- Utilize webhooks instead of high-frequency polling.
- Request a temporary rate limit burst increase via Support for migration events.
""",
        "webhook_deliveries.md": """# Webhook Failures and Retry Policy

## Symptoms & Error Codes
- **Webhook Status 504 Gateway Timeout**: Endpoint took > 5000ms to respond.
- **Signature Verification Failed**: `X-Signature-SHA256` header does not match payload secret.

## Troubleshooting Workflow
1. Verify endpoint responds with HTTP 200 within 5 seconds.
2. Check firewall and IP allowlist (allow standard egress IPs: 192.0.2.1-192.0.2.254).
3. System automatically retries failed deliveries 5 times with exponential backoff before disabling the endpoint.
""",
        "database_sync.md": """# Database Sync & Data Pipeline Errors

## Known Issue Patterns
- **Sync Lag > 60 mins**: Secondary replica lagging behind primary write node during peak load.
- **Schema Drift Error**: Column type mismatch between source warehouse (BigQuery/Snowflake) and app store.

## Resolution Guidelines
1. Pause running pipelines before altering source schemas.
2. Re-trigger full sync for corrupted table slices from Admin Console > Pipelines.
3. Escalation: Contact Infrastructure / Data Platform team for replication queue resets.
""",
        "billing_subscriptions.md": """# Subscription Management & Invoicing

## Common Inquiries
- **Unplanned Overage Charges**: Caused by unexpected API surge or seats added mid-billing cycle.
- **Failed Payment Retry**: System attempts payment 3 times over 7 days before suspending account.
- **Downgrade Requests & Cancellation**: Pro-rated refunds apply within 14 days of renewal.

## Action Protocol
- Route billing dispute tickets over $1,000 to TAM & Finance Escalations.
- Check invoices tab in Billing Portal before adjusting credits.
"""
    }

    for filename, content in kb_docs.items():
        with open(os.path.join(base_dir, "data", "knowledge_base", filename), "w", encoding="utf-8") as f:
            f.write(content.strip())

    # 2. Account Summaries (50 accounts)
    tiers = ["Enterprise", "Mid-Market", "SMB"]
    industries = ["Fintech", "Healthcare", "E-commerce", "SaaS", "Logistics", "Retail"]
    accounts = []

    for i in range(1, 51):
        account_id = f"ACC-{i:03d}"
        tier = random.choice(tiers)
        mrr = random.randint(500, 25000) if tier != "Enterprise" else random.randint(25000, 150000)
        csm = f"TAM_{random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Evan'])}"
        
        accounts.append({
            "account_id": account_id,
            "company_name": f"Acme {industries[i % len(industries)]} {i}",
            "tier": tier,
            "mrr": mrr,
            "assigned_tam": csm,
            "contract_end_date": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "health_score": random.choice(["HEALTHY", "AT_RISK", "CRITICAL", "STABLE"]),
            "summary": f"{tier} customer in {industries[i % len(industries)]} processing high transaction volume. Main contact is VP of Engineering. Active contract renewed annually."
        })

    with open(os.path.join(base_dir, "data", "accounts.json"), "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

    # 3. 500 Synthetic Support Tickets
    product_areas = ["Authentication", "API Integrations", "Webhooks", "Data Sync", "Billing & Plans"]
    issue_categories = ["Bug Report", "Performance Issue", "Account Access", "Billing Dispute", "Feature Request"]
    
    churn_phrases = [
        "We are seriously considering cancelling our subscription and moving to your competitor if this isn't fixed today.",
        "Our legal and procurement team is reviewing our contract termination options due to repeated downtime.",
        "If this P1 outage isn't resolved in 1 hour, we will demand a full refund and switch providers.",
        "This breach of SLA is unacceptable. We are halting our deployment and looking for alternatives.",
        "We spend over $50,000/month with you and cannot get decent support. Escalating to executive leadership."
    ]

    normal_issues = [
        ("SAML SSO login failing with OAuth_401 error", "Users in our organization are unable to log in via Okta SAML SSO since 9 AM EST. Error message displayed is OAuth_401 invalid client credentials. Please assist immediately."),
        ("HTTP 429 Rate limit reached during batch sync", "Our nightly data ingestion pipeline is getting throttled with HTTP 429 Too Many Requests. We need our rate limits increased or guidance on exponential backoff."),
        ("Webhook events dropping for payment updates", "Webhooks for invoice payment events are timing out with 504 Gateway Timeout. Our endpoint is fine, payload signature verification might be failing."),
        ("Database sync lag over 90 minutes", "The data synchronization between our PostgreSQL database and the reporting dashboard is lagging by 1.5 hours. Reporting tables are stale."),
        ("Overage charges on invoice INV-2026-88", "We were charged $2,400 for API overages this month, but our tier includes 500k calls. Please review and issue a refund credit.")
    ]

    tickets = []
    start_date = datetime.now() - timedelta(days=120)

    for i in range(1, 501):
        ticket_id = f"TCK-{i:04d}"
        account = random.choice(accounts)
        created_days_ago = random.randint(1, 115)
        created_at = (datetime.now() - timedelta(days=created_days_ago, hours=random.randint(0, 23))).isoformat()
        
        # Inject churn/escalation risk into ~15% of tickets
        has_churn_risk = random.random() < 0.15
        
        area = random.choice(product_areas)
        cat = random.choice(issue_categories)
        
        base_subj, base_body = random.choice(normal_issues)
        subject = f"[{area}] {base_subj} - {account['company_name']}"
        
        body = base_body
        if has_churn_risk:
            body += f"\n\nUrgent Notice: {random.choice(churn_phrases)}"

        # Assign urgency
        if has_churn_risk or "P1 outage" in body or "OAuth_401" in body:
            urgency = random.choice(["P1", "P2"])
        else:
            urgency = random.choice(["P2", "P3", "P4"])

        tickets.append({
            "ticket_id": ticket_id,
            "account_id": account["account_id"],
            "subject": subject,
            "body": body,
            "created_at": created_at,
            "status": random.choice(["OPEN", "RESOLVED", "PENDING_CUSTOMER"]),
            "urgency": urgency,
            "has_churn_signal": has_churn_risk
        })

    with open(os.path.join(base_dir, "data", "tickets.json"), "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)

    print(f"Generated mock dataset successfully in {base_dir}/data:")
    print(f" - {len(kb_docs)} KB documents")
    print(f" - {len(accounts)} Customer accounts")
    print(f" - {len(tickets)} Support tickets")

if __name__ == "__main__":
    generate_mock_dataset("C:\\Users\\rites\\.gemini\\antigravity\\scratch\\us-delivery-internship")
