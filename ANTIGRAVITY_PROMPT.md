# Antigravity implementation prompt — FoodRescue Cloud

You are a senior Python full-stack engineer, UI/UX designer, cloud deployment mentor, and QA engineer. Open and inspect this complete project folder. Build/refine it into a polished, working college cloud-computing project named:

**FoodRescue Cloud: A Cloud-Based Food Donation, Surplus Food Management and Community Redistribution Platform**

## Goal
Create a professional Streamlit app that demonstrates how surplus food donors can publish donations and NGOs/volunteers can discover, match, accept, collect, and track them. Keep it honest: use clearly marked synthetic demo records unless a real integration is configured.

## Must-have functionality
1. Dashboard: total donations, available, accepted, completed, estimated meals rescued; charts for status/category/trends; recent records.
2. Donate Food: validated form for donor, food name, category, quantity/unit, expiry date, pickup area/time, contact (demo only), storage/allergen notes, and safety confirmation. Reject blank required fields and expiry dates before today. Do not imply food safety is certified.
3. Find Food: searchable/filterable list; cards with quantities, expiry, location, pickup window; NGO/volunteer demo mode may accept.
4. Smart Matching: explainable heuristic score using location text preference, category preference, quantity fit, and expiry urgency. Clearly label it as a rule-based prototype—not trained AI or live distance routing. Include reason and score.
5. Pickup management: Accepted → Picked Up → Completed; log each status event and actor/time.
6. Analytics: donation trend, quantity by category, statuses, rescued totals, downloadable CSV.
7. Role switcher for demo: Donor, NGO, Volunteer, Admin. It is a demo switcher, NOT real authentication. Clearly disclose.
8. About: project summary, workflow, cloud architecture concepts, limitations, responsible handling and safety disclaimers.
9. Data persistence: demo CSV backend should work reliably; isolate storage logic so Supabase can be added. If implementing Supabase, make it optional, use secrets/env, add schema/setup instructions and safe fallback demo mode. Never expose or commit credentials.
10. UI: consistent branding, responsive layout, readable contrast, sensible empty states, helpful error messages, no fake external integrations.

## Engineering requirements
- Inspect all files before editing.
- Keep a clean modular structure, Python 3.10+.
- Fix bugs, missing imports, data typing, date parsing, duplicate IDs, and empty-data edge cases.
- Use Streamlit forms and avoid needless reruns.
- Validate and sanitize user-entered values.
- Do not store real sensitive contact data in demo data.
- Use `st.cache_data` only where safe; invalidate after writes.
- Charts should be accessible and clear.
- Use stable IDs and event log entries.
- Add tests for matching logic and donation validation if practical.
- Verify all navigation pages, donation create, accept, pickup updates, analytics, reset, and export.
- Run compile/test checks and resolve all errors before finishing.
- Avoid claiming a cloud database, AI model, live location, food safety verification, or deployment is active unless it truly is.

## Cloud deployment
Prepare for Streamlit Community Cloud. Ensure root `app.py`, requirements.txt and relative imports are correct. Include README with exact GitHub upload and Streamlit Cloud deployment steps. If secrets are required, explain Streamlit Cloud Secrets format. Keep demo mode usable without secrets.

## Final deliverables
1. Finished working app and all source files.
2. Updated README with local setup, demo workflow, architecture, cloud deployment, and limitations.
3. `ARCHITECTURE.md` describing browser → Streamlit Cloud → application modules → CSV demo / optional Supabase → analytics.
4. `TESTING.md` with test checklist and actual checks run.
5. If possible, a simple architecture diagram using Mermaid in Markdown.
6. Final response summarizing files changed, features, how to run, how to deploy, tests run, and any limitations.

Do the work directly in the project. Do not just give suggestions or a plan. Start by examining the files, then implement, run, test, and fix.
