# agents.py — Multi-agent underwriting system

import os
import json
import uuid
import anthropic
import chromadb
from dotenv import load_dotenv

load_dotenv()

claude     = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
chroma     = chromadb.PersistentClient(path='./underwriting_memory')
collection = chroma.get_or_create_collection('underwriting')

MODEL = "claude-opus-4-5"

# ── Shared memory helpers ─────────────────────────────────────
def save_finding(content: str, topic: str, application_id: str):
    collection.add(
        documents=[content],
        ids=[str(uuid.uuid4())],
        metadatas=[{"topic": topic, "application_id": application_id}]
    )

def get_findings(application_id: str) -> list:
    results = collection.query(
        query_texts=[application_id],
        n_results=10,
        where={"application_id": application_id}
    )
    return results['documents'][0] if results['documents'] else []

def clear_findings(application_id: str):
    results = collection.get(where={"application_id": application_id})
    if results['ids']:
        collection.delete(ids=results['ids'])


# ── Base agent runner ─────────────────────────────────────────
def run_agent(system_prompt: str, user_message: str, log_fn=None) -> str:
    """Run a single agent with a system prompt and return its text response."""
    if log_fn:
        log_fn("thinking", "Analyzing...")

    response = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return next(
        (b.text for b in response.content if hasattr(b, "text")),
        "No analysis generated."
    )


# ── Worker agent 1: Credit ────────────────────────────────────
CREDIT_SYSTEM = """You are a senior credit analyst for a mortgage lender.
Analyze the credit profile of the loan applicant and provide a structured assessment.

Your analysis MUST cover:
1. Credit score evaluation (excellent/good/fair/poor and what it means for this loan)
2. Payment history assessment
3. Debt-to-income ratio analysis (flag if over 43%)
4. Red flags (bankruptcies, foreclosures, collections)
5. Credit age and mix assessment
6. Overall credit recommendation: STRONG / ACCEPTABLE / MARGINAL / UNACCEPTABLE

Be specific with numbers. Format your response with clear sections.
End with: CREDIT VERDICT: [STRONG/ACCEPTABLE/MARGINAL/UNACCEPTABLE] — one sentence reason."""

def run_credit_agent(application_text: str, log_fn=None) -> str:
    if log_fn: log_fn("agent", "🏦 Credit agent analyzing...")
    result = run_agent(CREDIT_SYSTEM, application_text, log_fn)
    return result


# ── Worker agent 2: Income ────────────────────────────────────
INCOME_SYSTEM = """You are a senior income verification analyst for a mortgage lender.
Analyze the income and employment profile of the loan applicant.

Your analysis MUST cover:
1. Income stability assessment (employment type, tenure, consistency)
2. Gross monthly income vs required income for this loan
   - Use the 28% front-end rule: monthly PITI should be ≤28% of gross monthly income
   - Use the 36% back-end rule: all monthly debts should be ≤36% of gross monthly income
   - (Estimate monthly payment at ~0.5% of loan amount if exact rate unknown)
3. Self-employment / 1099 risk factors if applicable
4. Income documentation requirements
5. Overall income recommendation: STRONG / ACCEPTABLE / MARGINAL / UNACCEPTABLE

Be specific with calculations. Show your math.
End with: INCOME VERDICT: [STRONG/ACCEPTABLE/MARGINAL/UNACCEPTABLE] — one sentence reason."""

def run_income_agent(application_text: str, log_fn=None) -> str:
    if log_fn: log_fn("agent", "💰 Income agent analyzing...")
    result = run_agent(INCOME_SYSTEM, application_text, log_fn)
    return result


# ── Worker agent 3: Property ──────────────────────────────────
PROPERTY_SYSTEM = """You are a senior property and collateral analyst for a mortgage lender.
Analyze the property details for the loan application.

Your analysis MUST cover:
1. Loan-to-value (LTV) ratio assessment
   - Conventional: 80% LTV or below is ideal, above 80% requires PMI, above 97% is usually declined
   - VA loans: 100% LTV is acceptable
   - FHA: up to 96.5% LTV acceptable
2. Property type risk assessment (SFH is lowest risk, condos and multi-family have specific rules)
3. Appraisal vs purchase price comparison
4. Property age and condition concerns
5. Flood zone risk if applicable (requires flood insurance, increases cost)
6. Overall property recommendation: STRONG / ACCEPTABLE / MARGINAL / UNACCEPTABLE

End with: PROPERTY VERDICT: [STRONG/ACCEPTABLE/MARGINAL/UNACCEPTABLE] — one sentence reason."""

def run_property_agent(application_text: str, log_fn=None) -> str:
    if log_fn: log_fn("agent", "🏠 Property agent analyzing...")
    result = run_agent(PROPERTY_SYSTEM, application_text, log_fn)
    return result


# ── Worker agent 4: Risk ──────────────────────────────────────
RISK_SYSTEM = """You are a senior risk officer for a mortgage lender.
Perform a holistic risk assessment of this loan application.

Your analysis MUST cover:
1. Compensating factors (strong assets, low LTV, high income, excellent credit — things that reduce risk)
2. Risk amplifiers (multiple weak areas appearing together)
3. Layered risk assessment (when multiple marginal factors combine, risk multiplies)
4. Market and property risk (location, flood zone, property type)
5. Loan type specific risks (ARM vs fixed, VA/FHA vs conventional)
6. Overall risk score: LOW / MODERATE / HIGH / VERY HIGH

Be direct. If this application has serious problems, say so clearly.
End with: RISK VERDICT: [LOW/MODERATE/HIGH/VERY HIGH] — one sentence reason."""

