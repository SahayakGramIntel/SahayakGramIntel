"""Demo pointers to common MSME / livelihood schemes. Not eligibility advice."""

VERIFICATION_NOTE = "Verify current eligibility and terms from official government sources."

SCHEMES = [
    {
        "scheme": "PMEGP",
        "full_name": "Prime Minister's Employment Generation Programme",
        "purpose": "Credit-linked subsidy support for new micro-enterprises in manufacturing and services.",
        "categories": [
            "Agriculture", "Food Processing", "Dairy", "Handicraft", "Tailoring",
            "Small Manufacturing", "Repair Services", "Retail", "Beauty", "Other",
        ],
        "note": "Project report, own contribution, and bank appraisal typically apply. This prototype cannot confirm eligibility.",
    },
    {
        "scheme": "MUDRA",
        "full_name": "Pradhan Mantri MUDRA Yojana",
        "purpose": "Collateral-light working capital or term loans for micro / small non-farm activities (Shishu, Kishore, Tarun).",
        "categories": [
            "Retail", "Grocery", "Tailoring", "Beauty", "Repair Services",
            "Food Processing", "Transportation", "Education", "Handicraft",
            "Dairy", "Poultry", "Agriculture", "Other",
        ],
        "note": "Loan size, documentation, and bank policies vary. Do not treat this as a sanction or rate quote.",
    },
    {
        "scheme": "PMFME",
        "full_name": "PM Formalisation of Micro Food Processing Enterprises",
        "purpose": "Support for micro food processing units, including credit-linked subsidy and formalisation support.",
        "categories": ["Food Processing", "Dairy", "Agriculture", "Poultry"],
        "note": "Typically relevant where the activity is food processing or allied. Confirm product, FSSAI, and scheme guidelines.",
    },
    {
        "scheme": "Stand-Up India",
        "full_name": "Stand-Up India",
        "purpose": "Bank loans for SC/ST and women entrepreneurs for greenfield enterprises in manufacturing, services, or trading.",
        "categories": [
            "Small Manufacturing", "Retail", "Food Processing", "Education",
            "Beauty", "Transportation", "Other",
        ],
        "note": "Requires the entrepreneur to meet scheme beneficiary criteria. This app does not collect caste/gender data and cannot confirm fit.",
    },
]


def match_schemes(category, financials):
    category = category or "Other"
    loan = financials.get("loan_amount") or 0
    investment = financials.get("investment") or 0
    matched = []

    for item in SCHEMES:
        relevant = category in item["categories"]
        why = []
        if relevant:
            why.append(f"Business category '{category}' is commonly discussed under {item['scheme']}.")
        if item["scheme"] == "MUDRA" and 0 < loan <= 1000000:
            relevant = True
            why.append("Stated loan size is within a range often associated with MUDRA discussions.")
        if item["scheme"] == "PMEGP" and investment >= 50000:
            why.append("Capital investment for a new unit is the kind of project PMEGP is designed around.")
        if item["scheme"] == "PMFME" and category in ("Food Processing", "Dairy", "Agriculture", "Poultry"):
            why.append("Activity appears food or agri-allied, which is the PMFME focus.")
        if item["scheme"] == "Stand-Up India" and investment >= 100000:
            why.append("Greenfield enterprise with meaningful capital may be worth checking if beneficiary criteria apply.")

        if not why:
            continue
        if not relevant and item["scheme"] not in ("MUDRA",):
            continue

        matched.append({
            "scheme": item["scheme"],
            "full_name": item["full_name"],
            "purpose": item["purpose"],
            "why_relevant": " ".join(why),
            "important_note": f"{item['note']} {VERIFICATION_NOTE}",
        })

    if not matched:
        matched.append({
            "scheme": "General MSME / bank credit",
            "full_name": "Discuss with a bank / DIC / CSC",
            "purpose": "Local banks and district industries centres can map suitable credit or subsidy products.",
            "why_relevant": "Category did not strongly match the demo scheme list.",
            "important_note": VERIFICATION_NOTE,
        })

    return matched, VERIFICATION_NOTE
