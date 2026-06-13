import io
import csv
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from sqlalchemy import func, desc
from database import db
from models import Country, Sport, Olympic, Medal, Prediction
import genai as gen_ai

api_bp = Blueprint("api", __name__)


# ---------- Dashboard ----------
@api_bp.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    total_countries = db.session.query(func.count(Country.id)).scalar() or 0
    total_sports = db.session.query(func.count(Sport.id)).scalar() or 0
    total_medals = db.session.query(func.coalesce(func.sum(Medal.total), 0)).scalar()
    total_years = db.session.query(func.count(func.distinct(Olympic.year))).scalar() or 0

    # Distribution
    gold = db.session.query(func.coalesce(func.sum(Medal.gold), 0)).scalar()
    silver = db.session.query(func.coalesce(func.sum(Medal.silver), 0)).scalar()
    bronze = db.session.query(func.coalesce(func.sum(Medal.bronze), 0)).scalar()

    # Top 10 countries
    top_q = (
        db.session.query(
            Country.country_name, func.sum(Medal.total).label("t")
        )
        .join(Medal, Medal.country_id == Country.id)
        .group_by(Country.country_name)
        .order_by(desc("t"))
        .limit(10)
        .all()
    )

    # Trend by year
    trend_q = (
        db.session.query(Olympic.year, func.sum(Medal.total).label("t"))
        .join(Medal, Medal.olympic_id == Olympic.id)
        .group_by(Olympic.year)
        .order_by(Olympic.year)
        .all()
    )

    # Sport-wise
    sport_q = (
        db.session.query(Sport.sport_name, func.sum(Medal.total).label("t"))
        .join(Medal, Medal.sport_id == Sport.id)
        .group_by(Sport.sport_name)
        .order_by(desc("t"))
        .limit(10)
        .all()
    )

    return jsonify(
        {
            "cards": {
                "total_countries": int(total_countries),
                "total_sports": int(total_sports),
                "total_medals": int(total_medals),
                "total_years": int(total_years),
            },
            "distribution": {"gold": int(gold), "silver": int(silver), "bronze": int(bronze)},
            "top_countries": [{"country": r[0], "total": int(r[1])} for r in top_q],
            "trend": [{"year": int(r[0]), "total": int(r[1])} for r in trend_q],
            "sports": [{"sport": r[0], "total": int(r[1])} for r in sport_q],
        }
    )


# ---------- Reference data ----------
@api_bp.route("/api/countries", methods=["GET"])
@jwt_required()
def countries():
    rows = Country.query.order_by(Country.country_name).all()
    return jsonify([{"id": r.id, "name": r.country_name, "noc": r.noc_code} for r in rows])


@api_bp.route("/api/sports", methods=["GET"])
@jwt_required()
def sports():
    rows = Sport.query.order_by(Sport.sport_name).all()
    return jsonify([{"id": r.id, "name": r.sport_name} for r in rows])


@api_bp.route("/api/olympics", methods=["GET"])
@jwt_required()
def olympics():
    rows = Olympic.query.order_by(Olympic.year.desc()).all()
    return jsonify(
        [{"id": r.id, "year": r.year, "season": r.season, "city": r.city} for r in rows]
    )


# ---------- Medal standings ----------
@api_bp.route("/api/medals", methods=["GET"])
@jwt_required()
def medals():
    year = request.args.get("year", type=int)
    country = (request.args.get("country") or "").strip()
    sport = (request.args.get("sport") or "").strip()
    sort = request.args.get("sort", "total")
    page = max(request.args.get("page", default=1, type=int), 1)
    per_page = min(max(request.args.get("per_page", default=25, type=int), 1), 200)

    sort_map = {"gold": "g", "silver": "s", "bronze": "b", "total": "t"}
    sort_col = sort_map.get(sort, "t")

    q = (
        db.session.query(
            Country.country_name.label("country"),
            func.sum(Medal.gold).label("g"),
            func.sum(Medal.silver).label("s"),
            func.sum(Medal.bronze).label("b"),
            func.sum(Medal.total).label("t"),
        )
        .join(Medal, Medal.country_id == Country.id)
        .join(Olympic, Olympic.id == Medal.olympic_id)
        .join(Sport, Sport.id == Medal.sport_id)
    )
    if year:
        q = q.filter(Olympic.year == year)
    if country:
        q = q.filter(Country.country_name.ilike(f"%{country}%"))
    if sport:
        q = q.filter(Sport.sport_name.ilike(f"%{sport}%"))
    q = q.group_by(Country.country_name).order_by(desc(sort_col))

    total_rows = q.count()
    rows = q.offset((page - 1) * per_page).limit(per_page).all()
    data = [
        {
            "rank": (page - 1) * per_page + i + 1,
            "country": r.country,
            "gold": int(r.g or 0),
            "silver": int(r.s or 0),
            "bronze": int(r.b or 0),
            "total": int(r.t or 0),
        }
        for i, r in enumerate(rows)
    ]
    return jsonify({"rows": data, "total": total_rows, "page": page, "per_page": per_page})


