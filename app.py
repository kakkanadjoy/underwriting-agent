# app.py — Streamlit UI for the Multi-Agent Underwriting System

import os, queue, threading
import streamlit as st
from dotenv import load_dotenv
from data import SAMPLE_APPLICATIONS, generate_random_application, format_application_for_agent
from agents import run_underwriting_pipeline

load_dotenv()

# ── ENV validation ────────────────────────────────────────────
def validate_env():
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        st.set_page_config(page_title="⚠️ Setup Required", page_icon="⚠️")
        st.error("## ⚠️ Missing ANTHROPIC_API_KEY")
        st.markdown("Create a `.env` file with:")
        st.code("ANTHROPIC_API_KEY=sk-ant-your-key-here")
        st.stop()

validate_env()

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Underwriting System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Underwriting System")
st.caption("Multi-agent loan analysis powered by Claude | Credit • Income • Property • Risk • Compliance")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ How It Works")
    st.markdown("""
    **5 specialist AI agents analyze every application:**
    
    1. 🏦 **Credit Agent** — score, history, DTI  
    2. 💰 **Income Agent** — employment, ratios  
    3. 🏠 **Property Agent** — LTV, condition  
    4. ⚠️ **Risk Agent** — holistic risk score  
    5. 📋 **Compliance Agent** — regulatory check  
    6. 🎯 **Supervisor** — final decision  
    """)
    st.divider()
    st.success("✅ API key loaded")
    st.markdown("**Powered by:** Claude claude-opus-4-5")

# ── Tabs ──────────────────────────────────────────────────────
tab_samples, tab_random, tab_form = st.tabs([
    "📋 Sample Applications",
    "🎲 Random Generator",
    "✏️ Manual Entry"
])

selected_application = None

# ══════════════════════════════════════════════════════════════
# TAB 1 — Sample Applications
# ══════════════════════════════════════════════════════════════
with tab_samples:
    st.subheader("Pre-built sample applications")
    st.caption("Each sample is designed to test a different underwriting scenario.")

    cols = st.columns(2)
    for i, sample in enumerate(SAMPLE_APPLICATIONS):
        col = cols[i % 2]
        with col:
            with st.container(border=True):
                st.markdown(f"**{sample['label']}**")
                a = sample['applicant']
                c = sample['credit']
                l = sample['loan']
                st.markdown(f"""
                - 👤 {a['name']} | Age {a['age']} | {a['employment_status']}  
                - 💵 Income: ${a['annual_income']:,}/yr  
                - 📊 Credit: {c['credit_score']} | DTI: {round(c['monthly_debt_payments']/a['monthly_income']*100,1)}%  
                - 🏠 Loan: ${l['loan_amount']:,} ({l['loan_type']})
                """)
                if st.button(f"Analyze this application", key=f"sample_{i}", use_container_width=True):
                    st.session_state.selected_app = sample
                    st.session_state.source = "sample"

# ══════════════════════════════════════════════════════════════
# TAB 2 — Random Generator
# ══════════════════════════════════════════════════════════════
with tab_random:
    st.subheader("Generate a random applicant")
    st.caption("Uses Faker to create a realistic random loan application instantly.")

    if st.button("🎲 Generate Random Application", type="primary", use_container_width=True):
        st.session_state.random_app = generate_random_application()

    if "random_app" in st.session_state:
        app = st.session_state.random_app
        a, c, l, p = app['applicant'], app['credit'], app['loan'], app['property']

        st.success(f"Generated: **{a['name']}**")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Credit Score", c['credit_score'])
            st.metric("Annual Income", f"${a['annual_income']:,}")
        with col2:
            st.metric("Loan Amount", f"${l['loan_amount']:,}")
            st.metric("Down Payment", f"${l['down_payment']:,}")
        with col3:
            dti = round(c['monthly_debt_payments'] / a['monthly_income'] * 100, 1) if a['monthly_income'] > 0 else 0
            ltv = round(l['loan_amount'] / p['appraised_value'] * 100, 1) if p['appraised_value'] > 0 else 0
            st.metric("DTI Ratio", f"{dti}%")
            st.metric("LTV Ratio", f"{ltv}%")

        st.markdown(f"**Property:** {p['address']} | {p['type']} | {p['condition']}")
        st.markdown(f"**Employment:** {a['years_employed']} yrs at {a['employer']} ({a['employment_status']})")

        if st.button("🏦 Analyze This Applicant", type="primary", use_container_width=True):
            st.session_state.selected_app = st.session_state.random_app
            st.session_state.source = "random"

