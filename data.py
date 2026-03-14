# data.py — Sample loan applications + Faker generator

from faker import Faker
import random

fake = Faker()

# ── 5 pre-built realistic sample applications ─────────────────
SAMPLE_APPLICATIONS = [
    {
        "id": "SAMPLE-001",
        "label": "✅ Strong applicant — likely approve",
        "applicant": {
            "name": "Michael Johnson",
            "age": 42,
            "employment_status": "Full-time employed",
            "employer": "Boeing Corporation",
            "years_employed": 12,
            "annual_income": 145000,
            "monthly_income": 12083,
            "other_income": 2000,
            "income_source": "Salary + rental income",
        },
        "credit": {
            "credit_score": 768,
            "payment_history": "No missed payments in 8 years",
            "total_debt": 22000,
            "monthly_debt_payments": 850,
            "bankruptcies": 0,
            "foreclosures": 0,
            "open_accounts": 6,
            "credit_age_years": 18,
        },
        "loan": {
            "loan_amount": 380000,
            "loan_type": "30-year fixed",
            "down_payment": 95000,
            "purchase_price": 475000,
            "purpose": "Primary residence purchase",
        },
        "property": {
            "address": "1842 Elmwood Drive, St. Louis, MO 63101",
            "type": "Single-family home",
            "appraised_value": 482000,
            "year_built": 1998,
            "condition": "Excellent",
            "flood_zone": False,
        },
    },
    {
        "id": "SAMPLE-002",
        "label": "⚠️ Edge case — likely manual review",
        "applicant": {
            "name": "Sarah Chen",
            "age": 29,
            "employment_status": "Self-employed",
            "employer": "Freelance Graphic Designer",
            "years_employed": 2.5,
            "annual_income": 78000,
            "monthly_income": 6500,
            "other_income": 0,
            "income_source": "1099 / self-employment",
        },
        "credit": {
            "credit_score": 694,
            "payment_history": "2 late payments in last 24 months",
            "total_debt": 38000,
            "monthly_debt_payments": 1200,
            "bankruptcies": 0,
            "foreclosures": 0,
            "open_accounts": 9,
            "credit_age_years": 7,
        },
        "loan": {
            "loan_amount": 260000,
            "loan_type": "30-year fixed",
            "down_payment": 28000,
            "purchase_price": 288000,
            "purpose": "Primary residence purchase",
        },
        "property": {
            "address": "504 Birchwood Lane, Nashville, TN 37201",
            "type": "Condominium",
            "appraised_value": 291000,
            "year_built": 2005,
            "condition": "Good",
            "flood_zone": False,
        },
    },
    {
        "id": "SAMPLE-003",
        "label": "❌ High risk — likely decline",
        "applicant": {
            "name": "David Martinez",
            "age": 35,
            "employment_status": "Part-time employed",
            "employer": "Retail Store (part-time)",
            "years_employed": 0.8,
            "annual_income": 31000,
            "monthly_income": 2583,
            "other_income": 0,
            "income_source": "Part-time wages",
        },
        "credit": {
            "credit_score": 541,
            "payment_history": "Multiple missed payments, 1 collection account",
            "total_debt": 62000,
            "monthly_debt_payments": 1800,
            "bankruptcies": 1,
            "foreclosures": 0,
            "open_accounts": 12,
            "credit_age_years": 10,
        },
        "loan": {
            "loan_amount": 220000,
            "loan_type": "30-year fixed",
            "down_payment": 8000,
            "purchase_price": 228000,
            "purpose": "Primary residence purchase",
        },
        "property": {
            "address": "89 Maple Street, Detroit, MI 48201",
            "type": "Single-family home",
            "appraised_value": 215000,
            "year_built": 1962,
            "condition": "Fair — needs repairs",
            "flood_zone": True,
        },
    },
    {
        "id": "SAMPLE-004",
        "label": "🎖️ Veteran — VA loan application",
        "applicant": {
            "name": "James O'Brien",
            "age": 38,
            "employment_status": "Full-time employed",
            "employer": "U.S. Department of Veterans Affairs",
            "years_employed": 6,
            "annual_income": 95000,
            "monthly_income": 7917,
            "other_income": 1800,
            "income_source": "Salary + VA disability benefit",
        },
        "credit": {
            "credit_score": 724,
            "payment_history": "Clean — no missed payments in 5 years",
            "total_debt": 14000,
            "monthly_debt_payments": 420,
            "bankruptcies": 0,
            "foreclosures": 0,
            "open_accounts": 4,
            "credit_age_years": 14,
        },
        "loan": {
            "loan_amount": 340000,
            "loan_type": "VA 30-year fixed",
            "down_payment": 0,
            "purchase_price": 340000,
            "purpose": "Primary residence — VA loan (no down payment)",
        },
        "property": {
            "address": "2210 Liberty Ave, Columbia, MO 65201",
            "type": "Single-family home",
            "appraised_value": 345000,
            "year_built": 2010,
            "condition": "Very good",
            "flood_zone": False,
        },
    },
    {
        "id": "SAMPLE-005",
        "label": "🏠 Refinance application",
        "applicant": {
            "name": "Patricia Williams",
            "age": 55,
            "employment_status": "Full-time employed",
            "employer": "St. Louis Public Schools",
            "years_employed": 22,
            "annual_income": 72000,
            "monthly_income": 6000,
            "other_income": 500,
            "income_source": "Salary + part-time tutoring",
        },
        "credit": {
            "credit_score": 741,
            "payment_history": "Excellent — no issues in 10+ years",
            "total_debt": 8500,
            "monthly_debt_payments": 290,
            "bankruptcies": 0,
            "foreclosures": 0,
            "open_accounts": 3,
            "credit_age_years": 28,
        },
        "loan": {
            "loan_amount": 155000,
            "loan_type": "15-year fixed refinance",
            "down_payment": 0,
            "purchase_price": 0,
            "purpose": "Rate-and-term refinance — lower monthly payment",
        },
        "property": {
            "address": "731 Oak Park Blvd, Kansas City, MO 64101",
            "type": "Single-family home",
            "appraised_value": 248000,
            "year_built": 1985,
            "condition": "Good",
            "flood_zone": False,
        },
    },
]


