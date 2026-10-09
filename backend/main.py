
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# -------------------------
# Project Paths
# -------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "ml-model" / "glucotwin_model.pkl"
EHR_PATH = BASE_DIR / "data" / "ehr" / "ehr_data.csv"
WEARABLE_PATH = BASE_DIR / "data" / "wearable" / "wearable_data.csv"


# -------------------------
# Load ML Model and Data
# -------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"ML model not found: {MODEL_PATH}. "
        "Train the model before starting the backend."
    )

if not EHR_PATH.exists():
    raise FileNotFoundError(f"EHR dataset not found: {EHR_PATH}")

if not WEARABLE_PATH.exists():
    raise FileNotFoundError(
        f"Wearable dataset not found: {WEARABLE_PATH}"
    )

model = joblib.load(MODEL_PATH)

ehr_data = pd.read_csv(EHR_PATH)
wearable_data = pd.read_csv(WEARABLE_PATH)

wearable_data["timestamp"] = pd.to_datetime(
    wearable_data["timestamp"]
)

# Sort readings so the latest reading is selected correctly.
wearable_data = wearable_data.sort_values(
    ["patient_id", "timestamp"]
).reset_index(drop=True)


# -------------------------
# FastAPI Application
# -------------------------

app = FastAPI(
    title="GlucoTwin API",
    description=(
        "Digital Twin API for personalized glucose-spike prediction"
    ),
    version="1.0.0",
)


# -------------------------
# CORS Configuration
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Helper Functions
# -------------------------

FEATURE_COLUMNS = [
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
    "diastolic_bp",
]


def get_patient_ehr(patient_id: str):
    patient_ehr = ehr_data[
        ehr_data["patient_id"] == patient_id
    ]

    if patient_ehr.empty:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return patient_ehr.iloc[0]


def get_patient_wearable(patient_id: str):
    patient_wearable = wearable_data[
        wearable_data["patient_id"] == patient_id
    ]

    if patient_wearable.empty:
        raise HTTPException(
            status_code=404,
            detail="Wearable data not found",
        )

    return patient_wearable


def get_selected_reading(
    patient_id: str,
    timestamp: str | None = None,
):
    patient_wearable = get_patient_wearable(
        patient_id
    )

    if timestamp:
        try:
            requested_time = pd.to_datetime(timestamp)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp format",
            )

        differences = (
            patient_wearable["timestamp"] - requested_time
        ).abs()

        selected_index = differences.idxmin()
        return patient_wearable.loc[selected_index]

    return patient_wearable.iloc[-1]


def predict_risk(patient_ehr, reading):
    features = pd.DataFrame(
        [
            {
                "glucose_mg_dl": reading["glucose_mg_dl"],
                "heart_rate_bpm": reading["heart_rate_bpm"],
                "hrv_ms": reading["hrv_ms"],
                "steps": reading["steps"],
                "sleep_hours": reading["sleep_hours"],
                "age": patient_ehr["age"],
                "bmi": patient_ehr["bmi"],
                "hba1c": patient_ehr["hba1c"],
                "diabetes_duration_years": (
                    patient_ehr["diabetes_duration_years"]
                ),
                "systolic_bp": patient_ehr["systolic_bp"],
                "diastolic_bp": patient_ehr["diastolic_bp"],
            }
        ],
        columns=FEATURE_COLUMNS,
    )

    probability = float(
        model.predict_proba(features)[0][1]
    )

    if probability >= 0.70:
        risk_level = "HIGH"
    elif probability >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "glucose_spike_probability": round(
            probability * 100, 2
        ),
        "risk_level": risk_level,
        "prediction_window": "Next 2 hours",
    }


# -------------------------
# Root API
# -------------------------

@app.get("/")
def root():
    return {
        "message": "GlucoTwin API is running",
        "status": "success",
    }


# -------------------------
# Health Check
# -------------------------

@app.get("/api/health")
def health_check():
    return {
        "service": "GlucoTwin Backend",
        "status": "healthy",
    }


# -------------------------
# Get All Patients
# -------------------------

@app.get("/api/patients")
def get_patients():
    patients = ehr_data.to_dict(orient="records")

    return {
        "total_patients": len(patients),
        "patients": patients,
    }


# -------------------------
# Get Individual Patient
# -------------------------

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    patient_ehr = get_patient_ehr(patient_id)
    patient_wearable = get_patient_wearable(patient_id)

    latest_reading = patient_wearable.iloc[-1].copy()
    latest_reading["timestamp"] = str(
        latest_reading["timestamp"]
    )

    return {
        "patient": patient_ehr.to_dict(),
        "latest_wearable": latest_reading.to_dict(),
    }


# -------------------------
# Glucose Spike Prediction
# -------------------------

@app.get("/api/patients/{patient_id}/prediction")
def predict_glucose_spike(
    patient_id: str,
    timestamp: str | None = None,
):
    patient_ehr = get_patient_ehr(patient_id)
    reading = get_selected_reading(
        patient_id, timestamp
    )

    prediction = predict_risk(patient_ehr, reading)

    return {
        "patient_id": patient_id,
        "timestamp_used": str(reading["timestamp"]),
        "current_glucose_mg_dl": float(
            reading["glucose_mg_dl"]
        ),
        **prediction,
    }


# -------------------------
# Dashboard API
# -------------------------

@app.get("/api/dashboard/{patient_id}")
def get_dashboard(
    patient_id: str,
    timestamp: str | None = None,
):
    patient_ehr = get_patient_ehr(patient_id)
    reading = get_selected_reading(
        patient_id, timestamp
    )

    prediction = predict_risk(patient_ehr, reading)

    reading_data = reading.to_dict()
    reading_data["timestamp"] = str(
        reading_data["timestamp"]
    )

    return {
        "patient": patient_ehr.to_dict(),
        "latest_wearable": reading_data,
        "prediction": prediction,
    }


# -------------------------
# Get Available Timestamps
# -------------------------

@app.get("/api/patients/{patient_id}/timestamps")
def get_patient_timestamps(patient_id: str):
    patient_wearable = get_patient_wearable(
        patient_id
    )

    timestamps = (
        patient_wearable["timestamp"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
        .tolist()
    )

    return {
        "patient_id": patient_id,
        "total_timestamps": len(timestamps),
        "timestamps": timestamps,
    }


# -------------------------
# Get Glucose History
# -------------------------

@app.get("/api/patients/{patient_id}/glucose-history")
def get_glucose_history(
    patient_id: str,
    timestamp: str | None = None,
):
    patient_wearable = get_patient_wearable(
        patient_id
    )

    selected_reading = get_selected_reading(
        patient_id, timestamp
    )

    selected_time = selected_reading["timestamp"]

    start_time = selected_time - pd.Timedelta(hours=3)
    end_time = selected_time + pd.Timedelta(hours=2)

    history = patient_wearable[
        (patient_wearable["timestamp"] >= start_time)
        & (patient_wearable["timestamp"] <= end_time)
    ].copy()

    history["timestamp"] = history[
        "timestamp"
    ].dt.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "patient_id": patient_id,
        "selected_timestamp": str(selected_time),
        "glucose_history": history[
            ["timestamp", "glucose_mg_dl"]
        ].to_dict(orient="records"),
    }