# ══════════════════════════════════════════════════════════════
# TAB 3 — Manual Form
# ══════════════════════════════════════════════════════════════
with tab_form:
    st.subheader("Enter applicant details manually")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👤 Applicant Info**")
        f_name           = st.text_input("Full name", value="Jane Smith")
        f_age            = st.number_input("Age", 18, 90, 35)
        f_employment     = st.selectbox("Employment status", [
            "Full-time employed", "Part-time employed", "Self-employed", "Contract worker", "Retired"
        ])
        f_employer       = st.text_input("Employer / company", value="Acme Corp")
        f_years_employed = st.number_input("Years employed", 0.0, 40.0, 3.0, step=0.5)
        f_annual_income  = st.number_input("Annual income ($)", 0, 1000000, 80000, step=1000)
        f_other_income   = st.number_input("Other monthly income ($)", 0, 20000, 0, step=100)

        st.markdown("**📊 Credit Profile**")
        f_credit_score   = st.slider("Credit score", 300, 850, 700)
        f_payment_hist   = st.selectbox("Payment history", [
            "No missed payments in 5+ years",
            "1 late payment 18 months ago",
            "2 late payments in last 24 months",
            "Multiple missed payments",
        ])
        f_total_debt     = st.number_input("Total existing debt ($)", 0, 500000, 15000, step=500)
        f_monthly_debt   = st.number_input("Monthly debt payments ($)", 0, 10000, 400, step=50)
        f_bankruptcies   = st.number_input("Bankruptcies", 0, 5, 0)
        f_foreclosures   = st.number_input("Foreclosures", 0, 5, 0)

    with col2:
        st.markdown("**🏦 Loan Request**")
        f_loan_amount    = st.number_input("Loan amount ($)", 50000, 2000000, 280000, step=5000)
        f_loan_type      = st.selectbox("Loan type", [
            "30-year fixed", "15-year fixed", "5/1 ARM",
            "VA 30-year fixed", "FHA 30-year fixed"
        ])
        f_down_payment   = st.number_input("Down payment ($)", 0, 500000, 35000, step=1000)
        f_purchase_price = st.number_input("Purchase price ($)", 50000, 2000000, 315000, step=5000)
        f_purpose        = st.selectbox("Loan purpose", [
            "Primary residence purchase",
            "Investment property",
            "Second home / vacation property",
            "Rate-and-term refinance",
        ])

        st.markdown("**🏠 Property**")
        f_address        = st.text_input("Property address", value="123 Main St, Springfield, MO")
        f_prop_type      = st.selectbox("Property type", [
            "Single-family home", "Condominium", "Townhouse", "Multi-family (2-4 units)"
        ])
        f_appraised      = st.number_input("Appraised value ($)", 50000, 2000000, 320000, step=5000)
        f_year_built     = st.number_input("Year built", 1900, 2024, 2005)
        f_condition      = st.selectbox("Property condition", [
            "Excellent", "Very good", "Good", "Fair — needs repairs", "Poor"
        ])
        f_flood_zone     = st.checkbox("In a flood zone?")

    if st.button("🏦 Analyze This Application", type="primary", use_container_width=True):
        manual_app = {
            "id": f"MANUAL-{f_name.replace(' ', '').upper()[:8]}",
            "label": "✏️ Manual entry",
            "applicant": {
                "name": f_name, "age": f_age,
                "employment_status": f_employment, "employer": f_employer,
                "years_employed": f_years_employed,
                "annual_income": f_annual_income,
                "monthly_income": round(f_annual_income / 12),
                "other_income": f_other_income,
                "income_source": "Salary",
            },
            "credit": {
                "credit_score": f_credit_score,
                "payment_history": f_payment_hist,
                "total_debt": f_total_debt,
                "monthly_debt_payments": f_monthly_debt,
                "bankruptcies": f_bankruptcies,
                "foreclosures": f_foreclosures,
                "open_accounts": 5,
                "credit_age_years": 8,
            },
            "loan": {
                "loan_amount": f_loan_amount,
                "loan_type": f_loan_type,
                "down_payment": f_down_payment,
                "purchase_price": f_purchase_price,
                "purpose": f_purpose,
            },
            "property": {
                "address": f_address,
                "type": f_prop_type,
                "appraised_value": f_appraised,
                "year_built": f_year_built,
                "condition": f_condition,
                "flood_zone": f_flood_zone,
            },
        }
        st.session_state.selected_app = manual_app
        st.session_state.source = "form"

