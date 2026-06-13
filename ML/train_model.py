"""Trains a Random Forest classifier on the seeded Olympic dataset.

Run after seed_data.py has produced olympic_dataset.csv:
    python train_model.py
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "olympic_dataset.csv")
MODEL_PATH = os.path.join(HERE, "model.pkl")
ENC_PATH = os.path.join(HERE, "encoders.pkl")


def main():
    df = pd.read_csv(DATA)
    df = df.dropna()

    le_country = LabelEncoder().fit(df["Country"])
    le_sport = LabelEncoder().fit(df["Sport"])
    le_target = LabelEncoder().fit(df["Target_Medal_Category"])

    X = pd.DataFrame({
        "country": le_country.transform(df["Country"]),
        "sport": le_sport.transform(df["Sport"]),
        "athletes": df["Athletes"],
        "prev_gold": df["Previous_Gold"],
        "prev_silver": df["Previous_Silver"],
        "prev_bronze": df["Previous_Bronze"],
        "participation": df["Participation_Count"],
        "total_prev": df["Total_Previous_Medals"],
    })
    y = le_target.transform(df["Target_Medal_Category"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print("Accuracy :", round(accuracy_score(y_test, preds), 4))
    print("Precision:", round(precision_score(y_test, preds, average="weighted", zero_division=0), 4))
    print("Recall   :", round(recall_score(y_test, preds, average="weighted", zero_division=0), 4))
    print("F1 Score :", round(f1_score(y_test, preds, average="weighted", zero_division=0), 4))
    print("Confusion matrix:\n", confusion_matrix(y_test, preds))

    joblib.dump(clf, MODEL_PATH)
    joblib.dump({"country": le_country, "sport": le_sport, "target": le_target}, ENC_PATH)
    print(f"Saved {MODEL_PATH} and {ENC_PATH}")


if __name__ == "__main__":
    main()
