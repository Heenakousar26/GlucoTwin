import csv
import math
import random
from datetime import datetime, timedelta

random.seed(42)

patients = [
    ("P001", 7.8),
    ("P002", 7.1),
    ("P003", 8.4),
    ("P004", 6.5),
    ("P005", 7.9),
    ("P006", 7.3),
    ("P007", 8.7),
    ("P008", 6.8),
    ("P009", 8.1),
    ("P010", 7.5)
]

start_time = datetime(2026, 10, 1, 0, 0)

output_file = "wearable_data.csv"

rows = []

for patient_id, hba1c in patients:

    base_glucose = 95 + (hba1c - 6.5) * 18

    for i in range(7 * 48):

        timestamp = start_time + timedelta(minutes=30 * i)

        hour = timestamp.hour + timestamp.minute / 60

        # Daily glucose variation
        daily_variation = 8 * math.sin(i / 20)

        # Meal-related glucose response
        meal_effect = 0

        if 7 <= hour < 9:
            meal_effect = random.uniform(25, 55)

        elif 12 <= hour < 14:
            meal_effect = random.uniform(30, 65)

        elif 19 <= hour < 21:
            meal_effect = random.uniform(30, 70)

        # Some patients have higher spike tendency
        patient_risk_factor = {
            "P001": 1.10,
            "P002": 0.95,
            "P003": 1.25,
            "P004": 0.80,
            "P005": 1.15,
            "P006": 0.95,
            "P007": 1.30,
            "P008": 0.85,
            "P009": 1.20,
            "P010": 1.05
        }[patient_id]

        meal_effect *= patient_risk_factor

        # Random physiological variation
        noise = random.uniform(-7, 7)

        glucose = (
            base_glucose
            + meal_effect
            + daily_variation
            + noise
        )

        # Occasional stronger glucose excursion
        if meal_effect > 30 and random.random() < 0.25:
            glucose += random.uniform(25, 55)

        glucose = max(70, min(glucose, 260))

        # Heart rate
        heart_rate = 68 + random.uniform(-8, 12)

        if meal_effect > 30:
            heart_rate += random.uniform(4, 12)

        # HRV
        hrv = 48 + random.uniform(-8, 8)

        if heart_rate > 85:
            hrv -= random.uniform(5, 12)

        hrv = max(18, hrv)

        # Steps
        if 6 <= hour < 9 or 17 <= hour < 21:
            steps = random.randint(20, 150)
        else:
            steps = random.randint(0, 50)

        # Sleep
        if 0 <= hour < 6:
            sleep_hours = random.uniform(0.5, 1.0)
            activity = "Sleeping"

        elif 6 <= hour < 9:
            sleep_hours = random.uniform(0, 0.2)
            activity = "Morning"

        elif 9 <= hour < 17:
            sleep_hours = 0
            activity = "Sedentary"

        else:
            sleep_hours = 0
            activity = "Active"

        rows.append([
            patient_id,
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            round(glucose, 1),
            round(heart_rate, 1),
            round(hrv, 1),
            steps,
            round(sleep_hours, 2),
            activity
        ])

with open(output_file, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "patient_id",
        "timestamp",
        "glucose_mg_dl",
        "heart_rate_bpm",
        "hrv_ms",
        "steps",
        "sleep_hours",
        "activity_level"
    ])

    writer.writerows(rows)

print("Wearable dataset created successfully!")
print(f"Total records: {len(rows)}")
print(f"Output file: {output_file}")