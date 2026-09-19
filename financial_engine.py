"""Safe financial calculations and explainable feasibility scoring."""


def _to_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        number = float(value)
        if number != number:  # NaN
            return default
        if number == float("inf") or number == float("-inf"):
            return default
        return number
    except (TypeError, ValueError, OverflowError):
        return default


def sanitize_inputs(raw):
    raw = raw or {}
    investment = max(0.0, _to_float(raw.get("investment")))
    monthly_sales = max(0.0, _to_float(raw.get("monthly_sales")))
    monthly_expenses = max(0.0, _to_float(raw.get("monthly_expenses")))
    loan_amount = max(0.0, _to_float(raw.get("loan_amount")))
    interest_rate = max(0.0, _to_float(raw.get("interest_rate")))
    tenure = int(max(0.0, _to_float(raw.get("loan_tenure"), 0)))
    return {
        "investment": investment,
        "monthly_sales": monthly_sales,
        "monthly_expenses": monthly_expenses,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "loan_tenure": tenure,
    }


def calculate_emi(principal, annual_rate, tenure_months):
    principal = max(0.0, _to_float(principal))
    annual_rate = max(0.0, _to_float(annual_rate))
    n = int(max(0.0, _to_float(tenure_months)))

    if principal <= 0 or n <= 0:
        return 0.0

    if annual_rate == 0:
        return round(principal / n, 2)

    r = annual_rate / 12.0 / 100.0
    try:
        factor = (1 + r) ** n
        emi = principal * r * factor / (factor - 1)
        if emi != emi or emi == float("inf"):
            return round(principal / n, 2)
        return round(emi, 2)
    except (OverflowError, ZeroDivisionError, ValueError):
        return round(principal / n, 2)


