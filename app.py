import streamlit as st
import json
import time
from src.triage_agent import triage_ticket
from src.tam_summariser import generate_account_brief, TAMSummariserEngine
from src.eval_harness import EvaluationHarness

st.set_page_config(
    page_title="Support & TAM AI Platform",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI Support & TAM Operations Platform")
st.markdown("Production-grade LLM tools for Technical Support Engineers & Technical Account Managers.")

tab1, tab2, tab3 = st.tabs(["🎫 Task 1: Ticket Triage Agent", "📊 Task 2: TAM Account Brief", "🧪 Task 3: Evaluation Harness"])

# --- TAB 1: Ticket Triage Agent ---
with tab1:
    st.header("Task 1 · Intelligent Ticket Triage Agent")
    st.caption("Classify support tickets, surface matching Knowledge Base docs, route to teams, and auto-draft responses.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input Support Ticket")
        sample_ticket_type = st.selectbox(
            "Load Sample Ticket Preset:",
            ["Custom Input", "P1 SAML SSO Failure", "API Rate Limit 429", "Billing Dispute Overage"]
        )
        
        default_subj = ""
        default_body = ""
        
        if sample_ticket_type == "P1 SAML SSO Failure":
            default_subj = "[Authentication] SAML SSO login failing with OAuth_401 error"
            default_body = "Users in our organization are unable to log in via Okta SAML SSO. Error OAuth_401 invalid client credentials. We will cancel if not resolved!"
        elif sample_ticket_type == "API Rate Limit 429":
            default_subj = "HTTP 429 Too Many Requests during batch sync"
            default_body = "Our nightly batch sync pipeline is getting throttled with 429 rate limit errors."
        elif sample_ticket_type == "Billing Dispute Overage":
            default_subj = "Unexpected overage charge on invoice INV-2026-88"
            default_body = "We were charged $2,400 for API overages this month, but our tier includes 500k calls. Please issue refund."
            
        subj_input = st.text_input("Ticket Subject:", value=default_subj)
        body_input = st.text_area("Ticket Body:", value=default_body, height=150)
        
        run_triage = st.button("🚀 Process & Triage Ticket", type="primary")

    with col2:
        st.subheader("Structured Triage Output")
        if run_triage and body_input:
            with st.spinner("Analyzing ticket & querying RAG Knowledge Base..."):
                triage_res = triage_ticket({"subject": subj_input, "body": body_input})
                
            st.success("Triage Complete!")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Urgency", triage_res.urgency)
            c2.metric("Product Area", triage_res.product_area)
            c3.metric("Category", triage_res.issue_category)
            
            st.markdown(f"**Target Responder Team**: `{triage_res.recommended_responder_team}`")
            st.markdown(f"**Urgency Reasoning**: {triage_res.urgency_reasoning}")
            
            if triage_res.matched_kb_doc:
                st.info(f"📄 **Matched KB Article**: `{triage_res.matched_kb_doc}`\n\n{triage_res.kb_relevance_summary}")
            else:
                st.warning("No direct KB article matched.")
                
            st.subheader("Draft First-Response Message")
            st.code(triage_res.draft_response, language="markdown")

# --- TAB 2: TAM Account Health Summariser ---
with tab2:
    st.header("Task 2 · TAM Account Health Summariser")
    st.caption("Generate a deterministic 3-section brief from 90-day ticket history with direct churn quote justifications.")
    
    with open("data/accounts.json", "r", encoding="utf-8") as f:
        accounts_data = json.load(f)
    
    acc_options = {f"{a['account_id']} - {a['company_name']} ({a['tier']})": a['account_id'] for a in accounts_data}
    selected_acc_label = st.selectbox("Select Target Customer Account:", list(acc_options.keys()))
    target_acc_id = acc_options[selected_acc_label]
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Account Metadata")
        acc_info = next(a for a in accounts_data if a["account_id"] == target_acc_id)
        st.write(f"**Company**: {acc_info['company_name']}")
        st.write(f"**Tier**: {acc_info['tier']}")
        st.write(f"**MRR**: ${acc_info['mrr']:,}")
        st.write(f"**TAM**: {acc_info['assigned_tam']}")
        st.write(f"**Health Score**: `{acc_info['health_score']}`")
        st.write(f"**Renewal Date**: {acc_info['contract_end_date']}")
        
        stream_option = st.checkbox("Enable Real-time Token Streaming", value=True)
        generate_btn = st.button("⚡ Generate Account Brief", type="primary")

    with col_b:
        st.subheader("Generated Account Brief")
        if generate_btn:
            if stream_option:
                engine = TAMSummariserEngine()
                placeholder = st.empty()
                full_text = ""
                for token in engine.stream_brief(target_acc_id):
                    full_text += token
                    placeholder.markdown(full_text)
                    time.sleep(0.02)
            else:
                brief = generate_account_brief(target_acc_id)
                st.markdown(brief.formatted_markdown_brief)

# --- TAB 3: Evaluation Harness ---
with tab3:
    st.header("Task 3 · AI Evaluation Harness Dashboard")
    st.caption("Run regression tests and quality gate evaluations across Task 1 and Task 2 test cases.")
    
    if st.button("🧪 Run Full Evaluation Harness Now"):
        with st.spinner("Executing eval harness test suite..."):
            harness = EvaluationHarness()
            report = harness.run_all_evals()
            
        st.success("Evaluation Harness Run Complete!")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overall Pass Rate", f"{report.pass_rate_percentage}%")
        m2.metric("Avg Quality Score", f"{report.average_quality_score}/1.0")
        m3.metric("Task 1 Pass Rate", f"{report.task1_pass_rate}%")
        m4.metric("Task 2 Pass Rate", f"{report.task2_pass_rate}%")
        
        st.subheader("Detailed Evaluation Results")
        res_data = []
        for r in report.results:
            res_data.append({
                "Test ID": r.test_id,
                "Task": r.task,
                "Test Name": r.name,
                "Type": "Adversarial" if r.is_adversarial else "Standard",
                "Status": "PASS" if r.passed else "FAIL",
                "Quality Score": r.quality_score,
                "Exec Time": f"{r.execution_time_ms} ms",
                "Details": r.details
            })
        st.dataframe(res_data, use_container_width=True)
