"""Rule-based GramIntel assistant. Answers from the current report only."""

import re

INTENT_PATTERNS = {
    "emi": [
        r"\bemi\b", r"किस्त", r"\bkist\b", r"installment", r"monthly payment",
        r"meri emi", r"emi kitni", r"emi batao", r"explain.{0,12}emi",
    ],
    "profit": [
        r"\bprofit\b", r"munafa", r"mu(n|na)fa", r"faida", r"लाभ", r"मुनाफा",
        r"कमाई", r"operating profit", r"monthly profit", r"mera monthly profit",
        r"profit kitna", r"profitable",
    ],
    "revenue": [
        r"\brevenue\b", r"\bsales\b", r"bikri", r"बिक्री", r"aamdani", r"आय",
        r"monthly sales", r"kitni sales",
    ],
    "expenses": [
        r"\bexpense", r"kharch", r"खर्च", r"cost", r"spending", r"outgoing",
    ],
    "loan": [
        r"\bloan\b", r"कर्ज", r"उधार", r"udhaar", r"principal", r"borrow",
        r"interest rate", r"tenure", r"byaj", r"loan kitna",
    ],
    "feasibility": [
        r"feasib", r"score", r"why.{0,20}(score|feasib|low|high|moderate)",
        r"feasibility score like", r"possible", r"viable", r"kyun", r"क्यों",
        r"score kaisa", r"score kyun", r"score low",
    ],
    "risk": [
        r"\brisk", r"threat", r"खतर", r"जोखिम", r"jokhim", r"biggest risk",
        r"danger", r"problem", r"risk kya",
    ],
    "swot": [
        r"\bswot\b", r"strength", r"weakness", r"opportunit", r"threats",
        r"explain.{0,12}swot",
    ],
    "scheme": [
        r"scheme", r"yojana", r"योजना", r"mudra", r"pmegp", r"pmfme",
        r"stand-?up", r"sarkari", r"government scheme", r"which scheme",
        r"scheme kaunsi",
    ],
    "recommendation": [
        r"recommend", r"suggest", r"salah", r"सलाह", r"kya karun", r"what should",
        r"advice", r"next step",
    ],
    "break_even": [
        r"break[ -]?even", r"payback", r"wapas", r"capital recover", r"kitne mahine",
    ],
    "roi": [
        r"\broi\b", r"return on", r"return of investment", r"investment return",
    ],
    "what_if": [
        r"what[ -]?if", r"simulation", r"agar sales", r"agar kharch",
        r"sales \+?10", r"loan reduction", r"sales badhane", r"badhane par",
    ],
    "help": [
        r"\bhelp\b", r"madad", r"मदद", r"kya pooch", r"what can you", r"kaise use",
    ],
}


def inr(amount):
    try:
        value = float(amount)
    except (TypeError, ValueError):
        value = 0.0
    negative = value < 0
    value = abs(value)
    whole = int(round(value)) if abs(value - round(value)) < 0.005 else int(value)
    show_frac = abs(value - round(value)) >= 0.005
    s = str(whole)
    if len(s) <= 3:
        grouped = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        chunks = []
        while len(rest) > 2:
            chunks.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            chunks.insert(0, rest)
        grouped = ",".join(chunks + [last3])
    if show_frac:
        frac = round(value - int(value), 2)
        grouped += f"{frac:.2f}"[1:]
    return ("-₹" if negative else "₹") + grouped


def detect_language(text):
    raw = text or ""
    if re.search(r"[\u0900-\u097F]", raw):
        return "hi"
    lowered = raw.lower()
    hindi_markers = (
        "mera", "meri", "mere", "kitna", "kitni", "kya", "kyun", "kaise",
        "hai", "hain", "aapka", "aapki", "mujhe", "batao", "samjhao", "karun",
        "yojana", "kharch", "munafa", "kist", "madad", "salah", "kaunsi",
        "badhane",
    )
    if any(re.search(r"\b" + re.escape(w) + r"\b", lowered) for w in hindi_markers):
        return "hi"
    return "en"


def detect_intent(text):
    lowered = (text or "").strip().lower()
    if not lowered:
        return "help"
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, lowered, re.IGNORECASE):
                score += 2 if " " in pattern or len(pattern) > 8 else 1
        if score:
            scores[intent] = score
    if not scores:
        return "unknown"
    if scores.get("emi") and scores.get("loan") and scores["emi"] >= scores["loan"]:
        scores["loan"] = 0
    if scores.get("profit") and scores.get("roi"):
        if "roi" not in lowered and "return" not in lowered:
            scores["roi"] = 0
    return max(scores, key=scores.get)


