"""Rule-based SWOT and practical recommendations from actual numbers."""


def generate_swot(name, idea, category, financials, local_snapshot):
    strengths, weaknesses, opportunities, threats = [], [], [], []

    margin = financials.get("profit_margin") or 0
    surplus = financials.get("monthly_cash_surplus") or 0
    emi = financials.get("emi") or 0
    sales = financials.get("monthly_sales") or 0
    expenses = financials.get("monthly_expenses") or 0
    investment = financials.get("investment") or 0
    loan = financials.get("loan_amount") or 0
    roi = financials.get("roi") or 0
    be = financials.get("breakeven_months") or financials.get("break_even")

    if margin >= 20:
        strengths.append(f"Operating margin of {margin:.1f}% provides a buffer for price or volume shocks.")
    if surplus > 0:
        strengths.append(f"Monthly cash surplus of Rs {surplus:,.0f} after EMI supports day-to-day operations.")
    if loan <= 0:
        strengths.append("No loan reduces fixed repayment pressure.")
    elif emi > 0 and sales > 0 and emi / sales < 0.15:
        strengths.append("EMI is a small share of stated monthly sales.")
    if local_snapshot.get("matched"):
        strengths.append(f"Location matched to demo locality data for {local_snapshot.get('name')}.")
    if category and category != "Other":
        strengths.append(f"Idea maps clearly to '{category}', which helps structure the plan.")
    if roi >= 20:
        strengths.append(f"Indicative annual ROI of {roi:.1f}% on stated investment is attractive on paper.")
    if not strengths:
        strengths.append("The idea is documented with numbers, which is a starting point for iteration.")

    if margin <= 10:
        weaknesses.append("Thin or negative margin leaves little room for wastage, credit sales, or downtime.")
    if surplus < 0:
        weaknesses.append("Cash after EMI is negative — loan burden exceeds operating profit.")
    if expenses >= sales and sales > 0:
        weaknesses.append("Monthly expenses are at or above sales in the current plan.")
    if sales == 0:
        weaknesses.append("Expected monthly sales are zero or missing, so demand is unproven in this model.")
    if investment > 0 and sales / investment < 0.08:
        weaknesses.append("Investment is large compared with expected monthly sales.")
    if be and be > 36:
        weaknesses.append(f"Approximate break-even of {be} months is long.")
    if be is None and investment > 0:
        weaknesses.append("Break-even cannot be estimated because operating profit is not positive.")
    if not weaknesses:
        weaknesses.append("No major numeric red flags; still validate costs and demand locally.")

    for item in (local_snapshot.get("opportunities") or [])[:3]:
        opportunities.append(item)
    if category in ("Dairy", "Food Processing", "Agriculture", "Poultry"):
        opportunities.append("Explore value-addition and formalisation pathways (e.g. quality, packaging, PMFME-type support).")
    if sales > 0:
        opportunities.append("Test a smaller inventory cycle before locking the full investment.")
    if local_snapshot.get("matched"):
        opportunities.append("Use mandi / colony footfall patterns from the locality snapshot to pick a selling point.")
    if not opportunities:
        opportunities.append("Validate demand with a short pilot and customer conversations.")

    for item in (local_snapshot.get("risks") or [])[:3]:
        threats.append(item)
    if emi > 0 and sales > 0 and emi / sales >= 0.25:
        threats.append("High EMI relative to sales can cause default risk if collections slip.")
    if category in ("Grocery", "Retail", "Dairy"):
        threats.append("Price competition and thin retail margins are common in this category.")
    threats.append("Unverified assumptions (sales, expenses, local demand) can change the outcome.")
    if not threats:
        threats.append("General MSME risks: demand, working capital, and execution.")

    return {
        "strengths": strengths[:6],
        "weaknesses": weaknesses[:6],
        "opportunities": opportunities[:6],
        "threats": threats[:6],
    }


def generate_recommendations(financials, local_snapshot, category):
    recs = []
    margin = financials.get("profit_margin") or 0
    surplus = financials.get("monthly_cash_surplus") or 0
    emi = financials.get("emi") or 0
    sales = financials.get("monthly_sales") or 0
    expenses = financials.get("monthly_expenses") or 0
    investment = financials.get("investment") or 0
    loan = financials.get("loan_amount") or 0
    be = financials.get("breakeven_months") or financials.get("break_even")

    if expenses > 0 and sales > 0 and expenses / sales >= 0.75:
        recs.append("Consider reducing recurring operating expenses.")
    if surplus < 0 or (sales > 0 and emi / sales >= 0.25):
        recs.append("Consider reviewing loan amount or repayment structure.")
    if sales == 0 or (investment > 0 and sales < investment * 0.05):
        recs.append("Consider validating demand before increasing investment.")
    if margin > 0 and margin < 12:
        recs.append("Improve mix: add a higher-margin product rather than only expanding volume.")
    if local_snapshot.get("matched"):
        recs.append("Consider conducting a small local market validation.")
    else:
        recs.append("Location is not in the demo city set — treat locality comments as generic and collect on-ground data.")
    if be and be <= 18 and surplus > 0:
        recs.append("Numbers look workable on paper — keep a 2–3 month cash reserve before scaling.")
    if category in ("Dairy", "Food Processing", "Poultry"):
        recs.append("Plan cold-chain, spoilage, and FSSAI/hygiene costs; they often wipe thin margins.")
    if category in ("Grocery", "Retail"):
        recs.append("Track weekly fast-moving SKUs and avoid blocking cash in slow inventory.")
    if loan > investment * 0.8 and investment > 0:
        recs.append("Loan is a large share of project cost — raise promoter contribution to reduce repayment stress.")
    if not recs:
        recs.append("Keep written weekly records of sales, expenses, and cash. Re-run this assessment after 30 days of real data.")

    recs.append("This assistant is rule-based decision support. Confirm all figures with a banker, CA, or local officer before borrowing.")
    return recs[:8]


def apply_what_if(base_inputs, scenario):
    """Return modified inputs for a named scenario."""
    data = dict(base_inputs)
    scenario = (scenario or "").lower().strip()
    if scenario in ("sales_10", "sales+10", "sales +10%"):
        data["monthly_sales"] = (data.get("monthly_sales") or 0) * 1.10
        label = "Sales +10%"
    elif scenario in ("sales_20", "sales+20", "sales +20%"):
        data["monthly_sales"] = (data.get("monthly_sales") or 0) * 1.20
        label = "Sales +20%"
    elif scenario in ("expenses_10", "expenses+10", "expenses +10%"):
        data["monthly_expenses"] = (data.get("monthly_expenses") or 0) * 1.10
        label = "Expenses +10%"
    elif scenario in ("loan_20", "loan-20", "loan_reduction", "loan -20%"):
        data["loan_amount"] = (data.get("loan_amount") or 0) * 0.80
        label = "Loan -20%"
    else:
        label = "No change"
    return data, label
