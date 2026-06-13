from datetime import datetime
from database import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(120), unique=True, nullable=False)
    noc_code = db.Column(db.String(8), unique=True, nullable=False)


class Sport(db.Model):
    __tablename__ = "sports"
    id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.String(120), unique=True, nullable=False)


class Olympic(db.Model):
    __tablename__ = "olympics"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    season = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    __table_args__ = (db.UniqueConstraint("year", "season", name="uq_year_season"),)


class Medal(db.Model):
    __tablename__ = "medals"
    id = db.Column(db.Integer, primary_key=True)
    olympic_id = db.Column(db.Integer, db.ForeignKey("olympics.id"), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)
    gold = db.Column(db.Integer, default=0)
    silver = db.Column(db.Integer, default=0)
    bronze = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)

    olympic = db.relationship("Olympic")
    country = db.relationship("Country")
    sport = db.relationship("Sport")


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(120), nullable=False)
    sport = db.Column(db.String(120), nullable=False)
    predicted_medal = db.Column(db.String(20), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
