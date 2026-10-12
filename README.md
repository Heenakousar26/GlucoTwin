# GlucoTwin — Personalized Glucose Digital Twin

## 1. Project Overview

GlucoTwin is a personalized glucose digital twin prototype designed to explore how electronic health records (EHR) and wearable-device data can be combined to monitor glucose patterns and estimate glucose-related risk.

The application provides an interactive dashboard where users can select a patient and a date/time to view health information, wearable readings, glucose history, and a machine-learning prediction.

**Important:** This is an educational prototype built using synthetic data. Its predictions are not clinically validated and must not be used for medical diagnosis or treatment decisions.

## 2. Team Details

- **Team Leader:** KOLIMI HEENA KOUSAR
- **Team Member:** SHAIK BABA SHAREEF
- **College:** MADANAPALLE INSTITUE OF TECHNOLOGY & SCIENCE
- **Incubator:** N/A

Update this section with the actual team and institutional details before submission.

## 3. Problem Statement

Glucose levels can change over time depending on several factors, including physical activity, sleep, heart rate, and a person's existing health profile. Viewing these measurements separately can make it difficult to understand changing patterns.

GlucoTwin combines patient information and time-based wearable data in a single dashboard to demonstrate how a digital twin could support personalized health-data exploration.

## 4. Proposed Solution

GlucoTwin provides the following features:

- **Patient Selection:** Switch between multiple synthetic patient profiles.
- **Health Profile:** View available age, gender, BMI, HbA1c, blood pressure, and medication information.
- **Time-Based Monitoring:** Select a date and time to inspect available patient data.
- **Glucose History:** Explore glucose readings over time.
- **Risk Prediction:** Display a machine-learning model's estimated output.
- **Interactive Dashboard:** Present patient information, metrics, and glucose-related trends in one place.

## 5. Healthcare Use Case

Consider a hypothetical user exploring glucose-related information for a selected patient profile.

The user can select a patient, review available health information, choose a time, inspect glucose trends, and view the machine-learning output. This allows the user to explore the available data through one interface rather than reviewing separate files.

This prototype demonstrates a possible workflow for personalized health-data monitoring and analysis. It does not provide medical advice, diagnose diseases, or recommend treatments.

## 6. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, CSS |
| Charts | Recharts |
| Backend | Python, FastAPI |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, Random Forest |
| Model Storage | Joblib, Pickle |
| Data Storage | CSV files |
| Development Tools | VS Code, Git, GitHub |

## 7. System Architecture

The application follows a frontend-backend architecture with a machine-learning component.

1. The user interacts with the React dashboard and selects a patient and date/time.
2. The frontend communicates with the FastAPI backend through API requests.
3. The backend retrieves the relevant patient and wearable data from CSV files.
4. The backend loads the trained Random Forest model when required by the prediction workflow.
5. The model generates an output using the features provided by the implemented workflow.
6. The backend returns the relevant data and model output to the frontend.
7. The dashboard displays patient information, health metrics, glucose trends, and the model output.

### Architecture Diagram

The separate architecture diagram is provided in the project documentation:

- **Architecture File:** [Add the GitHub link to your architecture PDF or PPT]

## 8. Dataset

The prototype uses synthetic data generated for demonstration purposes.

### Electronic Health Records

**File:** `data/ehr/ehr_data.csv`

The dataset includes fields such as:

- Patient ID
- Age and gender
- BMI and HbA1c
- Diabetes duration
- Systolic and diastolic blood pressure
- Family history
- Medication

### Wearable Data

**File:** `data/wearable/wearable_data.csv`

The dataset includes:

- Patient ID and timestamp
- Glucose level
- Heart rate
- Heart-rate variability (HRV)
- Steps
- Sleep duration
- Activity level

The generated wearable dataset contains 10 synthetic patient profiles with readings at 30-minute intervals over seven days.

These records are synthetic and do not represent actual patients.

## 9. Machine-Learning Workflow

The project demonstrates the following machine-learning workflow:

1. Prepare the wearable dataset.
2. Generate a prediction target based on future glucose readings.
3. Train a Random Forest classification model.
4. Save the trained model.
5. Load the model in the FastAPI backend.
6. Use the data selected by the application's prediction workflow to generate a model output.
7. Display the output on the dashboard.