# ── Faker-based random application generator ──────────────────
def generate_random_application():
    """Generate a realistic random loan application using Faker."""
    credit_score    = random.randint(520, 820)
    annual_income   = random.randint(35000, 180000)
    monthly_income  = round(annual_income / 12)
    purchase_price  = random.randint(150000, 750000)
    down_pct        = random.choice([0.03, 0.05, 0.10, 0.15, 0.20])
    down_payment    = int(purchase_price * down_pct)
    loan_amount     = purchase_price - down_payment
    total_debt      = random.randint(0, 80000)
    monthly_debt    = int(total_debt / random.randint(24, 60))
    years_employed  = round(random.uniform(0.5, 20), 1)
    appraised_value = int(purchase_price * random.uniform(0.95, 1.08))

    return {
        "id": f"RAND-{fake.bothify('???-####').upper()}",
        "label": "🎲 Randomly generated applicant",
        "applicant": {
            "name": fake.name(),
            "age": random.randint(22, 65),
            "employment_status": random.choice([
                "Full-time employed", "Part-time employed",
                "Self-employed", "Contract worker"
            ]),
            "employer": fake.company(),
            "years_employed": years_employed,
            "annual_income": annual_income,
            "monthly_income": monthly_income,
            "other_income": random.choice([0, 0, 500, 1000, 2000]),
            "income_source": random.choice([
                "Salary", "Salary + freelance", "1099 / self-employment",
                "Salary + rental income", "Hourly wages"
            ]),
        },
        "credit": {
            "credit_score": credit_score,
            "payment_history": random.choice([
                "No missed payments in 5+ years",
                "1 late payment 18 months ago",
                "2 late payments in last 24 months",
                "Multiple missed payments",
                "Clean history — excellent",
            ]),
            "total_debt": total_debt,
            "monthly_debt_payments": monthly_debt,
            "bankruptcies": random.choice([0, 0, 0, 0, 1]),
            "foreclosures": random.choice([0, 0, 0, 1]),
            "open_accounts": random.randint(2, 15),
            "credit_age_years": random.randint(2, 25),
        },
        "loan": {
            "loan_amount": loan_amount,
            "loan_type": random.choice([
                "30-year fixed", "15-year fixed",
                "5/1 ARM", "VA 30-year fixed", "FHA 30-year fixed"
            ]),
            "down_payment": down_payment,
            "purchase_price": purchase_price,
            "purpose": random.choice([
                "Primary residence purchase",
                "Investment property",
                "Second home / vacation property",
                "Rate-and-term refinance",
            ]),
        },
        "property": {
            "address": fake.address(),
            "type": random.choice([
                "Single-family home", "Condominium",
                "Townhouse", "Multi-family (2-4 units)"
            ]),
            "appraised_value": appraised_value,
            "year_built": random.randint(1950, 2023),
            "condition": random.choice([
                "Excellent", "Very good", "Good",
                "Fair — needs repairs", "Poor"
            ]),
            "flood_zone": random.choice([False, False, False, True]),
        },
    }


def format_application_for_agent(app: dict) -> str:
    """Convert application dict to a clean text prompt for the agents."""
    a = app["applicant"]
    c = app["credit"]
    l = app["loan"]
    p = app["property"]

    dti = round((c["monthly_debt_payments"] / a["monthly_income"]) * 100, 1) if a["monthly_income"] > 0 else 0
    ltv = round((l["loan_amount"] / p["appraised_value"]) * 100, 1) if p["appraised_value"] > 0 else 0

    return f"""
LOAN APPLICATION — {app['id']}
{'='*50}

APPLICANT
  Name:               {a['name']}
  Age:                {a['age']}
  Employment:         {a['employment_status']} at {a['employer']}
  Years employed:     {a['years_employed']}
  Annual income:      ${a['annual_income']:,}
  Monthly income:     ${a['monthly_income']:,}
  Other income:       ${a['other_income']:,}/month ({a['income_source']})

CREDIT PROFILE
  Credit score:       {c['credit_score']}
  Payment history:    {c['payment_history']}
  Total debt:         ${c['total_debt']:,}
  Monthly debt pmts:  ${c['monthly_debt_payments']:,}
  Debt-to-income:     {dti}%
  Bankruptcies:       {c['bankruptcies']}
  Foreclosures:       {c['foreclosures']}
  Open accounts:      {c['open_accounts']}
  Credit age:         {c['credit_age_years']} years

LOAN REQUEST
  Loan amount:        ${l['loan_amount']:,}
  Loan type:          {l['loan_type']}
  Down payment:       ${l['down_payment']:,}
  Purchase price:     ${l['purchase_price']:,}
  Purpose:            {l['purpose']}

PROPERTY
  Address:            {p['address']}
  Type:               {p['type']}
  Appraised value:    ${p['appraised_value']:,}
  Loan-to-value:      {ltv}%
  Year built:         {p['year_built']}
  Condition:          {p['condition']}
  Flood zone:         {'YES ⚠️' if p['flood_zone'] else 'No'}
""".strip()
