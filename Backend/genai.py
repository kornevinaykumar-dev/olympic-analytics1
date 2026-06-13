"""Gemini integration for AI-generated Olympic insights."""
import os
import google.generativeai as genai
from config import Config

_configured = False


def _ensure_configured():
    global _configured
    if _configured:
        return
    key = Config.GEMINI_API_KEY
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")
    genai.configure(api_key=key)
    _configured = True


def _generate(prompt: str) -> str:
    _ensure_configured()
    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()


def country_summary(country: str, stats: dict) -> str:
    prompt = (
        f"Write a concise (3-4 sentence) executive Olympic performance summary "
        f"for {country}. Stats: {stats}. Focus on trends, strengths, and notable "
        f"changes. Avoid bullet points."
    )
    return _generate(prompt)


def trend_analysis(payload: dict) -> str:
    prompt = (
        "Analyze the following Olympic medal trend data and produce a 4-sentence "
        f"analytical narrative highlighting the fastest-growing sports and countries:\n{payload}"
    )
    return _generate(prompt)


def historical_comparison(country: str, current: dict, previous: dict) -> str:
    prompt = (
        f"Compare {country}'s Olympic results. Previous games: {previous}. "
        f"Current games: {current}. Output a 3-sentence comparison report with "
        "percent improvement where relevant."
    )
    return _generate(prompt)


def sport_insights(sport: str, leaderboard: list) -> str:
    prompt = (
        f"Given the medal leaderboard {leaderboard} for the sport {sport}, "
        "write 3 sentences of analytical insights about dominant nations and trends."
    )
    return _generate(prompt)
