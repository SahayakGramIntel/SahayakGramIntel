"""GramIntel Flask application — explainable AI-assisted rule-based advisory prototype."""

import json
import traceback

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

import database
from business_classifier import classify_business
from financial_engine import calculate_financials, score_feasibility
from local_data import get_local_snapshot
from scheme_data import match_schemes
from recommendation_engine import generate_swot, generate_recommendations, apply_what_if
from chatbot import answer_question

app = Flask(__name__)
app.secret_key = "gramintel-local-prototype-key"
app.config["PROPAGATE_EXCEPTIONS"] = False
database.init_db()


def build_assessment(form):
    name = (form.get("name") or "").strip() or "Not provided"
    location = (form.get("location") or "").strip() or "Not specified"
    idea = (form.get("business_idea") or "").strip() or "Not specified"

    raw = {
        "investment": form.get("investment"),
        "monthly_sales": form.get("monthly_sales"),
        "monthly_expenses": form.get("monthly_expenses"),
        "loan_amount": form.get("loan_amount"),
        "interest_rate": form.get("interest_rate"),
        "loan_tenure": form.get("loan_tenure"),
    }
    financials = calculate_financials(raw)
    classification = classify_business(idea)
    category = classification["category"]
    locality = get_local_snapshot(location)
    feasibility = score_feasibility(financials, locality, category)
    swot = generate_swot(name, idea, category, financials, locality)
    schemes, scheme_disclaimer = match_schemes(category, financials)
    recommendations = generate_recommendations(financials, locality, category)

    return {
        "name": name,
        "location": location,
        "business_idea": idea,
        "classification": classification,
        "category": category,
        "financials": financials,
        "locality": locality,
        "feasibility": feasibility,
        "swot": swot,
        "schemes": schemes,
        "scheme_disclaimer": scheme_disclaimer,
        "recommendations": recommendations,
    }


def inputs_from_report(report):
    return {
        "investment": report["investment"],
        "monthly_sales": report["monthly_sales"],
        "monthly_expenses": report["monthly_expenses"],
        "loan_amount": report["loan_amount"],
        "interest_rate": report["interest_rate"],
        "loan_tenure": report["loan_tenure"],
    }


def hydrate_report(report):
    assessment = build_assessment({
        "name": report["name"],
        "location": report["location"],
        "business_idea": report["business_idea"],
        **inputs_from_report(report),
    })
    assessment["id"] = report["id"]
    assessment["created_at"] = report["created_at"]
    return assessment


def _parse_assessment_id(payload):
    payload = payload or {}
    raw = (
        payload.get("assessment_id")
        or payload.get("report_id")
        or request.form.get("assessment_id")
        or request.form.get("report_id")
        or request.args.get("assessment_id")
    )
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found."}), 404
    flash("The page you requested was not found.")
    return redirect(url_for("index"))


@app.errorhandler(500)
def server_error(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Something went wrong. Please try again."}), 500
    flash("Something went wrong while processing your request. Please try again.")
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        idea = (request.form.get("business_idea") or "").strip()
        name = (request.form.get("name") or "").strip()
        location = (request.form.get("location") or "").strip()
        if not name or not location or not idea:
            flash("Please fill entrepreneur name, location, and business idea.")
            return redirect(url_for("index"))

        assessment = build_assessment(request.form)
        fin = assessment["financials"]
        feas = assessment["feasibility"]
        report_id = database.save_report({
            "name": assessment["name"],
            "location": assessment["location"],
            "business_idea": assessment["business_idea"],
            "category": assessment["category"],
            "investment": fin["investment"],
            "monthly_sales": fin["monthly_sales"],
            "monthly_expenses": fin["monthly_expenses"],
            "loan_amount": fin["loan_amount"],
            "interest_rate": fin["interest_rate"],
            "loan_tenure": fin["loan_tenure"],
            "revenue": fin["revenue"],
            "profit": fin["profit"],
            "profit_margin": fin["profit_margin"],
            "emi": fin["emi"],
            "roi": fin["roi"],
            "break_even": fin["break_even"],
            "feasibility_score": feas["feasibility_score"],
            "feasibility_reasons": json.dumps(feas.get("display_reasons") or feas.get("reasons") or []),
            "swot_data": json.dumps(assessment["swot"]),
            "recommendations": json.dumps(assessment["recommendations"]),
        })
        return redirect(url_for("report", report_id=report_id))
    except Exception:
        traceback.print_exc()
        flash("Could not analyse this business. Please check the numbers and try again.")
        return redirect(url_for("index"))


@app.route("/report/<int:report_id>")
def report(report_id):
    try:
        row = database.get_report(report_id)
        if not row:
            flash("Report not found. Please generate a business assessment first.")
            return redirect(url_for("reports"))
        return render_template("report.html", data=hydrate_report(row))
    except Exception:
        traceback.print_exc()
        flash("Could not open this report.")
        return redirect(url_for("reports"))


@app.route("/reports")
def reports():
    try:
        return render_template("reports.html", reports=database.list_reports())
    except Exception:
        traceback.print_exc()
        flash("Could not load saved reports.")
        return render_template("reports.html", reports=[])


@app.route("/chat")
def chat_latest():
    rows = database.list_reports()
    if not rows:
        flash("Please generate a business assessment first.")
        return redirect(url_for("index"))
    return redirect(url_for("chat_page", report_id=rows[0]["id"]))


@app.route("/chat/<int:report_id>")
def chat_page(report_id):
    row = database.get_report(report_id)
    if not row:
        flash("Please generate a business assessment first.")
        return redirect(url_for("index"))
    return redirect(url_for("report", report_id=report_id, chat=1))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "GramIntel"})


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        payload = request.get_json(silent=True) or {}
        assessment_id = _parse_assessment_id(payload)
        message = (payload.get("message") or request.form.get("message") or "").strip()

        if assessment_id is None:
            return jsonify({
                "reply": "Please generate a business assessment first.",
                "intent": "help",
            })
        if not message:
            return jsonify({"reply": "Please type a question.", "intent": "help"}), 400

        row = database.get_report(assessment_id)
        if not row:
            return jsonify({
                "reply": "Please generate a business assessment first.",
                "intent": "help",
            })

        assessment = hydrate_report(row)
        result = answer_question(assessment, message)
        database.save_chat_message(assessment_id, "user", message)
        database.save_chat_message(assessment_id, "assistant", result["reply"])
        return jsonify({
            "reply": result["reply"],
            "intent": result["intent"],
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"reply": "Something went wrong while answering. Please try again.", "intent": "help"}), 500