# ---------- Country analytics ----------
@api_bp.route("/api/analytics/country/<string:name>", methods=["GET"])
@jwt_required()
def country_analytics(name):
    c = Country.query.filter(Country.country_name.ilike(name)).first()
    if not c:
        return jsonify({"error": "Country not found"}), 404

    trend = (
        db.session.query(Olympic.year, func.sum(Medal.gold), func.sum(Medal.silver),
                         func.sum(Medal.bronze), func.sum(Medal.total))
        .join(Medal, Medal.olympic_id == Olympic.id)
        .filter(Medal.country_id == c.id)
        .group_by(Olympic.year)
        .order_by(Olympic.year)
        .all()
    )
    trend_data = [
        {"year": int(y), "gold": int(g or 0), "silver": int(s or 0),
         "bronze": int(b or 0), "total": int(t or 0)}
        for y, g, s, b, t in trend
    ]
    total = sum(r["total"] for r in trend_data)
    gold_total = sum(r["gold"] for r in trend_data)
    best_year = max(trend_data, key=lambda r: r["total"])["year"] if trend_data else None
    gold_pct = (gold_total / total * 100.0) if total else 0.0
    return jsonify(
        {
            "country": c.country_name,
            "trend": trend_data,
            "total_medals": total,
            "best_year": best_year,
            "gold_percentage": round(gold_pct, 2),
        }
    )


# ---------- Sport analytics ----------
@api_bp.route("/api/analytics/sport/<string:name>", methods=["GET"])
@jwt_required()
def sport_analytics(name):
    s = Sport.query.filter(Sport.sport_name.ilike(name)).first()
    if not s:
        return jsonify({"error": "Sport not found"}), 404
    top = (
        db.session.query(Country.country_name, func.sum(Medal.total).label("t"))
        .join(Medal, Medal.country_id == Country.id)
        .filter(Medal.sport_id == s.id)
        .group_by(Country.country_name)
        .order_by(desc("t"))
        .limit(8)
        .all()
    )
    trend = (
        db.session.query(Olympic.year, func.sum(Medal.total))
        .join(Medal, Medal.olympic_id == Olympic.id)
        .filter(Medal.sport_id == s.id)
        .group_by(Olympic.year)
        .order_by(Olympic.year)
        .all()
    )
    return jsonify(
        {
            "sport": s.sport_name,
            "top_countries": [{"country": r[0], "total": int(r[1])} for r in top],
            "trend": [{"year": int(r[0]), "total": int(r[1])} for r in trend],
        }
    )


# ---------- Prediction ----------
@api_bp.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():
    from ml_predict import predict_medal  # lazy import
    data = request.get_json(silent=True) or {}
    required = ["country", "sport", "athletes", "prev_gold", "prev_silver",
                "prev_bronze", "participation_count"]
    for k in required:
        if k not in data:
            return jsonify({"error": f"Missing field {k}"}), 400
    try:
        result = predict_medal(data)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

    rec = Prediction(
        country=str(data["country"])[:120],
        sport=str(data["sport"])[:120],
        predicted_medal=result["predicted_medal"],
        probability=float(result["probability"]),
    )
    db.session.add(rec)
    db.session.commit()
    return jsonify(result)


# ---------- Generative AI ----------
@api_bp.route("/api/generate-insights", methods=["POST"])
@jwt_required()
def generate_insights():
    data = request.get_json(silent=True) or {}
    kind = data.get("type", "country")
    try:
        if kind == "country":
            return jsonify({"text": gen_ai.country_summary(data["country"], data.get("stats", {}))})
        if kind == "trend":
            return jsonify({"text": gen_ai.trend_analysis(data.get("payload", {}))})
        if kind == "comparison":
            return jsonify({
                "text": gen_ai.historical_comparison(
                    data["country"], data.get("current", {}), data.get("previous", {})
                )
            })
        if kind == "sport":
            return jsonify({"text": gen_ai.sport_insights(data["sport"], data.get("leaderboard", []))})
        return jsonify({"error": "Unknown insight type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Exports ----------
@api_bp.route("/api/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    year = request.args.get("year", type=int)
    q = (
        db.session.query(
            Olympic.year, Country.country_name, Sport.sport_name,
            Medal.gold, Medal.silver, Medal.bronze, Medal.total,
        )
        .join(Country, Country.id == Medal.country_id)
        .join(Sport, Sport.id == Medal.sport_id)
        .join(Olympic, Olympic.id == Medal.olympic_id)
    )
    if year:
        q = q.filter(Olympic.year == year)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Year", "Country", "Sport", "Gold", "Silver", "Bronze", "Total"])
    for row in q.all():
        w.writerow(row)
    mem = io.BytesIO(buf.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True,
                     download_name=f"olympics_{year or 'all'}.csv")


@api_bp.route("/api/export/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    year = request.args.get("year", type=int)
    q = (
        db.session.query(
            Country.country_name,
            func.sum(Medal.gold), func.sum(Medal.silver),
            func.sum(Medal.bronze), func.sum(Medal.total),
        )
        .join(Medal, Medal.country_id == Country.id)
        .join(Olympic, Olympic.id == Medal.olympic_id)
    )
    if year:
        q = q.filter(Olympic.year == year)
    q = q.group_by(Country.country_name).order_by(desc(func.sum(Medal.total))).limit(50)

    mem = io.BytesIO()
    doc = SimpleDocTemplate(mem, pagesize=letter)
    styles = getSampleStyleSheet()
    elems = [Paragraph(f"Olympic Medal Standings — {year or 'All Years'}", styles["Title"]),
             Spacer(1, 12)]
    rows = [["Rank", "Country", "Gold", "Silver", "Bronze", "Total"]]
    for i, r in enumerate(q.all(), 1):
        rows.append([i, r[0], int(r[1] or 0), int(r[2] or 0), int(r[3] or 0), int(r[4] or 0)])
    tbl = Table(rows, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elems.append(tbl)
    doc.build(elems)
    mem.seek(0)
    return send_file(mem, mimetype="application/pdf", as_attachment=True,
                     download_name=f"olympics_{year or 'all'}.pdf")
