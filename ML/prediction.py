"""Standalone CLI for medal prediction (uses Backend/ml_predict.py logic)."""
import sys, os, json
import joblib, numpy as np

HERE = os.path.dirname(__file__)


def predict(data):
    model = joblib.load(os.path.join(HERE, "model.pkl"))
    enc = joblib.load(os.path.join(HERE, "encoders.pkl"))
    le_c, le_s, le_t = enc["country"], enc["sport"], enc["target"]
    c = data["country"] if data["country"] in le_c.classes_ else le_c.classes_[0]
    s = data["sport"] if data["sport"] in le_s.classes_ else le_s.classes_[0]
    feats = np.array([[
        le_c.transform([c])[0], le_s.transform([s])[0],
        data["athletes"], data["prev_gold"], data["prev_silver"],
        data["prev_bronze"], data["participation_count"],
        data["prev_gold"] + data["prev_silver"] + data["prev_bronze"],
    ]])
    probs = model.predict_proba(feats)[0]
    idx = int(np.argmax(probs))
    return {
        "predicted_medal": le_t.inverse_transform([idx])[0],
        "probability": round(float(probs[idx]), 4),
        "all": {le_t.inverse_transform([i])[0]: round(float(p), 4)
                for i, p in enumerate(probs)},
    }


if __name__ == "__main__":
    sample = {"country": "United States", "sport": "Athletics", "athletes": 20,
              "prev_gold": 5, "prev_silver": 3, "prev_bronze": 4,
              "participation_count": 6}
    print(json.dumps(predict(sample), indent=2))