def answer_question(assessment, message):
    if not assessment:
        return {
            "intent": "help",
            "language": detect_language(message),
            "reply": "Please generate a business assessment first.",
        }
    intent = detect_intent(message)
    lang = detect_language(message)
    reply = _compose(assessment, intent, lang)
    return {"intent": intent, "language": lang, "reply": reply}


def _compose(assessment, intent, lang):
    fin = assessment.get("financials") or {}
    feas = assessment.get("feasibility") or {}
    swot = assessment.get("swot") or {}
    schemes = assessment.get("schemes") or []
    recs = assessment.get("recommendations") or []
    hindi = lang == "hi"

    profit = fin.get("profit") or 0
    revenue = fin.get("revenue") or 0
    expenses = fin.get("monthly_expenses") or 0
    emi = fin.get("emi") or 0
    loan = fin.get("loan_amount") or 0
    rate = fin.get("interest_rate") or 0
    tenure = fin.get("loan_tenure") or 0
    surplus = fin.get("monthly_cash_surplus") or 0
    roi = fin.get("roi") or 0
    be = fin.get("breakeven_months") or fin.get("break_even")
    score = feas.get("feasibility_score")
    band = feas.get("feasibility_band") or feas.get("status") or ""
    reasons = feas.get("display_reasons") or feas.get("reasons") or []

    if intent == "profit":
        if hindi:
            return (
                f"Aapka estimated monthly operating profit {inr(profit)} hai. "
                f"Yeh monthly sales {inr(revenue)} minus expenses {inr(expenses)} se aaya hai. "
                f"EMI ke baad cash surplus {inr(surplus)} hai."
            )
        return (
            f"Your estimated monthly operating profit is {inr(profit)}. "
            f"That is monthly sales {inr(revenue)} minus expenses {inr(expenses)}. "
            f"Cash after EMI is {inr(surplus)}."
        )

    if intent == "revenue":
        if hindi:
            return f"Is report mein expected monthly sales / revenue {inr(revenue)} hai."
        return f"Expected monthly sales (revenue) in this report is {inr(revenue)}."

    if intent == "expenses":
        if hindi:
            return f"Aapka stated monthly expenses {inr(expenses)} hai."
        return f"Stated monthly expenses in this report are {inr(expenses)}."

    if intent == "emi":
        if emi <= 0:
            if hindi:
                return "Is plan mein koi loan EMI nahi hai (loan amount 0 ya tenure missing)."
            return "This plan has no loan EMI (loan amount is zero or tenure is missing)."
        if hindi:
            return (
                f"Aapki estimated monthly EMI {inr(emi)} hai. "
                f"Yeh {inr(loan)} loan, {rate}% annual interest, aur {tenure} months tenure par aadharit hai."
            )
        return (
            f"Your estimated monthly EMI is {inr(emi)}. "
            f"It is based on a {inr(loan)} loan at {rate}% annual interest for {tenure} months."
        )

    if intent == "loan":
        if hindi:
            return (
                f"Loan amount {inr(loan)} hai, annual interest {rate}%, tenure {tenure} months. "
                f"Estimated EMI {inr(emi)} hai."
            )
        return (
            f"Loan amount is {inr(loan)}, annual interest {rate}%, tenure {tenure} months. "
            f"Estimated EMI is {inr(emi)}."
        )

    if intent == "feasibility":
        reason_text = " ".join(reasons[:4]) if reasons else "Score factors were not stored."
        why = {
            "High": "Score 70–100 band mein hai kyunki profit, cash surplus, aur EMI burden comparatively theek hain.",
            "Moderate/High": "Score comparatively better band mein hai, lekin abhi bhi assumptions validate karni chahiye.",
            "Moderate": "Score 40–69 band mein hai — kuch factors theek hain, kuch pressure dikhate hain.",
            "Low": "Score 0–39 band mein hai kyunki profit, EMI, ya break-even mein kamzori hai.",
        }.get(band, "Band report ke score se nikala gaya hai.")
        if hindi:
            return (
                f"Aapka feasibility score {score}/100 ({band}) hai. {why} "
                f"Asli factors: {reason_text} "
                f"Yeh guarantee nahi hai — sirf is report ke numbers par based explainable score hai."
            )
        return (
            f"Your feasibility score is {score}/100 ({band}). "
            f"Factors used: {reason_text} "
            f"This is an explainable prototype score, not a guarantee of success."
        )

    if intent == "risk":
        threats = swot.get("threats") or []
        local_risks = (assessment.get("locality") or {}).get("risks") or []
        biggest = threats[0] if threats else (local_risks[0] if local_risks else None)
        extra = ""
        if surplus < 0:
            extra = f" Numeric red flag: cash after EMI is negative ({inr(surplus)})."
        if hindi:
            base = f"Is report ke hisaab se sabse bada risk: {biggest}" if biggest else "Alag se named risk nahi mila."
            return base + (f" Extra signal: EMI ke baad cash negative hai ({inr(surplus)})." if surplus < 0 else "")
        return (
            (f"The biggest risk called out for this report is: {biggest}" if biggest else "No named risk was stored.")
            + extra
        )

    if intent == "swot":
        def take(items):
            return "; ".join((items or [])[:2]) or "—"
        if hindi:
            return (
                f"SWOT is report ke inputs se bana hai. "
                f"Strengths: {take(swot.get('strengths'))}. "
                f"Weaknesses: {take(swot.get('weaknesses'))}. "
                f"Opportunities: {take(swot.get('opportunities'))}. "
                f"Threats: {take(swot.get('threats'))}."
            )
        return (
            f"SWOT is generated from this report’s numbers. "
            f"Strengths: {take(swot.get('strengths'))}. "
            f"Weaknesses: {take(swot.get('weaknesses'))}. "
            f"Opportunities: {take(swot.get('opportunities'))}. "
            f"Threats: {take(swot.get('threats'))}."
        )

    if intent == "scheme":
        if not schemes:
            msg = "Is report se koi scheme pointer match nahi hua." if hindi else "No scheme pointers matched this report."
            return msg + " Verify current eligibility and terms from official government sources."
        names = ", ".join(s.get("scheme") for s in schemes if s.get("scheme"))
        first = schemes[0]
        why = first.get("why_relevant") or ""
        if hindi:
            return (
                f"Is business category ke liye demo pointers: {names}. "
                f"{first.get('scheme')}: {why} "
                f"Verify current eligibility and terms from official government sources. Eligibility guarantee nahi hai."
            )
        return (
            f"Scheme pointers that may be relevant for this report: {names}. "
            f"{first.get('scheme')}: {why} "
            f"Verify current eligibility and terms from official government sources. This is not an eligibility decision."
        )

    if intent == "recommendation":
        top = recs[0] if recs else None
        if hindi:
            return ("Pramukh salah: " + top) if top else "Is report ke liye extra recommendation nahi mili."
        return ("Main recommendation: " + top) if top else "No extra recommendation was generated for this report."

    if intent == "break_even":
        if be:
            if hindi:
                return f"Approximate break-even period {be} months hai (investment / monthly operating profit)."
            return f"Approximate break-even is {be} months (investment ÷ monthly operating profit)."
        if hindi:
            return "Current operating profit se break-even estimate nahi nikal sakte (profit positive nahi hai)."
        return "Break-even cannot be estimated with current operating profit (profit is not positive)."

    if intent == "roi":
        if hindi:
            return f"Is report ka indicative annual ROI {roi}% hai (annual operating profit ÷ investment)."
        return f"Indicative annual ROI on stated investment is {roi}% (annual operating profit ÷ investment)."

    if intent == "what_if":
        if hindi:
            return (
                f"Abhi base monthly profit {inr(profit)} aur EMI {inr(emi)} hai. "
                f"Report page par Sales +10%, Sales +20%, Expenses +10%, aur Loan -20% buttons se naya profit/EMI/feasibility dekh sakte ho. "
                f"Woh simulation saved report ko overwrite nahi karta."
            )
        return (
            f"Current monthly profit is {inr(profit)} and EMI is {inr(emi)}. "
            f"Use the What-If buttons on this report (Sales +10% / +20%, Expenses +10%, Loan -20%) "
            f"to compare current vs scenario profit, EMI, and feasibility. Simulation does not overwrite the saved report."
        )

    if intent == "help":
        if hindi:
            return (
                "Aap is report ke profit, sales, kharch, EMI, loan, feasibility, risk, SWOT, schemes, "
                "recommendations, break-even, ROI, aur what-if ke baare mein pooch sakte ho. "
                "Main sirf is assessment ke numbers se jawab deta hoon — yeh trained LLM nahi hai."
            )
        return (
            "Ask about this report’s profit, sales, expenses, EMI, loan, feasibility, risk, SWOT, schemes, "
            "recommendations, break-even, ROI, or what-if. This is an explainable AI-assisted rule-based advisory prototype."
        )

    if hindi:
        return (
            "Main is sawal ko report metric se map nahi kar paya. "
            "Profit, EMI, feasibility, risk, SWOT, ya scheme ke baare mein poochiye."
        )
    return (
        "I could not map that to a report metric. Try asking about profit, EMI, feasibility, risk, SWOT, or schemes."
    )
