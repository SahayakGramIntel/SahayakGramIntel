# GramIntel

AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for rural micro-entrepreneurs.

This is a Smart India Hackathon (SIH) prototype. It is an **explainable AI-assisted rule-based advisory prototype**. It is **not** a trained LLM and does not call OpenAI, Gemini, or any paid cloud API.

## Problem statement

Rural micro-entrepreneurs often need a simple way to understand whether an idea is workable: estimated profit, EMI burden, local opportunity, risks, and which government scheme *might* be worth checking. GramIntel gives a local, transparent first-cut assessment.

## Features

- Business idea intake with demo fill
- Keyword-based business classification
- Financial engine: profit, margin, EMI, ROI, break-even
- Explainable feasibility score (0–100) with reasons
- Demo locality snapshots (Mandsaur, Indore, Bhopal, Sagar, Neemuch, Ujjain)
- SWOT, scheme pointers, recommendations
- What-If simulator (Sales +10% / +20%, Expenses +10%, Loan -20%)
- Previous reports in SQLite
- Local contextual chatbot (English + Hinglish) using the current assessment
- Optional browser voice input (app still works if speech is unavailable)

## Architecture

- `app.py` — Flask routes and orchestration
- `database.py` — SQLite (`data/gramintel.db`)
- `financial_engine.py` — EMI, profit, feasibility
- `business_classifier.py` — keyword categories
- `local_data.py` — demo locality snapshots
- `scheme_data.py` — PMEGP, MUDRA, PMFME, Stand-Up India pointers
- `recommendation_engine.py` — SWOT, recommendations, What-If
- `chatbot.py` — rule-based intent detection + report numbers
- `templates/` — Jinja2 pages
- `static/` — CSS and vanilla JavaScript

## Tech stack

Python 3, Flask, SQLite, HTML, CSS, Vanilla JavaScript, Jinja2.

No React, Node.js, Firebase, MongoDB, OpenAI, Gemini, paid APIs, or external CDNs.

## Installation

```
python -m venv venv
```

Windows:

```
venv\Scripts\activate
```

Then:

```
pip install -r requirements.txt
```

## Running

```
python app.py
```

Open:

http://127.0.0.1:5000

Health check: http://127.0.0.1:5000/health

Open the chatbox at http://127.0.0.1:5000/chat

Chat: http://127.0.0.1:5000/chat

## Chatbot explanation

The chatbot is a **local contextual assistant**. It detects intents (profit, EMI, feasibility, risk, SWOT, schemes, etc.) and answers using the saved assessment. Hindi/Hinglish phrases such as “Mera monthly profit kitna hai?” get simple Hinglish replies with the **actual** report numbers.

If `assessment_id` is missing, the API replies: “Please generate a business assessment first.”

## Voice explanation

`voice_input.js` fills Name, Location, and Business Idea using the browser `SpeechRecognition` / `webkitSpeechRecognition` API. `chatbot.js` can put spoken text into the chat input. Speech may depend on the browser. If unavailable, the UI shows “Voice input is not supported in this browser.” Typing still works.

## Financial calculations

- Monthly operating profit = sales − expenses
- EMI = `P * r * (1+r)^n / ((1+r)^n − 1)` where `r` is monthly interest rate
- Zero loan or zero interest is handled safely (no EMI, or principal / tenure)
- ROI = annual operating profit / investment
- Approximate break-even months = investment / monthly operating profit

## Feasibility methodology

A 0–100 explainable score from profit margin, cash surplus after EMI, EMI burden, break-even, investment vs sales, and demo local opportunity. Status bands: Low / Moderate / Moderate-High / High. **This is not a guarantee of business success.**

## Limitations

- Demo locality data is sample data, not live government statistics
- Scheme pointers are not eligibility decisions
- Chatbot is rule-based, not a generative model
- Voice input depends on the browser

## Future scope

- District-level official datasets
- More scheme rules with explicit eligibility questionnaires
- Offline speech-to-text
- Multi-year cash-flow projections

## SIH demo flow

1. Open the home page.
2. Click **Try Demo** (Ramesh / Mandsaur / dairy).
3. Click **Analyze Business**.
4. Review category, finances, feasibility, SWOT, schemes, recommendations.
5. Click What-If buttons.
6. Open **🤖 Ask GramIntel** and ask “Mera monthly profit kitna hai?”
7. Open **Previous Reports** and reopen the saved assessment.