def calculate_financials(raw):
    data = sanitize_inputs(raw)
    revenue = data["monthly_sales"]
    expenses = data["monthly_expenses"]
    operating_profit = revenue - expenses
    annual_profit = operating_profit * 12
    profit_margin = (operating_profit / revenue * 100.0) if revenue > 0 else 0.0
    emi = calculate_emi(data["loan_amount"], data["interest_rate"], data["loan_tenure"])
    annual_loan_payment = emi * 12
    monthly_cash_surplus = operating_profit - emi
    annual_cash_surplus = monthly_cash_surplus * 12

    investment = data["investment"]
    roi = (annual_profit / investment * 100.0) if investment > 0 else 0.0
    cash_roi = (annual_cash_surplus / investment * 100.0) if investment > 0 else 0.0

    if operating_profit > 0 and investment > 0:
        breakeven_months = investment / operating_profit
        if breakeven_months > 240:
            breakeven_months = None
    else:
        breakeven_months = None

    return {
        "investment": round(investment, 2),
        "monthly_sales": round(revenue, 2),
        "monthly_expenses": round(expenses, 2),
        "loan_amount": round(data["loan_amount"], 2),
        "interest_rate": round(data["interest_rate"], 2),
        "loan_tenure": data["loan_tenure"],
        "revenue": round(revenue, 2),
        "monthly_operating_profit": round(operating_profit, 2),
        "profit": round(operating_profit, 2),
        "annual_profit": round(annual_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "emi": emi,
        "annual_loan_payment": round(annual_loan_payment, 2),
        "annual_debt_payment": round(annual_loan_payment, 2),
        "monthly_cash_surplus": round(monthly_cash_surplus, 2),
        "annual_cash_surplus": round(annual_cash_surplus, 2),
        "roi": round(roi, 2),
        "cash_roi": round(cash_roi, 2),
        "breakeven_months": round(breakeven_months, 1) if breakeven_months else None,
        "break_even": round(breakeven_months, 1) if breakeven_months else None,
    }


def score_feasibility(financials, local_context=None, category=None):
    """Explainable 0-100 feasibility score. Not a guarantee of success."""
    reasons = []
    display_reasons = []
    score = 0

    margin = financials.get("profit_margin") or 0
    profit = financials.get("profit") or 0
    if margin >= 30:
        pts, note = 22, "Strong projected profit margin."
        display_reasons.append("Healthy projected margin")
    elif margin >= 20:
        pts, note = 18, "Healthy projected profit margin."
        display_reasons.append("Healthy projected margin")
    elif margin >= 10:
        pts, note = 12, "Moderate projected profit margin."
        display_reasons.append("Moderate projected margin")
    elif margin > 0:
        pts, note = 6, "Thin profit margin leaves little buffer."
        display_reasons.append("Thin profit margin")
    else:
        pts, note = 0, "No operating profit from current sales and expenses."
        display_reasons.append("Operating profit is not positive")
    score += pts
    reasons.append(f"Profit margin ({margin:.1f}%): {note} (+{pts})")
    if profit > 0:
        display_reasons.insert(0, "Positive monthly operating profit")

    surplus = financials.get("monthly_cash_surplus") or 0
    emi = financials.get("emi") or 0
    if surplus >= 20000:
        pts, note = 18, "Comfortable cash surplus after EMI."
        display_reasons.append("EMI is manageable relative to surplus")
    elif surplus >= 8000:
        pts, note = 14, "Positive cash surplus after EMI."
        display_reasons.append("EMI is manageable relative to surplus")
    elif surplus > 0:
        pts, note = 8, "Narrow surplus after debt service."
        display_reasons.append("Narrow surplus after EMI")
    elif surplus == 0 and emi == 0:
        pts, note = 6, "Break-even cash position with no loan."
    else:
        pts, note = 0, "Cash shortfall after EMI is a stress signal."
        display_reasons.append("EMI burden is high relative to surplus")
    score += pts
    reasons.append(f"Cash surplus (Rs {surplus:,.0f}/month): {note} (+{pts})")

    revenue = financials.get("revenue") or 0
    burden = (emi / revenue) if revenue > 0 else (1 if emi > 0 else 0)
    if emi <= 0:
        pts, note = 16, "No EMI burden on cash flows."
    elif burden < 0.15:
        pts, note = 16, "EMI is a small share of monthly sales."
    elif burden < 0.25:
        pts, note = 12, "EMI is manageable relative to sales."
    elif burden < 0.40:
        pts, note = 6, "EMI consumes a large share of sales."
    else:
        pts, note = 0, "EMI burden is high versus current sales."
    score += pts
    reasons.append(f"EMI burden ({burden * 100:.1f}% of sales): {note} (+{pts})")

    be = financials.get("breakeven_months") or financials.get("break_even")
    if be is None:
        pts, note = 0, "Break-even is not reachable with current profit."
        display_reasons.append("Break-even is not reachable with current profit")
    elif be <= 12:
        pts, note = 14, "Capital may recover within about a year."
        display_reasons.append("Approximate break-even is relatively near-term")
    elif be <= 24:
        pts, note = 11, "Break-even within two years is reasonable for many MSMEs."
        display_reasons.append("Approximate break-even is within a workable range")
    elif be <= 36:
        pts, note = 7, "Longer payback period increases risk."
    else:
        pts, note = 3, "Very long payback period."
    score += pts
    be_text = f"{be} months" if be else "not estimated"
    reasons.append(f"Break-even ({be_text}): {note} (+{pts})")

    investment = financials.get("investment") or 0
    sales = financials.get("monthly_sales") or 0
    turnover_ratio = (sales / investment) if investment > 0 else 0
    if investment <= 0:
        pts, note = 4, "Investment not provided; limited capital assessment."
    elif turnover_ratio >= 0.2:
        pts, note = 10, "Sales are high relative to invested capital."
    elif turnover_ratio >= 0.1:
        pts, note = 7, "Sales-to-investment ratio is moderate."
    elif turnover_ratio >= 0.05:
        pts, note = 4, "Sales are modest versus investment size."
    else:
        pts, note = 2, "Large investment relative to stated monthly sales."
    score += pts
    reasons.append(f"Investment vs sales: {note} (+{pts})")

    local_pts = 8
    local_note = "Neutral local signal (generic / unmatched locality)."
    if local_context:
        demand = (local_context.get("market_demand") or "").lower()
        opportunities = " ".join(local_context.get("opportunities") or []).lower()
        competition = (local_context.get("competition") or "").lower()
        cat = (category or "").lower()
        strong = any(word in demand or word in opportunities for word in [
            "high", "strong", "growing", "good", cat
        ]) if cat else "high" in demand or "strong" in demand
        crowded = any(word in competition for word in ["high", "intense", "saturated"])
        if strong and not crowded:
            local_pts, local_note = 12, "Demo locality data suggests supportive demand."
            display_reasons.append("Local opportunity indicator is positive")
        elif strong and crowded:
            local_pts, local_note = 8, "Demand exists but competition is notable."
            display_reasons.append("Local opportunity exists with competition")
        elif crowded:
            local_pts, local_note = 4, "Local competition may pressure margins."
        else:
            local_pts, local_note = 7, "Mixed local opportunity from demo data."
        if category and category.lower() in opportunities:
            local_pts = min(12, local_pts + 2)
            local_note += " Category aligns with listed local opportunities."
            if "Local opportunity indicator is positive" not in display_reasons:
                display_reasons.append("Local opportunity indicator is positive")
    score += local_pts
    reasons.append(f"Local opportunity (demo data): {local_note} (+{local_pts})")

    score = int(max(0, min(100, score)))
    if score >= 70:
        band = "High"
        status = "High"
    elif score >= 55:
        band = "Moderate"
        status = "Moderate/High"
    elif score >= 40:
        band = "Moderate"
        status = "Moderate"
    else:
        band = "Low"
        status = "Low"

    unique_display = []
    for item in display_reasons:
        if item not in unique_display:
            unique_display.append(item)

    disclaimer = (
        "This is an explainable prototype score, not a guarantee of business success. "
        "Actual outcomes depend on execution, local demand, and verification of data."
    )
    return {
        "feasibility_score": score,
        "feasibility_band": band,
        "status": status,
        "reasons": reasons,
        "display_reasons": unique_display[:6],
        "disclaimer": disclaimer,
    }
