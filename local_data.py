"""Demo / sample hyper-local market snapshots. Not official statistics."""

LOCALITIES = {
    "mandsaur": {
        "name": "Mandsaur",
        "label": "Demo / Sample Locality Data",
        "market_demand": "Moderate-to-high demand for dairy, grocery, agri-input, and repair services around mandi and residential clusters.",
        "common_businesses": [
            "Dairy and milk collection",
            "Kirana / grocery",
            "Agri-input and seed shops",
            "Two-wheeler repair",
            "Food processing (spices, namkeen)",
        ],
        "transport_access": "Connected via road to Neemuch, Ratlam, and Indore; mandi traffic supports wholesale movement. Last-mile village access varies by season.",
        "competition": "Kirana and dairy collection are moderately competitive; specialized processing and branded packaging are less crowded.",
        "opportunities": [
            "Value-added dairy (paneer, ghee, flavoured milk)",
            "Agri-linked processing around soybean and spices",
            "Repair and servicing for farm and two-wheelers",
        ],
        "risks": [
            "Seasonal farm income affects local spending",
            "Price sensitivity in grocery and milk",
            "Power and cold-chain gaps for perishables",
        ],
    },
    "indore": {
        "name": "Indore",
        "label": "Demo / Sample Locality Data",
        "market_demand": "High urban demand for food, retail, education, beauty, and logistics. Strong consumption and wholesale markets.",
        "common_businesses": [
            "Food service and packaged snacks",
            "Retail and apparel",
            "Coaching / skill centres",
            "Beauty salons",
            "Courier and last-mile delivery",
        ],
        "transport_access": "Major road, rail, and air hub of Madhya Pradesh. Dense intra-city transport but higher rental and traffic costs.",
        "competition": "High competition in retail, food, and coaching. Niche quality or location advantage is important.",
        "opportunities": [
            "Specialty food processing for city and e-commerce",
            "Repair and appliance services in housing colonies",
            "Skill and tuition near residential pockets",
        ],
        "risks": [
            "High rent and wage costs",
            "Intense competition",
            "Working-capital pressure from credit sales",
        ],
    },
    "bhopal": {
        "name": "Bhopal",
        "label": "Demo / Sample Locality Data",
        "market_demand": "Steady demand from government, education, and residential localities for grocery, tutoring, food, and services.",
        "common_businesses": [
            "Grocery and daily needs",
            "Tuition and computer training",
            "Food processing and bakery",
            "Tailoring and boutique",
            "Automobile repair",
        ],
        "transport_access": "State capital with good intercity connectivity. Intra-city demand is spread across multiple townships.",
        "competition": "Moderate-to-high in coaching and grocery; neighbourhood service businesses can still find pockets.",
        "opportunities": [
            "Neighbourhood dairy/food kiosks",
            "Education support near hostels and colonies",
            "Small manufacturing for local institutions",
        ],
        "risks": [
            "Scattered demand across a large city",
            "Compliance and licensing for food units",
            "Competition from established chains",
        ],
    },
    "sagar": {
        "name": "Sagar",
        "label": "Demo / Sample Locality Data",
        "market_demand": "Town-plus-hinterland demand for grocery, agri services, education, and basic manufacturing.",
        "common_businesses": [
            "Kirana and wholesale grocery",
            "Agriculture trading",
            "Tuition centres",
            "Tailoring",
            "Small fabrication",
        ],
        "transport_access": "Road and rail links to Bhopal and Jabalpur. Village catchment is important for agri-linked trade.",
        "competition": "Moderate in grocery and coaching; limited branded food processing.",
        "opportunities": [
            "Agri-linked trading and processing",
            "Skill/tuition for student population",
            "Repair services for transport and farm equipment",
        ],
        "risks": [
            "Seasonal cash cycles",
            "Smaller urban consumer base than Indore/Bhopal",
            "Logistics cost for inbound materials",
        ],
    },
    "neemuch": {
        "name": "Neemuch",
        "label": "Demo / Sample Locality Data",
        "market_demand": "Demand linked to agriculture, mandi trade, dairy, and cross-border Rajasthan traffic.",
        "common_businesses": [
            "Agri trading",
            "Dairy",
            "Transport and warehousing",
            "Kirana",
            "Repair workshops",
        ],
        "transport_access": "Highway connectivity toward Mandsaur and Rajasthan. Goods movement is a local advantage.",
        "competition": "Trading and transport are established; value-added processing is relatively open.",
        "opportunities": [
            "Dairy collection and chilling",
            "Transport / tempo services",
            "Packaging and small food processing",
        ],
        "risks": [
            "Commodity price swings",
            "Dependence on agri season",
            "Need for working capital in trading",
        ],
    },
    "ujjain": {
        "name": "Ujjain",
        "label": "Demo / Sample Locality Data",
        "market_demand": "Base urban demand plus pilgrimage/tourism spikes for food, retail, lodging-related services, and handicrafts.",
        "common_businesses": [
            "Food and prasad-related retail",
            "Handicraft and pooja items",
            "Grocery",
            "Tailoring",
            "Transport and lodging support services",
        ],
        "transport_access": "Well connected to Indore. Festival periods create sharp demand peaks and logistics strain.",
        "competition": "High around temple corridors; neighbourhood businesses away from core can be less crowded.",
        "opportunities": [
            "Packaged food and dairy for visitors",
            "Handicraft and local products",
            "Repair and transport around event seasons",
        ],
        "risks": [
            "Seasonal / festival demand volatility",
            "Crowded tourist retail",
            "Quality and hygiene compliance for food",
        ],
    },
}

GENERIC_LOCALITY = {
    "name": "Unmatched location",
    "label": "Demo / Sample Locality Data",
    "market_demand": "Generic small-town / rural demand assumed: daily needs, repair, agri-linked trade, and basic services. Replace with field validation.",
    "common_businesses": [
        "Kirana",
        "Dairy",
        "Repair services",
        "Tailoring",
        "Small trading",
    ],
    "transport_access": "Assume mixed road access. Confirm mandi, highway, and last-mile conditions on the ground.",
    "competition": "Typical neighbourhood competition in grocery and similar daily businesses.",
    "opportunities": [
        "Differentiate on quality, freshness, or service",
        "Start with a smaller test inventory",
        "Tie products to local crop or dairy cycles",
    ],
    "risks": [
        "Unverified local demand",
        "Price-sensitive customers",
        "Working-capital and seasonality risks",
    ],
}


def get_local_snapshot(location):
    key = (location or "").strip().lower()
    if key in LOCALITIES:
        snapshot = dict(LOCALITIES[key])
        snapshot["matched"] = True
        return snapshot
    for slug, data in LOCALITIES.items():
        if slug in key or data["name"].lower() in key:
            snapshot = dict(data)
            snapshot["matched"] = True
            return snapshot
    snapshot = dict(GENERIC_LOCALITY)
    snapshot["name"] = (location or "").strip() or "Not specified"
    snapshot["matched"] = False
    return snapshot
