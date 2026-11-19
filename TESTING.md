# FoodRescue Cloud — Testing & Quality Assurance Report

## 1. Quality Assurance Strategy
The testing suite for **FoodRescue Cloud** is designed to guarantee high reliability, correct data validation, deterministic algorithm behavior, and safe state transitions during college faculty presentations and live cloud deployments.

Testing is stratified into two primary vectors:
1. **Automated Programmatic Unit Testing (`tests/test_foodrescue.py`):** Fast, reproducible regression testing covering core mathematical engines, data integrity, and state machines.
2. **Interactive Functional & Edge-Case Testing:** Systematic manual verification of the Streamlit user interface, input validation boundaries, empty dataset behavior, and CSV data export.

---

## 2. Automated Test Suite Execution Summary

The test suite runs using Python's standard `unittest` framework with zero external test harness overhead.

### Command Execution
```bash
python -m unittest tests/test_foodrescue.py
```

### Execution Output
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.928s

OK
```

### Automated Test Cases Breakdown

| Test ID | Test Method | Module Under Test | Objective / Assertion | Result |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `test_load_donations_returns_valid_dataframe` | `src.storage` | Asserts data loads as a non-empty DataFrame with all required schema columns even after cold boot. | **PASS** |
| **TC-02** | `test_generate_donation_id_format_and_uniqueness` | `src.storage` | Generates 100 consecutive IDs and verifies complete 100% uniqueness and `FR-YYYY-XXXX` format. | **PASS** |
| **TC-03** | `test_validate_donation_input_success` | `src.storage` | Verifies compliant payload passes validation with 0 errors. | **PASS** |
| **TC-04** | `test_validate_donation_input_rejections` | `src.storage` | Verifies rejection of past expiry dates, negative quantities, and unconfirmed safety checkboxes. | **PASS** |
| **TC-05** | `test_create_donation_persists_and_logs` | `src.storage` | Confirms atomic persistence to storage and corresponding audit log event creation. | **PASS** |
| **TC-06** | `test_status_workflow_lifecycle` | `src.storage` | Asserts lifecycle transitions (`Available` ➔ `Accepted` ➔ `Picked Up` ➔ `Completed`) and blocks invalid jumps. | **PASS** |
| **TC-07** | `test_scoring_dimensions` | `src.matching` | Asserts high score (>=85) for matching location, category, quantity, and urgency. | **PASS** |
| **TC-08** | `test_recommendations_ranking` | `src.matching` | Asserts recommendations are correctly sorted in descending order of algorithmic fit. | **PASS** |
| **TC-09** | `test_calculate_impact_summary` | `src.analytics` | Asserts kg-equivalent, meals, CO₂e, and water calculations match UNEP multiplier formulas. | **PASS** |
| **TC-10** | `test_empty_dataframe_impact_does_not_crash` | `src.analytics` | Confirms 0-record datasets render safe default zeros without throwing exceptions. | **PASS** |
| **TC-11** | `test_export_csv` | `src.analytics` | Asserts valid CSV serialization with proper headers and data rows. | **PASS** |

---

## 3. Manual Functional Verification Matrix

| Feature / Page | Test Scenario | Steps Executed | Expected Behavior | Actual Status |
| :--- | :--- | :--- | :--- | :--- |
| **Dashboard** | Metric Calculation | Inspected KPI metrics upon app launch | Correct counts for Total (8), Available (4), Accepted (1), Completed (2). | **VERIFIED** |
| **Dashboard** | Donut & Bar Charts | Toggled between statuses and categories | Plotly charts render responsive SVG/canvas with green/neutral color palette. | **VERIFIED** |
| **Donate Food** | Blank Required Fields | Clicked submit with empty donor and food name | Highlighted validation errors; form submission blocked. | **VERIFIED** |
| **Donate Food** | Expired Date Check | Selected a past date (yesterday) | Flagged error: "Expiry date cannot be in the past." | **VERIFIED** |
| **Donate Food** | Valid Submission | Submitted fresh 20 kg bread donation | Success banner with unique ID; instant appearance in Find Food & Dashboard. | **VERIFIED** |
| **Find Food** | Keyword Search | Searched "Rice" | Filtered list to vegetable rice meals. | **VERIFIED** |
| **Find Food** | Category Filtering | Filtered by "Fresh Produce" | Displayed only apple/orange and vegetable crates. | **VERIFIED** |
| **Find Food** | Claim by NGO | Switched to NGO role; claimed an available batch | Status updated to "Accepted"; moved to Pickup Management active tab. | **VERIFIED** |
| **Smart Matching** | Proximity & Category | Tested with Indiranagar & Cooked Meals | Ranked Indiranagar cooked meals #1 with top match badge and clear explanation. | **VERIFIED** |
| **Pickup Mgmt** | Complete Workflow | Progressed donation: Accepted ➔ Picked Up ➔ Completed | Stage indicator updated at each step; completion timestamp recorded. | **VERIFIED** |
| **Analytics** | CSV Export | Clicked "Download Donations Dataset" | Browser downloaded timestamped CSV with clean columns. | **VERIFIED** |
| **Demo Roles** | Role Switcher | Switched between Donor, NGO, Volunteer, Admin | Active role badge updated; role description shown in sidebar. | **VERIFIED** |
| **Reset Data** | Sample Restoration | Clicked "Reset Demo Sample Data" | All sample donations and audit events restored to clean baseline state. | **VERIFIED** |

---

## 4. Edge Case & Fault-Tolerance Verification
1. **Empty CSV File Handling:**
   - *Scenario:* User deletes `donations.csv` or provides an empty file with only headers.
   - *Behavior:* `load_donations()` detects the absence of data rows and automatically seeds fresh sample records.
2. **Supabase Cloud Disconnection Fallback:**
   - *Scenario:* `SUPABASE_URL` is set to an unreachable host or network drops.
   - *Behavior:* Storage adapter catches exception and seamlessly falls back to local CSV storage with a status badge.
3. **High-Concurrency ID Collision:**
   - *Scenario:* Multiple donations submitted within the same second.
   - *Behavior:* `generate_donation_id()` generates timestamp prefix combined with 4-character random hex token and checks collision against existing IDs.
