"""Rule-based business idea classifier using keyword matching."""

CATEGORIES = {
    "Agriculture": [
        "farm", "farming", "agriculture", "crop", "kheti", "seed", "organic",
        "irrigation", "horticulture", "vegetable", "grain", "wheat", "soybean",
        "mandi", "nursery", "greenhouse", "krishi",
    ],
    "Dairy": [
        "dairy", "milk", "doodh", "ghee", "paneer", "curd", "yogurt", "cattle",
        "buffalo", "cow", "cream", "butter", "lassi",
    ],
    "Food Processing": [
        "food processing", "pickle", "achar", "namkeen", "snack", "flour mill",
        "atta", "spice", "masala", "packaged food", "jam", "papad", "bakery",
        "processing", "oil mill",
    ],
    "Poultry": [
        "poultry", "chicken", "egg", "broiler", "hatchery", "murgi",
    ],
    "Grocery": [
        "grocery", "kirana", "general store", "ration", "provisions", "mini mart",
        "supermarket",
    ],
    "Retail": [
        "retail", "shop", "store", "clothing shop", "mobile shop", "electronics",
        "showroom", "boutique", "stationery", "pharmacy", "medical store",
    ],
    "Handicraft": [
        "handicraft", "craft", "handmade", "pottery", "terracotta", "weaving",
        "embroidery", "woodwork", "artisan", "handloom",
    ],
    "Tailoring": [
        "tailor", "tailoring", "stitching", "garment", "boutique stitching",
        "sewing", "alteration", "clothes",
    ],
    "Repair Services": [
        "repair", "mechanic", "servicing", "mobile repair", "bike repair",
        "two wheeler", "workshop", "electrician", "plumber",
    ],
    "Transportation": [
        "transport", "tempo", "truck", "logistics", "delivery", "auto",
        "taxi", "goods vehicle", "e-rickshaw", "fleet",
    ],
    "Small Manufacturing": [
        "manufacturing", "unit", "fabrication", "welding", "brick", "furniture",
        "assembly", "production", "factory", "packaging unit",
    ],
    "Education": [
        "tuition", "coaching", "school", "education", "training", "computer class",
        "skill centre", "play school",
    ],
    "Beauty": [
        "beauty", "salon", "parlour", "parlor", "spa", "cosmetics", "barber",
        "makeup",
    ],
}


def classify_business(idea):
    text = (idea or "").strip().lower()
    if not text:
        return {"category": "Other", "confidence": 0.2, "matched_keywords": []}

    best_category = "Other"
    best_hits = []
    best_score = 0

    for category, keywords in CATEGORIES.items():
        hits = [kw for kw in keywords if kw in text]
        score = 0
        for kw in hits:
            score += 2 if " " in kw else 1
        if score > best_score:
            best_score = score
            best_category = category
            best_hits = hits

    if best_score == 0:
        return {"category": "Other", "confidence": 0.35, "matched_keywords": []}

    confidence = min(0.95, 0.45 + (best_score * 0.12))
    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "matched_keywords": best_hits,
    }
