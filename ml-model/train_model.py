import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)

# -----------------------------
# 1. Load datasets
# -----------------------------

ehr_file = "data/ehr/ehr_data.csv"
wearable_file = "data/wearable/wearable_with_target.csv"

ehr = pd.read_csv(ehr_file)
wearable = pd.read_csv(wearable_file)

# -----------------------------
# 2. Merge EHR + Wearable
# -----------------------------

df = wearable.merge(
    ehr,
    on="patient_id",
    how="left"
)

print("Data fusion completed!")
print(f"Total records after merging: {len(df)}")

# -----------------------------
# 3. Select features
# -----------------------------

features = [
    "glucose_mg_dl",
    "heart_rate_bpm",
    "hrv_ms",
    "steps",
    "sleep_hours",
    "age",
    "bmi",
    "hba1c",
    "diabetes_duration_years",
    "systolic_bp",
    "diastolic_bp"
]

target = "glucose_spike_next_2h"

X = df[features]
y = df[target]

# -----------------------------
# 4. Train-test split
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print()
print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# -----------------------------
# 5. Train Random Forest
# -----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# -----------------------------
# 6. Make predictions
# -----------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]

# -----------------------------
# 7. Evaluate model
# -----------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

print()
print("===== MODEL PERFORMANCE =====")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

print()
print("===== CLASSIFICATION REPORT =====")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))

# -----------------------------
# 8. Feature importance
# -----------------------------

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print()
print("===== FEATURE IMPORTANCE =====")
print(importance)

# -----------------------------
# 9. Save trained model
# -----------------------------

model_file = "ml-model/glucotwin_model.pkl"

joblib.dump(model, model_file)

print()
print(f"Model saved successfully: {model_file}")