# 🥗 FoodRescue Cloud
### A Cloud-Based Food Donation, Surplus Food Management & Community Redistribution Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg?logo=plotly&logoColor=white)](https://plotly.com/)
[![Database](https://img.shields.io/badge/Storage-Dual%20Mode%20(CSV%20%2B%20Supabase)-16a34a.svg)](https://supabase.com/)
[![Testing](https://img.shields.io/badge/Tests-11%2F11%20Passing-brightgreen.svg)](TESTING.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📌 Project Overview
**FoodRescue Cloud** is a modern, cloud-native web platform engineered to eliminate urban food waste and address local food insecurity. It provides a real-time bridge connecting food generators (restaurants, bakeries, corporate dining halls, canteens) with community redistribution networks (NGOs, community kitchens, shelters, and volunteer drivers).

Built for a **College Cloud Computing Project**, it demonstrates cloud application design, multi-tier software architecture, Platform-as-a-Service (PaaS) hosting on **Streamlit Community Cloud**, explainable rule-based decision support, and pluggable persistence (local CSV demo mode with seamless cloud **Supabase PostgreSQL** scalability).

---

## 🌟 Key Features

### 1. 🎨 Modern Food-Tech SaaS Design System
- Sleek green, white, and neutral color palette (`#16a34a`, `#ffffff`, `#f8fafc`, `#0f172a`).
- Responsive layouts for laptops, tablets, and smartphones.
- Informative KPI metric cards with hover animations.
- Custom status badges and category pills.
- Friendly, accessible empty states and confirmation alerts.

### 2. 📊 Executive Impact Dashboard
- Real-time KPIs: Total Donations, Available Batches, Accepted Claims, Completed Deliveries.
- Environmental Impact Index: Rescued kg-equivalent, Estimated Meals Saved, CO₂e greenhouse gas emissions prevented, and Agricultural Fresh Water conserved (UNEP & WRAP formulas).
- Visual charts: Donation status donut chart, surplus by food category, and cumulative growth timeline.
- Recent listings feed with expiry urgency tags.

### 3. 🍱 Food Donation Management Module
- Comprehensive submission form for surplus food donors.
- Captures food title, category, quantity, measurement units, and use-by dates.
- Logistics details: pickup area, pickup time window, storage temperature requirements, allergen disclosures, and dispatch contact info.
- Strict input validation: prevents past expiry dates, negative quantities, and missing fields.
- Immediate network synchronization across all modules.

### 4. 🔍 Find Food (NGO & Volunteer Portal)
- Instant keyword search across food titles, descriptions, and donor names.
- Multi-dimensional filters: category selection, geographic area/city filtering, and sorting by urgency, quantity, or newest listings.
- Rich details view: storage requirements, allergen warnings, and donor instructions.
- 1-click donation acceptance with customized claim notes.

### 5. 🤖 Explainable Smart Food Matching Engine
- Multi-criteria recommendation algorithm that ranks available donations for NGOs on a transparent **0 to 100 point scale**:
  - **Location Proximity (30%)**
  - **Category Alignment (25%)**
  - **Quantity Fulfillment (25%)**
  - **Rescue Urgency / Expiry (20%)**
- Fully explainable: provides plain-language reasons and point breakdowns for every recommendation.
- Explicitly documented as a **transparent rule-based heuristic prototype** (non-black-box AI).

### 6. 🚚 Pickup Lifecycle Workflow
- State machine tracking food through 4 stages:
  $$\text{Available} \longrightarrow \text{Accepted} \longrightarrow \text{Picked Up (In Transit)} \longrightarrow \text{Completed}$$
- Visual 4-stage stepper showing progress in real-time.
- Captures volunteer names, vehicle details, and delivery confirmation notes.
- Immutable system audit event log recording every state transition with timestamp and actor.

### 7. 📈 Analytics, Reporting & CSV Export
- Interactive Plotly visualizations for donor contributions, NGO claims, and category distributions.
- 1-click downloadable CSV dataset for faculty evaluation, grading, and external data audits.

### 8. 🎭 Multi-Persona Demo Role Switcher
- Fast sidebar role switcher simulating **Donor**, **NGO**, **Volunteer**, and **Admin** personas.
- Transparently labeled as educational role simulation (noting how commercial applications would integrate OAuth 2.0 / JWT).

### 9. ☁️ Dual Storage Backend (CSV + Supabase PostgreSQL)
- **Zero-Setup Mode:** Automatically persists to `data/donations.csv` and `data/events.csv` with built-in auto-seeding if files are missing or empty.
- **Enterprise Cloud Mode:** Integrates seamlessly with **Supabase PostgreSQL** when credentials are provided in `.streamlit/secrets.toml` or environment variables.
- Built-in graceful degradation: falls back to local storage if the database is unreachable.

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Client["Client Tier"]
        Browser[Web Browser / Mobile Viewport]
    end

    subgraph PaaS["Cloud Platform as a Service (PaaS)"]
        StreamlitCloud[Streamlit Community Cloud Container]
        UI[Custom SaaS UI / Responsive CSS]
        Router[Page Navigation & Role Switcher]
    end

    subgraph Core["Application Business Logic"]
        Validator[Data Validator & Unique ID Generator]
        StateMachine[Status State Machine: Available -> Accepted -> Picked Up -> Completed]
        MatchingEngine[Explainable Heuristic Matcher: Location + Category + Qty + Urgency]
        AnalyticsEngine[Plotly Visualizations & UNEP Impact Calculations]
    end

    subgraph Storage["Decoupled Storage Layer"]
        StorageAdapter[Storage Backend Adapter (src/storage.py)]
        LocalCSV[(Local CSV Mode: data/donations.csv)]
        CloudSupabase[(Cloud Supabase PostgreSQL Database)]
    end

    Browser <--> StreamlitCloud
    StreamlitCloud --> UI --> Router
    Router --> Validator --> StateMachine
    Router --> MatchingEngine
    Router --> AnalyticsEngine
    StateMachine --> StorageAdapter
    MatchingEngine --> StorageAdapter
    AnalyticsEngine --> StorageAdapter
    StorageAdapter -->|Default / Fallback| LocalCSV
    StorageAdapter -->|Configured Secrets| CloudSupabase
```

*For in-depth architectural details, sequence diagrams, and design patterns, see [ARCHITECTURE.md](ARCHITECTURE.md).*

---

## 🚀 Quickstart: Running Locally

### Prerequisites
- **Python 3.10+** installed on your system.

### Step 1: Clone or Navigate to the Project
```bash
cd FoodRescue_Cloud
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

## 🧪 Running the Automated Test Suite

The project includes an automated test suite verifying data validation, unique ID generation, lifecycle transitions, the recommendation engine, and impact calculations:

```bash
python -m unittest tests/test_foodrescue.py
```

*Output:*
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.928s

OK
```
*For complete testing documentation and manual test matrices, see [TESTING.md](TESTING.md).*

---

## ☁️ Deployment Guide: Streamlit Community Cloud

Deploying FoodRescue Cloud online for your college demonstration takes less than 3 minutes:

### Step 1: Push Project to GitHub
1. Create a new GitHub repository (e.g. `foodrescue-cloud`).
2. Initialize and push your code:
```bash
git init
git add .
git commit -m "Initial commit of FoodRescue Cloud"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/foodrescue-cloud.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<YOUR_USERNAME>/foodrescue-cloud`.
4. Set the **Branch** to `main`.
5. Set the **Main file path** to `app.py`.
6. Click **"Deploy!"**.

### Step 3 (Optional): Connecting Cloud Supabase PostgreSQL
1. Create a free database at **[supabase.com](https://supabase.com)**.
2. Open the **SQL Editor** in Supabase and paste the contents of `supabase_schema.sql`, then click **Run**.
3. In your Streamlit Cloud app dashboard, click **Settings** ➔ **Secrets**.
4. Add your database credentials:
```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```
5. Click **Save**. The app will automatically detect Supabase and switch from CSV to Cloud PostgreSQL!

---

## 🎓 Faculty Presentation & Viva Guide

### Frequently Asked Viva Questions & Model Answers

**Q1: What cloud deployment model and service category does this project belong to?**  
> *"FoodRescue Cloud utilizes the **Platform as a Service (PaaS)** model hosted on Streamlit Community Cloud. The underlying container lifecycle, TLS termination, CDN distribution, and continuous deployment are managed automatically by the PaaS infrastructure, allowing us to focus on application logic and data decoupling."*

**Q2: How does the application maintain resilience against database downtime?**  
> *"We implemented an **Adapter Pattern** with graceful degradation in `src/storage.py`. If the remote Supabase PostgreSQL database becomes unreachable or is not configured, the platform automatically falls back to local CSV storage without throwing unhandled exceptions or interrupting user workflows."*

**Q3: How does the Smart Matching algorithm make recommendations?**  
> *"It is an **explainable rule-based scoring engine** that assigns up to 100 points based on four deterministic dimensions: Location Proximity (30 pts), Food Category Alignment (25 pts), Quantity Fulfillment (25 pts), and Expiry Urgency (20 pts). Every point awarded is backed by plain-language explanations visible in the UI."*

**Q4: How do you prevent data corruption during state changes?**  
> *"Donation status transitions follow a strict unidirectional state machine (`Available` ➔ `Accepted` ➔ `Picked Up` ➔ `Completed`). Every status transition atomically updates the record and logs an immutable audit event in `events.csv` / `events` table with the actor's identity and timestamp."*

---

## 📁 Repository File Structure

```text
FoodRescue_Cloud/
├── .streamlit/
│   └── config.toml             # Streamlit visual theme and server settings
├── data/
│   ├── donations.csv           # Persistent donations CSV dataset
│   └── events.csv              # Immutable event audit log
├── src/
│   ├── __init__.py             # Package initializer
│   ├── config.py               # Constants, categories, roles, and impact multipliers
│   ├── storage.py              # Dual-backend storage layer (CSV + Supabase)
│   ├── matching.py             # Explainable heuristic recommendation engine
│   ├── analytics.py            # Plotly visualizations & UNEP impact calculations
│   └── ui.py                   # Custom CSS styling, header, and UI components
├── tests/
│   ├── __init__.py             # Test package initializer
│   └── test_foodrescue.py      # Automated unit test suite (11 test cases)
├── app.py                      # Main application entry point
├── ARCHITECTURE.md             # In-depth cloud architecture and Mermaid diagrams
├── TESTING.md                  # Test reports, execution logs, and QA checklists
├── supabase_schema.sql         # Production PostgreSQL DDL schema with RLS & seed data
├── requirements.txt            # Python package dependencies
├── .env.example                # Example environment variable template
├── .gitignore                  # Git ignore rules for virtual environments & secrets
└── README.md                   # Project documentation and presentation guide
```

---

## ⚖️ Ethical & Educational Disclaimers
- **Classroom Prototype:** This platform is an academic engineering demonstration. Sample records are synthetic illustrative data.
- **Role Switcher Notice:** The sidebar role switcher is an interactive simulation for demonstration purposes; commercial deployments would implement OAuth 2.0 / OpenID Connect with multi-factor authentication (MFA).
- **Food Safety:** The application facilitates logistics and communications but does not perform microbiological testing. Commercial deployments must incorporate certified food safety inspection protocols (e.g., FSSAI / FDA standards).
