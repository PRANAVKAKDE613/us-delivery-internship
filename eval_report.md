# AI Solution Evaluation Harness Summary Report

**Total Test Cases**: 10 | **Passed**: 10 | **Pass Rate**: 100.0% | **Average Quality Score**: 1.0/1.0
- **Task 1 (Ticket Triage Agent) Pass Rate**: 100.0%
- **Task 2 (TAM Account Summariser) Pass Rate**: 100.0%

## Detailed Results Table

| Test ID | Task | Test Name | Type | Status | Quality Score | Exec Time (ms) | Details |
|---|---|---|---|---|---|---|---|
| `TC1-01` | Task 1 | P1 SSO Auth Outage with Churn Signal | Standard | ✅ PASS | 1.00 | 5.7ms | Checks passed: area ok, urgency ok, kb match ok, team ok |
| `TC1-02` | Task 1 | API Rate Limits Throttling | Standard | ✅ PASS | 1.00 | 4.77ms | Checks passed: area ok, kb match ok, urgency ok |
| `TC1-03` | Task 1 | Billing Overage Dispute | Standard | ✅ PASS | 1.00 | 13.57ms | Checks passed: area ok, category ok, team ok |
| `TC1-04` | Task 1 | Webhook Gateway Timeout | Standard | ✅ PASS | 1.00 | 3.98ms | Checks passed: area ok, kb match ok, urgency ok |
| `TC1-05-ADV` | Task 1 | Adversarial Ambiguous Multi-topic Ticket | ⚠️ Adversarial | ✅ PASS | 1.00 | 2.68ms | Adversarial checks passed: escalated to P1 ok, kb surfaced ok, draft response valid ok |
| `TC2-01` | Task 2 | Standard Account Health Brief Structure | Standard | ✅ PASS | 1.00 | 7.05ms | Checks passed: sec 1 ok, sec 2 ok, sec 3 ok |
| `TC2-02` | Task 2 | Churn Risk Detection & Direct Quotes | Standard | ✅ PASS | 1.00 | 5.92ms | Checks passed: churn tickets flagged ok, direct quotes included ok |
| `TC2-03` | Task 2 | Executive Summary Sentence Constraint | Standard | ✅ PASS | 1.00 | 6.94ms | Checks passed: exec summary 3-5 sentences ok, account meta ok |
| `TC2-04` | Task 2 | Output Determinism Verification | Standard | ✅ PASS | 1.00 | 27.58ms | Identical markdown outputs verified across 3 consecutive executions |
| `TC2-05-ADV` | Task 2 | Adversarial Minimal Data Account Brief | ⚠️ Adversarial | ✅ PASS | 1.00 | 6.26ms | Adversarial checks passed: handled validly ok, valid markdown output ok |