# ══════════════════════════════════════════════════════════════
# Analysis Runner
# ══════════════════════════════════════════════════════════════
if "selected_app" in st.session_state:
    app = st.session_state.selected_app
    application_text = format_application_for_agent(app)

    st.divider()
    st.subheader(f"🔄 Analyzing: {app['applicant']['name']} — {app['label']}")

    with st.expander("📄 View raw application data"):
        st.code(application_text)

    log_queue = queue.Queue()
    logs      = []
    results   = {}

    def run_in_thread():
        try:
            result = run_underwriting_pipeline(app, application_text, log_queue)
            results.update(result)
        except Exception as e:
            log_queue.put(("error", str(e)))
            log_queue.put(("done", f"__ERROR__:{str(e)}"))

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()

    # Progress display
    progress_bar    = st.progress(0)
    status_text     = st.empty()
    log_placeholder = st.empty()

    step_map = {
        "Step 1/6": 0.15, "Step 2/6": 0.30,
        "Step 3/6": 0.45, "Step 4/6": 0.60,
        "Step 5/6": 0.75, "Step 6/6": 0.90,
    }
    agent_icons = {
        "agent": "🤖", "progress": "⚙️",
        "supervisor": "🎯", "thinking": "💭", "error": "❌"
    }

    final_report = None
    error_msg    = None

    import time
    while thread.is_alive() or not log_queue.empty():
        while not log_queue.empty():
            msg_type, msg = log_queue.get()
            if msg_type == "done":
                if msg.startswith("__ERROR__:"):
                    error_msg = msg[len("__ERROR__:"):]
                else:
                    final_report = msg
            else:
                icon = agent_icons.get(msg_type, "⚙️")
                logs.append(f"{icon} {msg}")
                for key, pct in step_map.items():
                    if key in msg:
                        progress_bar.progress(pct)
                        status_text.info(f"⏳ {msg}")

        if logs:
            log_placeholder.code("\n".join(logs[-8:]))
        time.sleep(0.3)

    progress_bar.progress(1.0)
    log_placeholder.empty()

    # ── Display results ───────────────────────────────────────
    if error_msg:
        st.error(f"### ❌ Error\n{error_msg}")

    elif final_report:
        status_text.success("✅ Underwriting complete!")

        # Determine decision color
        decision_color = "blue"
        if "APPROVE" in final_report.upper() and "CONDITIONS" not in final_report.upper() and "MANUAL" not in final_report.upper():
            decision_color = "green"
        elif "DECLINE" in final_report.upper():
            decision_color = "red"
        elif "MANUAL" in final_report.upper():
            decision_color = "orange"

        # Final report
        st.markdown("---")
        st.subheader("📄 Final Underwriting Report")
        st.markdown(final_report)

        st.divider()

        # Individual agent reports in expandable sections
        st.subheader("🔍 Individual Agent Reports")
        agent_labels = {
            "credit":     "🏦 Credit Analyst Report",
            "income":     "💰 Income Analyst Report",
            "property":   "🏠 Property Analyst Report",
            "risk":       "⚠️ Risk Officer Report",
            "compliance": "📋 Compliance Officer Report",
        }
        for key, label in agent_labels.items():
            if key in results:
                with st.expander(label):
                    st.markdown(results[key])

        st.divider()

        # Download button
        full_report = f"""UNDERWRITING REPORT
Application: {app['id']}
Applicant: {app['applicant']['name']}
{'='*60}

FINAL DECISION REPORT:
{final_report}

{'='*60}
INDIVIDUAL AGENT REPORTS:
{'='*60}

""" + "\n\n".join([f"{label}:\n{results.get(key,'')}"
                   for key, label in agent_labels.items()])

        st.download_button(
            label="⬇️ Download Full Report",
            data=full_report,
            file_name=f"underwriting_{app['id']}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Clear selected app after display
    del st.session_state["selected_app"]
