
import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
const DEFAULT_TIMESTAMP = "2026-10-07 12:00:00";

function App() {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState("P001");
  const [dashboard, setDashboard] = useState(null);
  const [timestamps, setTimestamps] = useState([]);
  const [selectedTimestamp, setSelectedTimestamp] =
    useState(DEFAULT_TIMESTAMP);
  const [glucoseHistory, setGlucoseHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const selectedDate = selectedTimestamp
    ? selectedTimestamp.slice(0, 10)
    : "";

  const availableDates = useMemo(
    () => [...new Set(timestamps.map((timestamp) => timestamp.slice(0, 10)))],
    [timestamps]
  );

  const timesForSelectedDate = useMemo(
    () =>
      timestamps.filter(
        (timestamp) => timestamp.slice(0, 10) === selectedDate
      ),
    [timestamps, selectedDate]
  );

  // Load all patients.
  useEffect(() => {
    let cancelled = false;

    fetch(`${API_URL}/api/patients`)
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load patients");
        return response.json();
      })
      .then((data) => {
        if (!cancelled) setPatients(data.patients || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load timestamps for the selected patient.
  useEffect(() => {
    let cancelled = false;

    fetch(`${API_URL}/api/patients/${selectedPatient}/timestamps`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load patient timestamps");
        }
        return response.json();
      })
      .then((data) => {
        if (cancelled) return;

        const availableTimestamps = data.timestamps || [];
        setTimestamps(availableTimestamps);

        if (!availableTimestamps.includes(selectedTimestamp)) {
          const fallbackTimestamp = availableTimestamps.includes(
            DEFAULT_TIMESTAMP
          )
            ? DEFAULT_TIMESTAMP
            : availableTimestamps[availableTimestamps.length - 1] || "";

          setSelectedTimestamp(fallbackTimestamp);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedPatient]);

  // Load dashboard and glucose history for the selected patient and time.
  useEffect(() => {
    if (!selectedPatient || !selectedTimestamp) return;

    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");
      setDashboard(null);
      setGlucoseHistory([]);

      try {
        const encodedTimestamp = encodeURIComponent(selectedTimestamp);

        const dashboardResponse = await fetch(
          `${API_URL}/api/dashboard/${selectedPatient}?timestamp=${encodedTimestamp}`
        );

        if (!dashboardResponse.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const dashboardData = await dashboardResponse.json();

        if (dashboardData.error) {
          throw new Error(dashboardData.error);
        }

        const historyResponse = await fetch(
          `${API_URL}/api/patients/${selectedPatient}/glucose-history?timestamp=${encodedTimestamp}`
        );

        if (!historyResponse.ok) {
          throw new Error("Failed to fetch glucose history");
        }

        const historyData = await historyResponse.json();

        if (historyData.error) {
          throw new Error(historyData.error);
        }

        if (!cancelled) {
          setDashboard(dashboardData);
          setGlucoseHistory(historyData.glucose_history || []);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [selectedPatient, selectedTimestamp]);

  // Change the date while preserving the selected time when possible.
  function handleDateChange(event) {
    const newDate = event.target.value;
    const currentTime = selectedTimestamp.slice(11, 16);

    const matchingTimestamp = timestamps.find(
      (timestamp) =>
        timestamp.slice(0, 10) === newDate &&
        timestamp.slice(11, 16) === currentTime
    );

    const firstTimestampForDate = timestamps.find(
      (timestamp) => timestamp.slice(0, 10) === newDate
    );

    setSelectedTimestamp(
      matchingTimestamp || firstTimestampForDate || ""
    );
  }

  // Change the time on the currently selected date.
  function handleTimeChange(event) {
    const selectedTime = event.target.value;

    const matchingTimestamp = timestamps.find(
      (timestamp) =>
        timestamp.slice(0, 10) === selectedDate &&
        timestamp.slice(11, 16) === selectedTime
    );

    if (matchingTimestamp) {
      setSelectedTimestamp(matchingTimestamp);
    }
  }

  if (error) {
    return (
      <div className="error">
        <div>
          <h2>Unable to load GlucoTwin</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading || !dashboard) {
    return (
      <div className="loading">
        Loading GlucoTwin Dashboard...
      </div>
    );
  }

  const patient = dashboard.patient;
  const wearable = dashboard.latest_wearable;
  const prediction = dashboard.prediction;

  const chartData = glucoseHistory.map((reading) => ({
    time: reading.timestamp.slice(11, 16),
    glucose: reading.glucose_mg_dl,
  }));

  const riskClass =
    prediction.risk_level === "HIGH"
      ? "high-risk"
      : prediction.risk_level === "MEDIUM"
      ? "medium-risk"
      : "low-risk";

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>GlucoTwin</h1>
          <p>Personalized Glucose Digital Twin</p>
        </div>

        <div className="header-status">
          <span className="status-dot"></span>
          System Active
        </div>
      </header>

      <main className="dashboard">
        {/* Patient Profile */}
        <section className="patient-banner">
          <div>
            <span className="section-label">PATIENT PROFILE</span>
            <h2>{patient.patient_id}</h2>
            <p>
              {patient.age} years • {patient.gender} •{" "}
              {patient.medication}
            </p>
          </div>

          <div className="patient-risk">
            <span>Current Risk</span>
            <strong className={riskClass}>
              {prediction.risk_level}
            </strong>
          </div>
        </section>

        {/* Patient Selection */}
        <section className="time-selector">
          <div>
            <span className="section-label">PATIENT SELECTION</span>
            <h2>Select Patient</h2>
            <p>
              Choose a patient to load their personalized Digital Twin.
            </p>
          </div>

          <select
            value={selectedPatient}
            onChange={(event) => setSelectedPatient(event.target.value)}
            aria-label="Select patient"
          >
            {patients.map((item) => (
              <option key={item.patient_id} value={item.patient_id}>
                {item.patient_id} — {item.age} yrs — {item.gender}
              </option>
            ))}
          </select>
        </section>

        {/* Date and Time Selection */}
        <section className="time-selector">
          <div>
            <span className="section-label">DIGITAL TWIN STATE</span>
            <h2>Select Patient Time</h2>
            <p>
              Choose a date and wearable reading to explore the patient's
              historical physiological state.
            </p>
          </div>

          <div className="datetime-controls">
            <label className="datetime-field">
              <span>Select date</span>
              <select
                value={selectedDate}
                onChange={handleDateChange}
                aria-label="Select date"
                disabled={availableDates.length === 0}
              >
                {availableDates.map((date) => (
                  <option key={date} value={date}>
                    {date}
                  </option>
                ))}
              </select>
            </label>

            <label className="datetime-field">
              <span>Select time</span>
              <select
                value={selectedTimestamp.slice(11, 16)}
                onChange={handleTimeChange}
                aria-label="Select time"
                disabled={timesForSelectedDate.length === 0}
              >
                {timesForSelectedDate.map((timestamp) => {
                  const time = timestamp.slice(11, 16);

                  return (
                    <option key={timestamp} value={time}>
                      {time}
                    </option>
                  );
                })}
              </select>
            </label>
          </div>
        </section>

        {/* Patient Information */}
        <section className="section">
          <div className="section-title">
            <h2>Patient Information</h2>
            <span>Historical EHR Data</span>
          </div>

          <div className="info-grid">
            <div className="info-card">
              <span>Age</span>
              <strong>{patient.age}</strong>
              <small>years</small>
            </div>

            <div className="info-card">
              <span>BMI</span>
              <strong>{patient.bmi}</strong>
              <small>kg/m²</small>
            </div>

            <div className="info-card">
              <span>HbA1c</span>
              <strong>{patient.hba1c}%</strong>
              <small>Latest value</small>
            </div>

            <div className="info-card">
              <span>Blood Pressure</span>
              <strong>
                {patient.systolic_bp}/{patient.diastolic_bp}
              </strong>
              <small>mmHg</small>
            </div>
          </div>
        </section>

        {/* Wearable Metrics */}
        <section className="section">
          <div className="section-title">
            <h2>Real-Time Health Metrics</h2>
            <span>Wearable / Sensor Data</span>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">🩸</div>
              <div>
                <span>Glucose</span>
                <strong>
                  {wearable.glucose_mg_dl}
                  <small> mg/dL</small>
                </strong>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">❤️</div>
              <div>
                <span>Heart Rate</span>
                <strong>
                  {wearable.heart_rate_bpm}
                  <small> bpm</small>
                </strong>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🧠</div>
              <div>
                <span>HRV</span>
                <strong>
                  {wearable.hrv_ms}
                  <small> ms</small>
                </strong>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🚶</div>
              <div>
                <span>Steps</span>
                <strong>{wearable.steps}</strong>
              </div>
            </div>
          </div>
        </section>

        {/* AI Prediction and Glucose Chart */}
        <section className="prediction-layout">
          <div className="prediction-card">
            <span className="section-label">AI PREDICTION</span>
            <h2>Glucose Spike Risk</h2>

            <div
              className="risk-circle"
              style={{
                borderColor:
                  prediction.risk_level === "HIGH"
                    ? "#ff5d6c"
                    : prediction.risk_level === "MEDIUM"
                    ? "#ffc857"
                    : "#35e38a",
              }}
            >
              <strong>
                {prediction.glucose_spike_probability}%
              </strong>
              <span>Probability</span>
            </div>

            <div className="risk-result">
              <span>Risk Level</span>
              <strong className={riskClass}>
                ● {prediction.risk_level}
              </strong>
            </div>

            <div className="prediction-window">
              Prediction window:
              <strong> {prediction.prediction_window}</strong>
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-header">
              <div>
                <span className="section-label">CGM HISTORY</span>
                <h2>Glucose Trend</h2>
              </div>
              <span className="chart-unit">mg/dL</span>
            </div>

            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => [
                      `${value} mg/dL`,
                      "Glucose",
                    ]}
                  />
                  <Line
                    type="monotone"
                    dataKey="glucose"
                    stroke="#53c7e8"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p>No glucose-history readings available.</p>
            )}
          </div>
        </section>

        {/* Latest Sensor Reading */}
        <section className="latest-reading">
          <div>
            <span className="section-label">
              DIGITAL TWIN TIMESTAMP
            </span>
            <h3>{wearable.timestamp}</h3>
          </div>

          <div>
            <span>Activity</span>
            <strong>{wearable.activity_level}</strong>
          </div>

          <div>
            <span>Sleep</span>
            <strong>{wearable.sleep_hours} hrs</strong>
          </div>
        </section>

        {/* Prototype Disclaimer */}
        <footer className="disclaimer">
          <strong>Prototype Notice:</strong> GlucoTwin is a research
          prototype using synthetic data. Predictions are for demonstration
          purposes only and are not intended for clinical diagnosis or
          treatment.
        </footer>
      </main>
    </div>
  );
}

export default App;