@app.route("/api/chat/<int:assessment_id>", methods=["GET"])
def chat_history(assessment_id):
    try:
        row = database.get_report(assessment_id)
        if not row:
            return jsonify({"error": "Report not found"}), 404
        return jsonify({"messages": database.list_chat_messages(assessment_id)})
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Could not load chat history."}), 500


def _what_if_payload(report_id, scenario):
    row = database.get_report(report_id)
    if not row:
        return None, {"error": "Report not found"}

    base = inputs_from_report(row)
    locality = get_local_snapshot(row["location"])
    category = row["category"]

    old_fin = calculate_financials(base)
    old_feas = score_feasibility(old_fin, locality, category)

    new_inputs, label = apply_what_if(base, scenario)
    new_fin = calculate_financials(new_inputs)
    new_feas = score_feasibility(new_fin, locality, category)

    def diff(new, old):
        return round((new or 0) - (old or 0), 2)

    return {
        "scenario": scenario,
        "label": label,
        "current": {
            "revenue": old_fin["revenue"],
            "expenses": old_fin["monthly_expenses"],
            "profit": old_fin["profit"],
            "emi": old_fin["emi"],
            "feasibility_score": old_feas["feasibility_score"],
            "status": old_feas["status"],
        },
        "scenario_result": {
            "revenue": new_fin["revenue"],
            "expenses": new_fin["monthly_expenses"],
            "profit": new_fin["profit"],
            "emi": new_fin["emi"],
            "feasibility_score": new_feas["feasibility_score"],
            "status": new_feas["status"],
        },
        "difference": {
            "revenue": diff(new_fin["revenue"], old_fin["revenue"]),
            "expenses": diff(new_fin["monthly_expenses"], old_fin["monthly_expenses"]),
            "profit": diff(new_fin["profit"], old_fin["profit"]),
            "emi": diff(new_fin["emi"], old_fin["emi"]),
            "feasibility_score": new_feas["feasibility_score"] - old_feas["feasibility_score"],
        },
        "old_profit": old_fin["profit"],
        "new_profit": new_fin["profit"],
        "old_emi": old_fin["emi"],
        "new_emi": new_fin["emi"],
        "old_revenue": old_fin["revenue"],
        "new_revenue": new_fin["revenue"],
        "old_expenses": old_fin["monthly_expenses"],
        "new_expenses": new_fin["monthly_expenses"],
        "old_feasibility": old_feas["feasibility_score"],
        "new_feasibility": new_feas["feasibility_score"],
        "old_band": old_feas["status"],
        "new_band": new_feas["status"],
        "new_margin": new_fin["profit_margin"],
        "new_surplus": new_fin["monthly_cash_surplus"],
    }, None


@app.route("/api/what-if", methods=["POST"])
def what_if():
    try:
        payload = request.get_json(silent=True) or {}
        assessment_id = _parse_assessment_id(payload)
        scenario = payload.get("scenario") or request.form.get("scenario")
        if assessment_id is None:
            return jsonify({"error": "Please generate a business assessment first."}), 400
        data, err = _what_if_payload(assessment_id, scenario)
        if err:
            return jsonify(err), 404
        return jsonify(data)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Could not run the simulation."}), 500


@app.route("/api/what-if/<int:report_id>", methods=["POST"])
def what_if_by_id(report_id):
    try:
        payload = request.get_json(silent=True) or {}
        scenario = payload.get("scenario") or request.form.get("scenario")
        data, err = _what_if_payload(report_id, scenario)
        if err:
            return jsonify(err), 404
        return jsonify(data)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Could not run the simulation."}), 500


if __name__ == "__main__":
    database.init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
