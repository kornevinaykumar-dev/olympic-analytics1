"""Generates an Olympic dataset (~600 rows) and seeds the MySQL DB.

Run AFTER creating the schema:
    python seed_data.py
"""
import random
from datetime import datetime
import csv
import os

from app import create_app
from database import db
from models import Country, Sport, Olympic, Medal

random.seed(42)

COUNTRIES = [
    ("United States", "USA"), ("China", "CHN"), ("Japan", "JPN"),
    ("Great Britain", "GBR"), ("Russia", "RUS"), ("Germany", "GER"),
    ("France", "FRA"), ("Australia", "AUS"), ("Italy", "ITA"),
    ("South Korea", "KOR"), ("Netherlands", "NED"), ("Canada", "CAN"),
    ("Brazil", "BRA"), ("India", "IND"), ("Spain", "ESP"),
    ("Hungary", "HUN"), ("New Zealand", "NZL"), ("Kenya", "KEN"),
    ("Jamaica", "JAM"), ("Cuba", "CUB"),
]

SPORTS = [
    "Athletics", "Swimming", "Gymnastics", "Cycling", "Rowing", "Boxing",
    "Wrestling", "Weightlifting", "Shooting", "Archery", "Fencing",
    "Judo", "Sailing", "Diving", "Hockey",
]

OLYMPICS = [
    (2000, "Summer", "Sydney"), (2004, "Summer", "Athens"),
    (2008, "Summer", "Beijing"), (2012, "Summer", "London"),
    (2016, "Summer", "Rio de Janeiro"), (2020, "Summer", "Tokyo"),
    (2024, "Summer", "Paris"),
]


def country_strength(idx, sport):
    base = max(1, 14 - idx) * 0.7
    boost = {"Athletics": 1.4, "Swimming": 1.3, "Gymnastics": 1.1}.get(sport, 1.0)
    return base * boost


def make_row(country_idx, country, sport, year):
    s = country_strength(country_idx, sport)
    gold = max(0, int(random.gauss(s * 0.4, 1.2)))
    silver = max(0, int(random.gauss(s * 0.5, 1.3)))
    bronze = max(0, int(random.gauss(s * 0.6, 1.4)))
    return gold, silver, bronze


def seed():
    app = create_app()
    with app.app_context():
        if Country.query.count() == 0:
            for n, code in COUNTRIES:
                db.session.add(Country(country_name=n, noc_code=code))
        if Sport.query.count() == 0:
            for s in SPORTS:
                db.session.add(Sport(sport_name=s))
        if Olympic.query.count() == 0:
            for y, season, city in OLYMPICS:
                db.session.add(Olympic(year=y, season=season, city=city))
        db.session.commit()

        if Medal.query.count() > 0:
            print("Medals already seeded; skipping.")
            return

        countries = {c.country_name: c for c in Country.query.all()}
        sports = {s.sport_name: s for s in Sport.query.all()}
        olys = {o.year: o for o in Olympic.query.all()}

        # CSV for ML training too
        ml_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "..", "ML", "olympic_dataset.csv"))
        os.makedirs(os.path.dirname(ml_path), exist_ok=True)
        f = open(ml_path, "w", newline="")
        w = csv.writer(f)
        w.writerow(["Country", "Year", "Sport", "Athletes", "Previous_Gold",
                    "Previous_Silver", "Previous_Bronze", "Participation_Count",
                    "Total_Previous_Medals", "Target_Medal_Category"])

        prev = {}  # (country, sport) -> (g,s,b)
        count = 0
        for year_idx, (year, _, _) in enumerate(OLYMPICS):
            for idx, (cname, _) in enumerate(COUNTRIES):
                for sname in SPORTS:
                    g, s, b = make_row(idx, cname, sname, year)
                    total = g + s + b
                    db.session.add(Medal(
                        olympic_id=olys[year].id,
                        country_id=countries[cname].id,
                        sport_id=sports[sname].id,
                        gold=g, silver=s, bronze=b, total=total,
                    ))
                    pg, ps, pb = prev.get((cname, sname), (0, 0, 0))
                    athletes = random.randint(2, 30)
                    target = "None"
                    if g > 0: target = "Gold"
                    elif s > 0: target = "Silver"
                    elif b > 0: target = "Bronze"
                    w.writerow([cname, year, sname, athletes, pg, ps, pb,
                                year_idx + 1, pg + ps + pb, target])
                    prev[(cname, sname)] = (g, s, b)
                    count += 1
            db.session.commit()
        f.close()
        print(f"Seeded {count} medal rows; wrote ML dataset to {ml_path}")


if __name__ == "__main__":
    seed()