The model's output depends on the training data, selected input features, and implementation. It should not be interpreted as a clinically validated probability.

### Model and Framework Details

- **Algorithm:** Random Forest Classification
- **Language:** Python
- **ML Framework:** Scikit-learn
- **Data Processing:** Pandas and NumPy
- **Model Persistence:** Joblib/Pickle

## 10. Project Structure

```text
GlucoTwin/
├── backend/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── ml-model/
│   ├── create_prediction_target.py
│   ├── train_model.py
│   └── glucotwin_model.pkl
├── data/
│   ├── ehr/
│   │   └── ehr_data.csv
│   └── wearable/
│       ├── generate_wearable_data.py
│       ├── wearable_data.csv
│       └── wearable_with_target.csv
├── docs/
│   ├── GlucoTwin_Architecture.pdf
│   └── GlucoTwin_Presentation.pptx
├── screenshots/
├── README.md
├── LICENSE
└── .gitignore
```

The documentation filenames above are examples. Replace them with the actual uploaded filenames if they differ.

## 11. Installation and Execution

### Prerequisites

Install the following tools:

- Python 3.11 or another compatible Python version
- Node.js and npm
- Visual Studio Code
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Heenakousar26/GlucoTwin.git
cd GlucoTwin
```

### Step 2: Start the Backend

Open a terminal in VS Code.

```bash
cd backend
```

Create a virtual environment if one does not already exist:

```powershell
python -m venv venv
```

Activate it in Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn scipy joblib
```

Start the backend:

```bash
python -m uvicorn main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### Step 3: Start the Frontend

Open a second terminal in VS Code.

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend URL: `http://localhost:5173/`

Keep both terminal processes running while using the application.

**Note:** The backend expects the CSV files and trained model to be available at their configured paths. The frontend also requires the backend to be running. Follow the project's configured file paths if they differ from these examples.

## 12. Demo Video

Watch the GlucoTwin project demonstration:

**YouTube Demo:** [https://youtu.be/IyU7GZr4eVs]

The demonstration covers the dashboard, patient profile selection, health metrics, glucose trends, date/time controls, and machine-learning component.

The video is shared as an unlisted YouTube video for evaluation.

## 13. API Endpoints

The backend provides the following endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Check backend health |
| `GET /api/patients` | Retrieve the patient list |
| `GET /api/patients/{patient_id}` | Retrieve a patient's profile |
| `GET /api/patients/{patient_id}/prediction?timestamp=...` | Obtain a prediction for a selected timestamp |
| `GET /api/dashboard/{patient_id}?timestamp=...` | Retrieve dashboard information |
| `GET /api/patients/{patient_id}/timestamps` | Retrieve available timestamps |
| `GET /api/patients/{patient_id}/glucose-history?timestamp=...` | Retrieve glucose history |

Endpoint availability and query parameters should match the implementation in `backend/main.py`.

## 14. Project Presentation

The project presentation summarizes the problem statement, proposed solution, system architecture, technology stack, machine-learning workflow, demonstration, limitations, and future scope.

- **Presentation File:** [Add the GitHub link to your presentation PDF or PPT]

## 15. Open-Source License

This project is intended to be shared for educational and demonstration purposes.

**License:** [Enter the license actually selected for this repository]

The full license terms are available in the `LICENSE` file at the root of the repository.

Do not claim a particular open-source license until the corresponding license file has been added.

## 16. Future Enhancements

Possible future improvements include:

- Integrate real wearable devices and authorized health records.
- Evaluate the model using appropriate patient-level data splits and independent datasets.
- Improve prediction reliability and model explainability.
- Add authentication, patient consent, and secure data handling.
- Introduce personalized trend analysis and clinician-facing reports.
- Evaluate the prototype with healthcare professionals before any clinical use.

## 17. Conclusion

GlucoTwin demonstrates a prototype approach to personalized glucose monitoring by combining synthetic electronic health records, wearable time-series data, a machine-learning model, and an interactive web dashboard.

The project provides a foundation for exploring digital twins in healthcare while highlighting the importance of data privacy, independent validation, and clinical evaluation before real-world deployment.

## Disclaimer

GlucoTwin is an educational prototype that uses synthetic data. It is not a medical device and does not provide medical advice, diagnosis, or treatment recommendations.
