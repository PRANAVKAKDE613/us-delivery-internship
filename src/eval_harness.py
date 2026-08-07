import os
import json
import time
from typing import Dict, Any, List
from pydantic import BaseModel
from src.triage_agent import triage_ticket, TriageResult
from src.tam_summariser import generate_account_brief, TAMAccountBrief

class TestResult(BaseModel):
    test_id: str
    task: str
    name: str
    is_adversarial: bool
    passed: bool
    quality_score: float  # 0.0 to 1.0
    details: str
    execution_time_ms: float

class EvalSummaryReport(BaseModel):
    total_tests: int
    total_passed: int
    pass_rate_percentage: float
    average_quality_score: float
    task1_pass_rate: float
    task2_pass_rate: float
    results: List[TestResult]

class EvaluationHarness:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def run_all_evals(self) -> EvalSummaryReport:
        results = []

        # --- Task 1 Test Cases ---
        results.append(self._eval_t1_p1_sso_outage())
        results.append(self._eval_t1_rate_limit())
        results.append(self._eval_t1_billing_dispute())
        results.append(self._eval_t1_webhook_timeout())
        results.append(self._eval_t1_adversarial_ambiguous())

        # --- Task 2 Test Cases ---
        results.append(self._eval_t2_standard_account())
        results.append(self._eval_t2_churn_risk_detection())
        results.append(self._eval_t2_healthy_account())
        results.append(self._eval_t2_determinism_verification())
        results.append(self._eval_t2_adversarial_incomplete_data())

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        avg_score = round(sum(r.quality_score for r in results) / total, 3) if total > 0 else 0.0

        t1_results = [r for r in results if r.task == "Task 1"]
        t2_results = [r for r in results if r.task == "Task 2"]

        t1_pass = (sum(1 for r in t1_results if r.passed) / len(t1_results)) * 100 if t1_results else 0.0
        t2_pass = (sum(1 for r in t2_results if r.passed) / len(t2_results)) * 100 if t2_results else 0.0

        report = EvalSummaryReport(
            total_tests=total,
            total_passed=passed,
            pass_rate_percentage=round((passed / total) * 100, 1),
            average_quality_score=avg_score,
            task1_pass_rate=round(t1_pass, 1),
            task2_pass_rate=round(t2_pass, 1),
            results=results
        )

        self._save_reports(report)
        return report

    # --- Task 1 Evaluators ---
    def _eval_t1_p1_sso_outage(self) -> TestResult:
        t0 = time.time()
        ticket = {
            "subject": "CRITICAL: SAML SSO Login down with OAuth_401 error",
            "body": "Okta SSO is failing across our entire company. Users get OAuth_401 invalid credentials. We will cancel our contract immediately if not resolved!"
        }
        res = triage_ticket(ticket, kb_dir=os.path.join(self.data_dir, "knowledge_base"))
        
        score = 0.0
        checks = []
        if res.product_area == "Authentication": score += 0.25; checks.append("area ok")
        if res.urgency == "P1": score += 0.25; checks.append("urgency ok")
        if res.matched_kb_doc == "auth_sso.md": score += 0.25; checks.append("kb match ok")
        if "Strategic TAM Escalation" in res.recommended_responder_team or "Auth Support" in res.recommended_responder_team: score += 0.25; checks.append("team ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC1-01",
            task="Task 1",
            name="P1 SSO Auth Outage with Churn Signal",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t1_rate_limit(self) -> TestResult:
        t0 = time.time()
        ticket = {
            "subject": "HTTP 429 Too Many Requests during daily data import",
            "body": "Our batch integration pipeline is receiving HTTP 429 rate limit errors. Please advise."
        }
        res = triage_ticket(ticket, kb_dir=os.path.join(self.data_dir, "knowledge_base"))
        
        score = 0.0
        checks = []
        if res.product_area == "API Integrations": score += 0.35; checks.append("area ok")
        if res.matched_kb_doc == "api_rate_limits.md": score += 0.35; checks.append("kb match ok")
        if res.urgency in ["P1", "P2", "P3"]: score += 0.30; checks.append("urgency ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC1-02",
            task="Task 1",
            name="API Rate Limits Throttling",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t1_billing_dispute(self) -> TestResult:
        t0 = time.time()
        ticket = {
            "subject": "Invoice overage inquiry for INV-2026-99",
            "body": "We received an unexpected overage charge of $1,500 on our invoice. We request a refund review."
        }
        res = triage_ticket(ticket, kb_dir=os.path.join(self.data_dir, "knowledge_base"))
        
        score = 0.0
        checks = []
        if res.product_area == "Billing & Plans": score += 0.35; checks.append("area ok")
        if res.issue_category in ["Billing Dispute", "Bug Report"]: score += 0.35; checks.append("category ok")
        if "Billing" in res.recommended_responder_team or "Support" in res.recommended_responder_team: score += 0.30; checks.append("team ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC1-03",
            task="Task 1",
            name="Billing Overage Dispute",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t1_webhook_timeout(self) -> TestResult:
        t0 = time.time()
        ticket = {
            "subject": "Webhook 504 Gateway Timeout on payment events",
            "body": "Webhook deliveries are failing with 504 gateway timeout and signature verification errors."
        }
        res = triage_ticket(ticket, kb_dir=os.path.join(self.data_dir, "knowledge_base"))
        
        score = 0.0
        checks = []
        if res.product_area == "Webhooks": score += 0.35; checks.append("area ok")
        if res.matched_kb_doc == "webhook_deliveries.md": score += 0.35; checks.append("kb match ok")
        if res.urgency in ["P1", "P2"]: score += 0.30; checks.append("urgency ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC1-04",
            task="Task 1",
            name="Webhook Gateway Timeout",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t1_adversarial_ambiguous(self) -> TestResult:
        t0 = time.time()
        ticket = {
            "subject": "HELP!! EVERYTHING IS BROKEN",
            "body": "Database sync lag is high but also login SSO failing and we want refund for API overages. Fix ASAP or we switch to competitor!"
        }
        res = triage_ticket(ticket, kb_dir=os.path.join(self.data_dir, "knowledge_base"))
        
        score = 0.0
        checks = []
        if res.urgency == "P1": score += 0.40; checks.append("escalated to P1 ok")
        if res.matched_kb_doc is not None: score += 0.30; checks.append("kb surfaced ok")
        if len(res.draft_response) > 50: score += 0.30; checks.append("draft response valid ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC1-05-ADV",
            task="Task 1",
            name="Adversarial Ambiguous Multi-topic Ticket",
            is_adversarial=True,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Adversarial checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    # --- Task 2 Evaluators ---
    def _eval_t2_standard_account(self) -> TestResult:
        t0 = time.time()
        brief = generate_account_brief("ACC-001", data_dir=self.data_dir)
        
        score = 0.0
        checks = []
        if "### 1. Executive Summary" in brief.formatted_markdown_brief: score += 0.33; checks.append("sec 1 ok")
        if "### 2. Open Risks & Flagged Issues" in brief.formatted_markdown_brief: score += 0.33; checks.append("sec 2 ok")
        if "### 3. Recommended Talking Points for TAM" in brief.formatted_markdown_brief: score += 0.34; checks.append("sec 3 ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC2-01",
            task="Task 2",
            name="Standard Account Health Brief Structure",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t2_churn_risk_detection(self) -> TestResult:
        t0 = time.time()
        brief = generate_account_brief("ACC-001", data_dir=self.data_dir)
        
        score = 0.0
        checks = []
        if brief.flagged_churn_tickets > 0: score += 0.50; checks.append("churn tickets flagged ok")
        if any("direct_quote" in r and r["direct_quote"] for r in brief.open_risks_and_flagged_issues): score += 0.50; checks.append("direct quotes included ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC2-02",
            task="Task 2",
            name="Churn Risk Detection & Direct Quotes",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t2_healthy_account(self) -> TestResult:
        t0 = time.time()
        brief = generate_account_brief("ACC-005", data_dir=self.data_dir)
        
        score = 0.0
        checks = []
        sentences = [s for s in brief.executive_summary.split(".") if s.strip()]
        if 3 <= len(sentences) <= 5: score += 0.50; checks.append("exec summary 3-5 sentences ok")
        if brief.company_name != "": score += 0.50; checks.append("account meta ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC2-03",
            task="Task 2",
            name="Executive Summary Sentence Constraint",
            is_adversarial=False,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t2_determinism_verification(self) -> TestResult:
        t0 = time.time()
        run1 = generate_account_brief("ACC-002", data_dir=self.data_dir).formatted_markdown_brief
        run2 = generate_account_brief("ACC-002", data_dir=self.data_dir).formatted_markdown_brief
        run3 = generate_account_brief("ACC-002", data_dir=self.data_dir).formatted_markdown_brief
        
        is_identical = (run1 == run2 == run3)
        score = 1.0 if is_identical else 0.0

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC2-04",
            task="Task 2",
            name="Output Determinism Verification",
            is_adversarial=False,
            passed=is_identical,
            quality_score=score,
            details="Identical markdown outputs verified across 3 consecutive executions" if is_identical else "Outputs differed across runs",
            execution_time_ms=round(dt, 2)
        )

    def _eval_t2_adversarial_incomplete_data(self) -> TestResult:
        t0 = time.time()
        brief = generate_account_brief("ACC-050", data_dir=self.data_dir)
        
        score = 0.0
        checks = []
        if brief.account_id == "ACC-050": score += 0.50; checks.append("handled validly ok")
        if len(brief.formatted_markdown_brief) > 100: score += 0.50; checks.append("valid markdown output ok")

        dt = (time.time() - t0) * 1000
        return TestResult(
            test_id="TC2-05-ADV",
            task="Task 2",
            name="Adversarial Minimal Data Account Brief",
            is_adversarial=True,
            passed=score >= 0.8,
            quality_score=score,
            details=f"Adversarial checks passed: {', '.join(checks)}",
            execution_time_ms=round(dt, 2)
        )

    def _save_reports(self, report: EvalSummaryReport):
        with open("eval_report.json", "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

        md_lines = [
            "# AI Solution Evaluation Harness Summary Report",
            "",
            f"**Total Test Cases**: {report.total_tests} | **Passed**: {report.total_passed} | **Pass Rate**: {report.pass_rate_percentage}% | **Average Quality Score**: {report.average_quality_score}/1.0",
            f"- **Task 1 (Ticket Triage Agent) Pass Rate**: {report.task1_pass_rate}%",
            f"- **Task 2 (TAM Account Summariser) Pass Rate**: {report.task2_pass_rate}%",
            "",
            "## Detailed Results Table",
            "",
            "| Test ID | Task | Test Name | Type | Status | Quality Score | Exec Time (ms) | Details |",
            "|---|---|---|---|---|---|---|---|"
        ]

        for r in report.results:
            status_str = "✅ PASS" if r.passed else "❌ FAIL"
            type_str = "⚠️ Adversarial" if r.is_adversarial else "Standard"
            md_lines.append(f"| `{r.test_id}` | {r.task} | {r.name} | {type_str} | {status_str} | {r.quality_score:.2f} | {r.execution_time_ms}ms | {r.details} |")

        with open("eval_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

if __name__ == "__main__":
    harness = EvaluationHarness()
    rep = harness.run_all_evals()
    print(f"Eval Run Complete! Pass Rate: {rep.pass_rate_percentage}% | Avg Quality: {rep.average_quality_score}")