def run_risk_agent(application_text: str, log_fn=None) -> str:
    if log_fn: log_fn("agent", "⚠️ Risk agent analyzing...")
    result = run_agent(RISK_SYSTEM, application_text, log_fn)
    return result


# ── Worker agent 5: Compliance ────────────────────────────────
COMPLIANCE_SYSTEM = """You are a mortgage compliance officer.
Review this loan application for regulatory and guideline compliance.

Your analysis MUST cover:
1. Ability-to-Repay (ATR) rule compliance — can the borrower realistically repay?
2. Qualified Mortgage (QM) standards — does this meet standard QM criteria?
3. Fair lending considerations — is there anything unusual requiring documentation?
4. VA loan specific requirements (if applicable) — COE, entitlement, occupancy
5. FHA loan specific requirements (if applicable) — MIP, property standards
6. Documentation requirements — what must be collected before closing?
7. Any regulatory red flags

End with: COMPLIANCE VERDICT: [CLEAR/REVIEW NEEDED/RED FLAG] — one sentence reason."""

def run_compliance_agent(application_text: str, log_fn=None) -> str:
    if log_fn: log_fn("agent", "📋 Compliance agent analyzing...")
    result = run_agent(COMPLIANCE_SYSTEM, application_text, log_fn)
    return result


# ── Supervisor agent ──────────────────────────────────────────
SUPERVISOR_SYSTEM = """You are the Chief Underwriting Officer at Veterans United Home Loans.
You have received reports from 5 specialist analysts. Your job is to synthesize their findings
and make a final underwriting decision.

Your final report MUST follow this exact structure:

## Underwriting Decision Report

**Application ID:** [ID]
**Applicant:** [Name]
**Loan Amount:** [Amount]

---

### Executive Summary
2-3 sentences summarizing the overall profile and decision rationale.

---

### Agent Findings Summary
Brief 1-2 sentence summary of each agent's verdict:
- **Credit:** [verdict + key reason]
- **Income:** [verdict + key reason]  
- **Property:** [verdict + key reason]
- **Risk:** [verdict + key reason]
- **Compliance:** [verdict + key reason]

---

### Key Strengths
Bullet points of positive factors supporting approval.

### Key Concerns
Bullet points of risk factors or issues found.

---

### Conditions (if any)
List any conditions that must be met before closing (documentation, explanations, etc.)

---

### ✅ FINAL DECISION: [APPROVE / APPROVE WITH CONDITIONS / MANUAL REVIEW / DECLINE]

**Decision rationale:** 2-3 sentences explaining the final decision clearly.

**If APPROVE:** State the approved loan amount and any conditions.
**If MANUAL REVIEW:** Explain exactly what needs human review and why.
**If DECLINE:** State the specific reasons for decline clearly and respectfully.

---
Be decisive. Use clear language. This report may be shown to the loan officer."""

def run_supervisor(application_text: str, agent_reports: dict, log_fn=None) -> str:
    if log_fn: log_fn("supervisor", "🎯 Supervisor synthesizing final decision...")

    combined = f"""ORIGINAL APPLICATION:
{application_text}

{'='*50}
SPECIALIST AGENT REPORTS:
{'='*50}

CREDIT ANALYST REPORT:
{agent_reports['credit']}

{'='*50}
INCOME ANALYST REPORT:
{agent_reports['income']}

{'='*50}
PROPERTY ANALYST REPORT:
{agent_reports['property']}

{'='*50}
RISK OFFICER REPORT:
{agent_reports['risk']}

{'='*50}
COMPLIANCE OFFICER REPORT:
{agent_reports['compliance']}
"""

    return run_agent(SUPERVISOR_SYSTEM, combined, log_fn)


# ── Main orchestrator ─────────────────────────────────────────
def run_underwriting_pipeline(application: dict, application_text: str, log_queue=None) -> dict:
    """
    Run all 5 worker agents sequentially, save to memory,
    then run supervisor for final decision.
    Returns dict with all reports and final decision.
    """

    def log(msg_type, msg):
        if log_queue:
            log_queue.put((msg_type, msg))

    app_id = application.get("id", "UNKNOWN")
    clear_findings(app_id)

    reports = {}

    # ── Run each worker agent ─────────────────────────────────
    log("progress", "Step 1/6 — Credit analysis")
    reports['credit'] = run_credit_agent(application_text, log)
    save_finding(reports['credit'], "credit_analysis", app_id)

    log("progress", "Step 2/6 — Income analysis")
    reports['income'] = run_income_agent(application_text, log)
    save_finding(reports['income'], "income_analysis", app_id)

    log("progress", "Step 3/6 — Property analysis")
    reports['property'] = run_property_agent(application_text, log)
    save_finding(reports['property'], "property_analysis", app_id)

    log("progress", "Step 4/6 — Risk assessment")
    reports['risk'] = run_risk_agent(application_text, log)
    save_finding(reports['risk'], "risk_assessment", app_id)

    log("progress", "Step 5/6 — Compliance check")
    reports['compliance'] = run_compliance_agent(application_text, log)
    save_finding(reports['compliance'], "compliance_check", app_id)

    # ── Run supervisor ────────────────────────────────────────
    log("progress", "Step 6/6 — Supervisor making final decision")
    reports['final'] = run_supervisor(application_text, reports, log)
    save_finding(reports['final'], "final_decision", app_id)

    log("done", reports['final'])
    return reports
