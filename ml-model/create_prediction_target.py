import pandas as pd

input_file = "data/wearable/wearable_data.csv"
output_file = "data/wearable/wearable_with_target.csv"

df = pd.read_csv(input_file)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort each patient's readings chronologically
df = df.sort_values(["patient_id", "timestamp"]).reset_index(drop=True)

# Look at the next 4 readings = next 2 hours
future_glucose_values = (
    df.groupby("patient_id")["glucose_mg_dl"]
    .transform(
        lambda x: x.shift(-1)
        .rolling(window=4, min_periods=1)
        .max()
    )
)

df["max_glucose_next_2h"] = future_glucose_values

# Define a glucose spike
df["glucose_spike_next_2h"] = (
    df["max_glucose_next_2h"] >= 180
).astype(int)

# Remove rows where there are not enough future observations
df = df.dropna(subset=["max_glucose_next_2h"])

df.to_csv(output_file, index=False)

print("Prediction target created successfully!")
print(f"Total records: {len(df)}")
print()
print("Target distribution:")
print(df["glucose_spike_next_2h"].value_counts())
print()
print("Target percentage:")
print(df["glucose_spike_next_2h"].value_counts(normalize=True) * 100)