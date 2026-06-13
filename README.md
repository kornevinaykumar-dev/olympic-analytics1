# AI-Enhanced Olympic Medal Analytics System

Full-stack platform: **Flask + MySQL + scikit-learn + Gemini AI + Bootstrap/Chart.js**.

## Features
- JWT auth (register/login/profile), bcrypt password hashing
- Dashboard with KPI cards + Chart.js charts (pie, bar, line, horizontal bar)
- Medal standings (search/filter/sort/paginate, CSV + PDF export)
- Country & Sport analytics (trends, radar)
- Random Forest medal prediction (Gold/Silver/Bronze/None + probabilities)
- Gemini-generated insights: country summary, sport insights, trend analysis
- Rate limiting, CORS, input validation, parameterised SQL via SQLAlchemy

## Project structure
```
AI_Enhanced_Olympic_Medal_Analytics_System/
├── Backend/   Flask app, models, routes, auth, genai, seed
├── Frontend/  HTML + Bootstrap + Chart.js pages
├── ML/        dataset, training script, trained model.pkl / encoders.pkl
└── README.md
```

## Setup

### 1. MySQL
```bash
mysql -u root -p < Backend/schema.sql
```

### 2. Backend
```bash
cd Backend
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # edit DB creds + GEMINI_API_KEY
python seed_data.py        # populates DB + writes ML/olympic_dataset.csv
```

### 3. ML model
A pre-trained `ML/model.pkl` and `ML/encoders.pkl` ship with the project. To retrain:
```bash
cd ML && python train_model.py
```

### 4. Run
```bash
cd Backend && python app.py
# open http://localhost:5000
```

Register an account, then explore Dashboard / Standings / Analytics / Prediction / AI Insights.

## Gemini API key
Get one at https://aistudio.google.com/app/apikey and put it in `Backend/.env`:
```
GEMINI_API_KEY=your-key-here
```

## REST API
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/register | Create account |
| POST | /api/login | Returns JWT |
| GET | /api/profile | Current user (JWT) |
| GET | /api/dashboard | KPI cards + chart data |
| GET | /api/countries,/sports,/olympics | Reference lists |
| GET | /api/medals | Standings with filters |
| GET | /api/analytics/country/<name> | Country trend |
| GET | /api/analytics/sport/<name> | Sport trend |
| POST | /api/predict | ML medal prediction |
| POST | /api/generate-insights | Gemini insight |
| GET | /api/export/csv?year= | CSV export |
| GET | /api/export/pdf?year= | PDF export |

All `/api/*` endpoints (except register/login) require `Authorization: Bearer <token>`.

## Security notes
- Passwords stored as bcrypt hashes only.
- JWTs signed with `JWT_SECRET_KEY` (change in production).
- SQLAlchemy parameterises all queries — no string SQL.
- Email + length validation on registration.
- Rate limit 200 req/min/IP via Flask-Limiter.
- `.env` excluded from version control; use `.env.example` as template.

## License
MIT — academic / portfolio use.
