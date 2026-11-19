"""
FoodRescue Cloud - Main Application Entrypoint
A Cloud-Based Food Donation, Surplus Food Management & Community Redistribution Platform.

Designed for college cloud-computing demonstration and Streamlit Community Cloud deployment.
"""

from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

from src.analytics import (
    calculate_impact_summary,
    create_category_bar_chart,
    create_donor_leaderboard,
    create_ngo_activity_chart,
    create_status_donut_chart,
    create_timeline_chart,
    export_donations_csv,
)
from src.config import (
    ALLERGEN_OPTIONS,
    APP_ICON,
    APP_SUBTITLE,
    APP_TITLE,
    APP_VERSION,
    DEMO_ROLES,
    FOOD_CATEGORIES,
    PICKUP_WINDOWS,
    PRIMARY_GREEN,
    QUANTITY_UNITS,
    ROLE_ADMIN,
    ROLE_DESCRIPTIONS,
    ROLE_DONOR,
    ROLE_NGO,
    ROLE_VOLUNTEER,
    STATUS_ACCEPTED,
    STATUS_AVAILABLE,
    STATUS_COMPLETED,
    STATUS_PICKED_UP,
    STATUS_CANCELLED,
    STORAGE_CONDITIONS,
)
from src.matching import get_recommendations, score_donation_match
from src.storage import (
    create_donation,
    get_storage_backend_info,
    load_donations,
    load_events,
    reset_all_data,
    save_donations,
    save_events,
    update_donation_status,
)
from src.ui import (
    check_urgency,
    inject_custom_css,
    render_empty_state,
    render_header,
    render_status_pill,
    render_workflow_stepper,
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_TITLE} — Surplus Redistribution",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom design system CSS
inject_custom_css()

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "donations" not in st.session_state:
    st.session_state.donations = load_donations()
if "events" not in st.session_state:
    st.session_state.events = load_events()
if "active_role" not in st.session_state:
    st.session_state.active_role = ROLE_NGO

df = st.session_state.donations
events = st.session_state.events
storage_info = get_storage_backend_info()

# ---------------------------------------------------------
# Sidebar Navigation & Role Switcher
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 2rem;">{APP_ICON}</span>
            <div>
                <h2 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #166534;">{APP_TITLE}</h2>
                <p style="margin: 0; font-size: 0.75rem; color: #64748b; font-weight: 600;">v{APP_VERSION} • Cloud Edition</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation Menu",
        [
            "📊 Dashboard",
            "🍱 Donate Food",
            "🔍 Find Food",
            "🤖 Smart Matching",
            "🚚 Pickup Management",
            "📈 Analytics & Reports",
            "☁️ Cloud Architecture",
            "ℹ️ About & Viva Guide",
        ],
        index=0,
    )

    st.divider()

    # Demo Role Switcher
    st.markdown("#### 🎭 Demo Role Switcher")
    st.caption("Simulate different ecosystem actors. (Educational simulation mode, not live RBAC authentication).")

    selected_role = st.selectbox(
        "Current Active Role",
        DEMO_ROLES,
        index=DEMO_ROLES.index(st.session_state.active_role),
    )
    if selected_role != st.session_state.active_role:
        st.session_state.active_role = selected_role
        st.rerun()

    st.info(f"**{selected_role} Mode:** {ROLE_DESCRIPTIONS[selected_role]}")

    st.divider()

    # Quick summary metric badge in sidebar
    avail_count = int((df["status"] == STATUS_AVAILABLE).sum()) if not df.empty else 0
    rescued_count = int((df["status"].isin([STATUS_PICKED_UP, STATUS_COMPLETED])).sum()) if not df.empty else 0
    st.markdown(
        f"""
        <div style="background: #f1f5f9; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 0.85rem;">
            <div style="color: #64748b; font-weight: 600; margin-bottom: 4px;">SYSTEM SNAPSHOT</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                <span>🟢 Available:</span> <strong>{avail_count}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>🤝 Rescued:</span> <strong>{rescued_count}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Demo sample data reset
    if st.button("↻ Reset Demo Sample Data", use_container_width=True, help="Restores fresh sample records and events"):
        reset_all_data()
        st.session_state.donations = load_donations(reset=True)
        st.session_state.events = load_events()
        st.toast("Sample records and activity audit restored!", icon="✅")
        st.rerun()

# Global App Header
render_header(role=st.session_state.active_role, storage_info=storage_info)


# =========================================================
# PAGE 1: DASHBOARD
# =========================================================
if page == "📊 Dashboard":
    impact = calculate_impact_summary(df)

    # Key Metrics Bar
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Listed", impact["total_donations"], help="All food donations registered in the system")
    m2.metric("Available Now", impact["available_donations"], help="Open batches ready for immediate NGO collection")
    m3.metric("Accepted", impact["accepted_donations"], help="Claimed by NGOs, awaiting volunteer transit")
    m4.metric("Completed", impact["completed_donations"], help="Successfully redistributed and delivered")
    m5.metric("Food Rescued", f"{impact['rescued_kg_equivalent']:g} kg", help="Total kg-equivalent saved from landfills")
    m6.metric("Meals Saved", f"{impact['meals_saved']:,}", help="Nutritious meal servings provided (at 400g/portion)")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Environmental Impact Callout
    st.markdown(
        f"""
        <div class="impact-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #14532d;">
                        🌍 Verified Ecological Dividend (UNEP Benchmark Assumptions)
                    </h3>
                    <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #15803d;">
                        By intercepting surplus edible food before organic landfill decay, FoodRescue Cloud prevents methane emissions and conserves natural resources.
                    </p>
                </div>
                <div style="display: flex; gap: 24px;">
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #14532d;">~{impact['co2_prevented_kg']:g} kg</div>
                        <div style="font-size: 0.78rem; font-weight: 600; color: #166534;">CO₂e EMISSIONS AVOIDED</div>
                    </div>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #14532d;">~{impact['water_saved_liters']:,.0f} L</div>
                        <div style="font-size: 0.78rem; font-weight: 600; color: #166534;">WATER FOOTPRINT SAVED</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main Visualizations Row
    c1, c2 = st.columns([1, 1])

    with c1:
        with st.container(border=True):
            st.markdown("#### 🍩 Donation Status Breakdown")
            st.plotly_chart(create_status_donut_chart(df), use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("#### 🍱 Surplus by Food Category")
            st.plotly_chart(create_category_bar_chart(df), use_container_width=True)

    # Activity Timeline
    with st.container(border=True):
        st.markdown("#### 📈 Donation Submission & Cumulative Growth Timeline")
        st.plotly_chart(create_timeline_chart(df), use_container_width=True)

    # Recent Donations Cards
    st.markdown("### 🕒 Recent Food Listings")
    if df.empty:
        render_empty_state("No Donations Found", "Be the first to list surplus food to begin community redistribution.", "🍱")
    else:
        recent = df.sort_values("created_at", ascending=False).head(5)
        for _, row in recent.iterrows():
            is_urgent, urg_label = check_urgency(row["expiry"])
            urgency_html = f'<span class="urgent-pill">⏳ {urg_label}</span>' if is_urgent else ""

            with st.container(border=True):
                r_col1, r_col2 = st.columns([3, 1])
                with r_col1:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <h4 style="margin: 0; font-weight: 700;">{row['food_name']}</h4>
                            <span class="category-pill">{row['category']}</span>
                            {render_status_pill(row['status'])}
                            {urgency_html}
                        </div>
                        <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.88rem;">
                            🏢 <strong>Donor:</strong> {row['donor_name']} &nbsp;|&nbsp; 📍 <strong>Location:</strong> {row['location']} &nbsp;|&nbsp; 🕒 <strong>Pickup:</strong> {row['pickup_window']}
                        </p>
                        <p style="margin: 0; color: #64748b; font-size: 0.85rem;">{row['description'] or 'No additional description provided.'}</p>
                        """,
                        unsafe_allow_html=True,
                    )
                with r_col2:
                    st.metric("Quantity", f"{row['quantity']:g} {row['unit']}")
                    st.caption(f"Expires: **{row['expiry']}**")


# =========================================================
# PAGE 2: DONATE FOOD MODULE
# =========================================================
elif page == "🍱 Donate Food":
    st.markdown("## 🍱 List Surplus Food Donation")
    st.markdown(
        "Publish surplus prepared meals, bakery items, or fresh produce for nearby verified NGOs, community kitchens, and shelters."
    )

    if st.session_state.active_role != ROLE_DONOR:
        st.info(
            f"💡 **Demo Note:** You are in **{st.session_state.active_role}** mode. In this prototype, all roles can submit donations for easy faculty demonstration.",
            icon="ℹ️",
        )

    with st.form("donation_submission_form", clear_on_submit=False):
        st.markdown("#### 1. Donor & Food Specifics")
        col1, col2 = st.columns(2)

        with col1:
            donor_name = st.text_input(
                "Donor or Organization Name *",
                value="City Central Cafeteria" if st.session_state.active_role == ROLE_DONOR else "",
                placeholder="e.g. Green Leaf Cafe, Campus Dining Hall, Banquet Center",
                help="Legal name of business, restaurant, or individual contributor.",
            )
            category = st.selectbox(
                "Food Category *",
                FOOD_CATEGORIES,
                index=0,
                help="Categorization ensures suitable cold-chain or thermal transit.",
            )
            quantity = st.number_input(
                "Quantity *",
                min_value=0.5,
                max_value=5000.0,
                value=15.0,
                step=1.0,
                help="Estimated portion count or weight.",
            )

        with col2:
            food_name = st.text_input(
                "Food Title / Item Description *",
                placeholder="e.g. Fresh Vegetable Pulav & Raita, Whole Wheat Loaves",
                help="Clear name of prepared or packaged items.",
            )
            unit = st.selectbox(
                "Measurement Unit *",
                QUANTITY_UNITS,
                index=0,
                help="Select kg for bulk produce/bakery, meals for individual plates.",
            )
            expiry_date = st.date_input(
                "Safe Consumption / Use-By Date *",
                min_value=date.today(),
                value=date.today() + timedelta(days=1),
                help="Food cannot be listed past its safe consumption window.",
            )

        st.markdown("#### 2. Logistics & Safe Handling")
        col3, col4 = st.columns(2)

        with col3:
            location = st.text_input(
                "Pickup Location / Area Address *",
                placeholder="e.g. Koramangala 5th Block, Bengaluru",
                help="Precise pickup neighborhood or premises for NGO dispatch.",
            )
            pickup_window = st.selectbox(
                "Pickup Time Window *",
                PICKUP_WINDOWS,
                index=1,
            )

        with col4:
            storage_conditions = st.selectbox(
                "Storage & Temperature Requirement *",
                STORAGE_CONDITIONS,
                index=0,
            )
            allergens = st.selectbox(
                "Allergen Disclosure *",
                ALLERGEN_OPTIONS,
                index=0,
                help="Crucial safety detail for vulnerable community recipients.",
            )

        contact = st.text_input(
            "Demo Dispatch Contact Info",
            value="dispatch@centralcanteen.demo",
            placeholder="Phone number or email for pickup coordination",
            help="For demo purposes only; synthetic contacts recommended.",
        )

        description = st.text_area(
            "Packaging & Storage Notes",
            placeholder="Describe containers (e.g. food-grade insulated trays), handling advice, and gate entry instructions.",
            help="Helps the collecting NGO bring appropriate transport containers.",
        )

        st.markdown("#### 3. Certification of Food Quality")
        confirmation = st.checkbox(
            "✅ I confirm that this surplus food is wholesome, stored in accordance with sanitary safety guidelines, and the listed details are true and accurate.",
            value=False,
        )

        submitted = st.form_submit_button(
            "🚀 Publish Food Donation to Network",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        payload = {
            "donor_name": donor_name,
            "food_name": food_name,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "expiry": expiry_date.strftime("%Y-%m-%d"),
            "location": location,
            "pickup_window": pickup_window,
            "storage_conditions": storage_conditions,
            "allergens": allergens,
            "contact": contact,
            "description": description,
            "confirmed": confirmation,
        }

        success, msg, created = create_donation(payload, actor=st.session_state.active_role)
        if success and created:
            st.session_state.donations = load_donations()
            st.session_state.events = load_events()
            st.balloons()
            st.success(
                f"🎉 **Donation Registered Successfully!** Generated Tracking ID: `{created['id']}`. "
                "This donation is now immediately discoverable in **Find Food** and eligible for **Smart Matching**.",
                icon="✅",
            )
        else:
            st.error(f"⚠️ **Validation Failed:** {msg}", icon="🚨")


# =========================================================
# PAGE 3: FIND FOOD MODULE
# =========================================================
elif page == "🔍 Find Food":
    st.markdown("## 🔍 Available Food Donations")
    st.markdown(
        "Browse surplus batches ready for collection. Filter by proximity, category, or expiry urgency."
    )

    available_df = df[df["status"] == STATUS_AVAILABLE].copy() if not df.empty else pd.DataFrame()

    # Search & Filter Controls
    with st.container(border=True):
        st.markdown("##### 🔎 Filter & Search Donations")
        f1, f2, f3, f4 = st.columns([2, 1.5, 1.5, 1.5])

        with f1:
            search_query = st.text_input("Search food name or description", placeholder="e.g. Rice, Bread, Organic").strip().lower()

        with f2:
            all_cats = ["All Categories"] + FOOD_CATEGORIES
            selected_cat = st.selectbox("Category", all_cats, index=0)

        with f3:
            area_query = st.text_input("Filter by Area / City", placeholder="e.g. Indiranagar, Bengaluru").strip().lower()

        with f4:
            sort_option = st.selectbox(
                "Sort Results",
                [
                    "Expiry: Soonest First (Urgent)",
                    "Quantity: Highest First",
                    "Newest Listed",
                ],
            )

    # Apply filters
    filtered = available_df.copy()
    if not filtered.empty:
        if search_query:
            filtered = filtered[
                filtered["food_name"].str.lower().str.contains(search_query, na=False)
                | filtered["description"].str.lower().str.contains(search_query, na=False)
                | filtered["donor_name"].str.lower().str.contains(search_query, na=False)
            ]

        if selected_cat != "All Categories":
            filtered = filtered[filtered["category"] == selected_cat]

        if area_query:
            filtered = filtered[filtered["location"].str.lower().str.contains(area_query, na=False)]

        # Sorting
        if sort_option == "Expiry: Soonest First (Urgent)":
            filtered = filtered.sort_values("expiry", ascending=True)
        elif sort_option == "Quantity: Highest First":
            filtered = filtered.sort_values("quantity", ascending=False)
        elif sort_option == "Newest Listed":
            filtered = filtered.sort_values("created_at", ascending=False)

    st.caption(f"Showing **{len(filtered)}** available donation(s) ready for rescue.")

    if filtered.empty:
        render_empty_state(
            "No Matching Donations Found",
            "Try broadening your search keywords, clearing area filters, or switch categories.",
            "🔍",
        )
    else:
        for _, row in filtered.iterrows():
            d_id = row["id"]
            is_urgent, urg_label = check_urgency(row["expiry"])
            urgency_html = f'<span class="urgent-pill">⏳ {urg_label}</span>' if is_urgent else ""

            with st.container(border=True):
                c_top1, c_top2 = st.columns([3, 1])

                with c_top1:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px;">
                            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a;">{row['food_name']}</h3>
                            <span class="category-pill">{row['category']}</span>
                            {render_status_pill(row['status'])}
                            {urgency_html}
                            <span style="font-size: 0.78rem; color: #94a3b8; font-family: monospace;">#{d_id}</span>
                        </div>
                        <div style="color: #475569; font-size: 0.88rem; margin-bottom: 8px;">
                            🏢 <strong>Donor:</strong> {row['donor_name']} &nbsp;|&nbsp; 📍 <strong>Location:</strong> {row['location']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with c_top2:
                    st.metric("Available Portion", f"{row['quantity']:g} {row['unit']}")

                # Details Row
                q1, q2, q3, q4 = st.columns(4)
                q1.caption(f"📅 **Use-By Date:** {row['expiry']}")
                q2.caption(f"⏰ **Pickup Window:** {row['pickup_window']}")
                q3.caption(f"❄️ **Storage:** {row.get('storage_conditions', 'Standard')}")
                q4.caption(f"⚠️ **Allergens:** {row.get('allergens', 'None')}")

                if row.get("description"):
                    st.markdown(
                        f"""
                        <div style="background: #f8fafc; padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; color: #475569; margin: 8px 0; border: 1px solid #f1f5f9;">
                            📝 <em>{row['description']}</em>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Claim / Accept Action
                with st.expander(f"🤝 Claim / Accept this Donation ({d_id})", expanded=False):
                    if st.session_state.active_role in [ROLE_NGO, ROLE_VOLUNTEER, ROLE_ADMIN]:
                        claim_col1, claim_col2 = st.columns([2, 1])
                        with claim_col1:
                            org_name = st.text_input(
                                "Claiming Organization / Recipient Name",
                                value="Community Kitchen Network" if st.session_state.active_role == ROLE_NGO else f"Volunteer {st.session_state.active_role}",
                                key=f"claim_org_{d_id}",
                            )
                            claim_notes = st.text_input(
                                "Collection Notes (Vehicle, ETA, Dispatch details)",
                                placeholder="e.g. Volunteer van arriving in 45 mins",
                                key=f"claim_note_{d_id}",
                            )
                        with claim_col2:
                            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
                            if st.button("Confirm Acceptance", key=f"btn_accept_{d_id}", type="primary", use_container_width=True):
                                ok, msg = update_donation_status(
                                    donation_id=d_id,
                                    new_status=STATUS_ACCEPTED,
                                    actor_name=org_name.strip() or st.session_state.active_role,
                                    actor_role=st.session_state.active_role,
                                    note=claim_notes.strip(),
                                )
                                if ok:
                                    st.session_state.donations = load_donations()
                                    st.session_state.events = load_events()
                                    st.success(f"Donation {d_id} accepted! Status transitioned to 'Accepted'.")
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.warning(
                            f"You are currently in **{st.session_state.active_role}** mode. "
                            "Switch your demo role to **NGO**, **Volunteer**, or **Admin** in the sidebar to claim donations.",
                            icon="🔒",
                        )


# =========================================================
# PAGE 4: SMART FOOD MATCHING
# =========================================================
elif page == "🤖 Smart Matching":
    st.markdown("## 🤖 Explainable Smart Food Matching Engine")
    st.markdown(
        "A transparent, multi-criteria recommendation algorithm that connects surplus food batches "
        "with recipient NGOs based on spatial proximity, category alignment, volume fitness, and rescue urgency."
    )

    st.markdown(
        """
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px 18px; border-radius: 10px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #166534; font-size: 0.92rem; margin-bottom: 4px;">
                📐 Methodological Transparency Disclosure (Non-AI Rule-Based Engine)
            </div>
            <div style="color: #15803d; font-size: 0.85rem; line-height: 1.45;">
                This module uses an explainable heuristic scoring matrix (0–100 points) consisting of:
                <strong>Location Match (30%)</strong> + <strong>Category Alignment (25%)</strong> + 
                <strong>Quantity Fit (25%)</strong> + <strong>Expiry Urgency (20%)</strong>.
                Unlike opaque neural black-box models, every awarded point is auditable and explainable during faculty presentation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Recipient Profile Controls
    with st.container(border=True):
        st.markdown("#### 🎯 Specify Recipient Organization Needs")
        pref_col1, pref_col2 = st.columns(2)

        with pref_col1:
            recipient_name = st.text_input(
                "NGO / Recipient Community Organization",
                value="Hope Community Kitchen (NGO)",
                help="Identifier of the receiving shelter or distribution group.",
            )
            preferred_area = st.text_input(
                "Preferred Area / Target Zone",
                value="Bengaluru",
                help="Area keyword (e.g. Indiranagar, Koramangala, Whitefield, Bengaluru).",
            )

        with pref_col2:
            preferred_category = st.selectbox(
                "Target Food Category",
                ["Any"] + FOOD_CATEGORIES,
                index=0,
                help="Select 'Any' for all edible groups, or filter for specific kitchen capabilities.",
            )
            needed_quantity = st.number_input(
                "Approximate Target Quantity Needed",
                min_value=1.0,
                max_value=1000.0,
                value=25.0,
                step=5.0,
                help="The algorithm rewards batches that closely match or satisfy this portion size.",
            )

    # Run recommendation algorithm
    ranked_recommendations = get_recommendations(
        donations_df=df,
        preferred_area=preferred_area,
        preferred_category=preferred_category,
        needed_quantity=needed_quantity,
        limit=8,
    )

    st.markdown("### 🏆 Top Recommended Donations")

    if ranked_recommendations.empty:
        render_empty_state(
            "No Available Donations to Match",
            "All current food donations have either been accepted or completed. Add a new donation in 'Donate Food' to test matching.",
            "🤖",
        )
    else:
        for rank_idx, (_, row) in enumerate(ranked_recommendations.iterrows(), 1):
            score = row["match_score"]
            tier = row["match_tier"]
            d_id = row["id"]

            with st.container(border=True):
                top_m1, top_m2 = st.columns([3, 1])

                with top_m1:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span style="background: #0f172a; color: #ffffff; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">#{rank_idx}</span>
                            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">{row['food_name']}</h3>
                            <span class="category-pill">{row['category']}</span>
                            <span style="background: #e0f2fe; color: #0369a1; padding: 3px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700;">
                                {tier}
                            </span>
                        </div>
                        <div style="color: #475569; font-size: 0.88rem;">
                            🏢 <strong>{row['donor_name']}</strong> &nbsp;|&nbsp; 📍 {row['location']} &nbsp;|&nbsp; 📦 <strong>{row['quantity']:g} {row['unit']}</strong> &nbsp;|&nbsp; 📅 Expires {row['expiry']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with top_m2:
                    st.markdown(
                        f"""
                        <div style="text-align: right;">
                            <div style="font-size: 1.7rem; font-weight: 800; color: #16a34a;">{score} <span style="font-size: 0.9rem; color: #94a3b8;">/ 100</span></div>
                            <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">ALGORITHMIC FIT</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Progress Bar
                st.progress(min(1.0, score / 100.0))

                # Score Breakdown Metrics
                s1, s2, s3, s4 = st.columns(4)
                s1.caption(f"📍 Location Match: **{row['score_loc']}/30**")
                s2.caption(f"🍱 Category Match: **{row['score_cat']}/25**")
                s3.caption(f"⚖️ Quantity Fit: **{row['score_qty']}/25**")
                s4.caption(f"⏳ Expiry Urgency: **{row['score_urg']}/20**")

                # Explainable Reasons
                with st.expander("🔍 View Explainable Match Audit", expanded=False):
                    st.markdown("**Scoring Breakdown & Rationale:**")
                    for reason in row["match_reasons"]:
                        st.markdown(f"- {reason}")

                    # 1-click claim button
                    if st.session_state.active_role in [ROLE_NGO, ROLE_VOLUNTEER, ROLE_ADMIN]:
                        st.markdown("---")
                        if st.button(
                            f"🤝 Accept & Assign to {recipient_name}",
                            key=f"match_claim_{d_id}",
                            type="primary",
                        ):
                            ok, msg = update_donation_status(
                                donation_id=d_id,
                                new_status=STATUS_ACCEPTED,
                                actor_name=recipient_name.strip(),
                                actor_role=st.session_state.active_role,
                                note="Claimed via Smart Matching recommendation engine.",
                            )
                            if ok:
                                st.session_state.donations = load_donations()
                                st.session_state.events = load_events()
                                st.success(f"Matched donation {d_id} accepted for {recipient_name}!")
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        st.caption("Switch demo role to NGO or Volunteer in the sidebar to accept.")


# =========================================================
# PAGE 5: PICKUP MANAGEMENT & AUDIT LOG
# =========================================================
elif page == "🚚 Pickup Management":
    st.markdown("## 🚚 Pickup Management & Redistribution Workflow")
    st.markdown(
        "Manage the end-to-end custody transfer of food donations: "
        "`Available` ➔ `Accepted` ➔ `Picked Up` (In Transit) ➔ `Completed`."
    )

    tab1, tab2, tab3 = st.tabs(["Active Operations", "Completed Distributions", "Complete Audit Log"])

    with tab1:
        active_pickups = df[df["status"].isin([STATUS_ACCEPTED, STATUS_PICKED_UP])].copy()

        if active_pickups.empty:
            render_empty_state(
                "No Active Pickups in Progress",
                "Accepted donations waiting for volunteer collection or in transit will appear here. Claim an available donation in 'Find Food' to begin.",
                "🚚",
            )
        else:
            st.caption(f"**{len(active_pickups)}** donation batch(es) currently undergoing collection and transit.")

            for _, row in active_pickups.iterrows():
                d_id = row["id"]
                cur_status = row["status"]

                with st.container(border=True):
                    render_workflow_stepper(cur_status)

                    p_col1, p_col2 = st.columns([3, 1])

                    with p_col1:
                        st.markdown(
                            f"""
                            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">{row['food_name']}</h3>
                            <div style="color: #475569; font-size: 0.88rem; margin: 4px 0 8px 0;">
                                <strong>Tracking ID:</strong> <code>{d_id}</code> &nbsp;|&nbsp; 
                                <strong>Quantity:</strong> {row['quantity']:g} {row['unit']} &nbsp;|&nbsp; 
                                <strong>Category:</strong> {row['category']}
                            </div>
                            <div style="color: #64748b; font-size: 0.85rem;">
                                📍 <strong>Pickup From:</strong> {row['location']} ({row['donor_name']})<br>
                                🏢 <strong>Claimed By:</strong> {row['claimed_by'] or 'Volunteer Network'}<br>
                                📝 <strong>Claim Note:</strong> {row['claim_note'] or 'None provided'}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with p_col2:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                        if cur_status == STATUS_ACCEPTED:
                            st.caption("Stage 2: Awaiting Transit")
                            volunteer_note = st.text_input(
                                "Volunteer / Vehicle Info",
                                placeholder="e.g. Volunteer Priya, Van KA-04-1234",
                                key=f"v_note_{d_id}",
                            )
                            if st.button("🚚 Mark Picked Up", key=f"btn_pickup_{d_id}", type="primary", use_container_width=True):
                                ok, msg = update_donation_status(
                                    donation_id=d_id,
                                    new_status=STATUS_PICKED_UP,
                                    actor_name=st.session_state.active_role,
                                    actor_role=st.session_state.active_role,
                                    note=volunteer_note.strip() or "Collected from donor premises; en route to distribution hub.",
                                )
                                if ok:
                                    st.session_state.donations = load_donations()
                                    st.session_state.events = load_events()
                                    st.success(f"Donation {d_id} is now In Transit.")
                                    st.rerun()
                                else:
                                    st.error(msg)

                        elif cur_status == STATUS_PICKED_UP:
                            st.caption("Stage 3: In Transit")
                            delivery_note = st.text_input(
                                "Delivery Confirmation Note",
                                placeholder="e.g. Delivered to Shelter A; inspected wholesome",
                                key=f"del_note_{d_id}",
                            )
                            if st.button("✅ Mark as Completed", key=f"btn_complete_{d_id}", type="primary", use_container_width=True):
                                ok, msg = update_donation_status(
                                    donation_id=d_id,
                                    new_status=STATUS_COMPLETED,
                                    actor_name=st.session_state.active_role,
                                    actor_role=st.session_state.active_role,
                                    note=delivery_note.strip() or "Successfully received and distributed to community beneficiaries.",
                                )
                                if ok:
                                    st.session_state.donations = load_donations()
                                    st.session_state.events = load_events()
                                    st.balloons()
                                    st.success(f"Donation {d_id} successfully completed!")
                                    st.rerun()
                                else:
                                    st.error(msg)

    with tab2:
        completed_pickups = df[df["status"] == STATUS_COMPLETED].copy()
        if completed_pickups.empty:
            render_empty_state("No Completed Distributions Yet", "Once donations are collected and delivered, they are archived here.", "✅")
        else:
            st.caption(f"**{len(completed_pickups)}** successfully completed food redistribution missions.")
            display_cols = ["id", "food_name", "donor_name", "quantity", "unit", "location", "claimed_by", "created_at", "completed_at"]
            st.dataframe(
                completed_pickups[display_cols].sort_values("completed_at", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        st.markdown("#### 📜 System Event Audit Log")
        st.caption("Immutable append-only event trail recording every state change, actor, and timestamp.")

        ev_df = pd.DataFrame(st.session_state.events)
        if ev_df.empty:
            render_empty_state("No Events Recorded", "System activity will be logged here.", "📜")
        else:
            search_evt = st.text_input("Filter events by keyword", placeholder="Filter by actor, donation ID, or action").strip().lower()
            if search_evt:
                ev_df = ev_df[
                    ev_df["event"].str.lower().str.contains(search_evt, na=False)
                    | ev_df["actor"].str.lower().str.contains(search_evt, na=False)
                    | ev_df["donation_id"].str.lower().str.contains(search_evt, na=False)
                    | ev_df["details"].str.lower().str.contains(search_evt, na=False)
                ]

            st.dataframe(
                ev_df.sort_values("timestamp", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# PAGE 6: ANALYTICS & REPORTS
# =========================================================
elif page == "📈 Analytics & Reports":
    st.markdown("## 📈 Food Redistribution Analytics & Reporting")
    st.markdown(
        "Aggregated intelligence on food surplus redirection, donor participation, and community impact."
    )

    impact = calculate_impact_summary(df)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Rescued Food Weight", f"{impact['rescued_kg_equivalent']:g} kg")
    k2.metric("Estimated Meals Served", f"{impact['meals_saved']:,}")
    k3.metric("Greenhouse Gases Avoided", f"{impact['co2_prevented_kg']:g} kg CO₂e")
    k4.metric("Water Footprint Saved", f"{impact['water_saved_liters']:,.0f} L")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        with st.container(border=True):
            st.markdown("#### 🏆 Top Contributing Donors")
            st.plotly_chart(create_donor_leaderboard(df), use_container_width=True)

    with g2:
        with st.container(border=True):
            st.markdown("#### 🤝 NGO & Recipient Claims")
            st.plotly_chart(create_ngo_activity_chart(df), use_container_width=True)

    st.markdown("#### 📥 Export Audit Data for Academic Evaluation")
    st.caption("Download sanitized project records in CSV format for viva evaluation, external spreadsheets, or cloud data lake ingestion.")

    csv_data = export_donations_csv(df)
    st.download_button(
        label="📥 Download Donations Dataset (CSV)",
        data=csv_data,
        file_name=f"foodrescue_donations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        type="primary",
    )

    with st.expander("🔍 Explore Raw Database Records", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)


# =========================================================
# PAGE 7: CLOUD ARCHITECTURE & SUPABASE
# =========================================================
elif page == "☁️ Cloud Architecture":
    st.markdown("## ☁️ Cloud Architecture & Database Integration")
    st.markdown(
        "Explore how FoodRescue Cloud is engineered for high availability, zero-friction local demonstration, "
        "and seamless scalability to enterprise PostgreSQL databases."
    )

    # Storage Mode Callout
    status_color = "#16a34a" if storage_info["is_cloud"] else "#2563eb"
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 2px solid {status_color}; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 2.2rem;">{storage_info['icon']}</span>
                    <div>
                        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #0f172a;">Active Storage: {storage_info['name']}</h3>
                        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.88rem;">{storage_info['details']}</p>
                    </div>
                </div>
                <div>
                    <span style="background: {'#dcfce7' if storage_info['is_cloud'] else '#dbeafe'}; color: {'#166534' if storage_info['is_cloud'] else '#1e40af'}; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">
                        {'● Cloud Connected' if storage_info['is_cloud'] else '● Zero-Setup Demo Mode'}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🏛️ System Architecture Layers")
    arch_c1, arch_c2, arch_c3 = st.columns(3)

    with arch_c1:
        with st.container(border=True):
            st.markdown("#### 1. Presentation Layer")
            st.markdown(
                """
                - **Streamlit Framework:** Dynamic responsive web interface rendered directly from Python.
                - **Streamlit Community Cloud:** Managed serverless container hosting connected to GitHub CI/CD.
                - **Custom SaaS UI/UX:** Responsive grid, CSS design system, and custom SVG iconography.
                """
            )

    with arch_c2:
        with st.container(border=True):
            st.markdown("#### 2. Application Logic")
            st.markdown(
                """
                - **State Machine Engine:** Enforces valid status progressions (`Available` ➔ `Accepted` ➔ `Picked Up` ➔ `Completed`).
                - **Explainable Matching:** Multi-parameter heuristic scoring algorithm for proximity and category ranking.
                - **Data Sanitation:** Strict input validation on quantities, units, and non-expired dates.
                """
            )

    with arch_c3:
        with st.container(border=True):
            st.markdown("#### 3. Decoupled Storage")
            st.markdown(
                """
                - **Dual-Backend Storage Adapter:** Abstracted data layer with zero code coupling.
                - **Local Mode:** Immediate CSV persistence (`donations.csv` & `events.csv`) with automatic seed fallback.
                - **Cloud Mode:** Supabase PostgreSQL with connection pooling, Row Level Security, and audit trails.
                """
            )

    st.markdown("### 🗄️ Supabase PostgreSQL Setup & Secrets Configuration")
    st.markdown(
        """
        To connect FoodRescue Cloud to a real managed cloud database, follow these three steps:
        1. Create a free project at [supabase.com](https://supabase.com).
        2. Navigate to the **SQL Editor** and run the provided schema script below.
        3. Add your Supabase credentials to Streamlit Cloud Secrets (or local `.streamlit/secrets.toml`).
        """
    )

    with st.expander("📄 View Production Supabase SQL Schema (DDL)", expanded=False):
        supabase_sql = """-- =========================================================
-- FoodRescue Cloud - Supabase PostgreSQL Production Schema
-- =========================================================

-- 1. Create Donations Table
CREATE TABLE IF NOT EXISTS public.donations (
    id VARCHAR(32) PRIMARY KEY,
    donor_name VARCHAR(255) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(50) NOT NULL,
    expiry DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    pickup_window VARCHAR(100),
    contact VARCHAR(255),
    description TEXT,
    storage_conditions VARCHAR(100),
    allergens VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    claimed_by VARCHAR(255),
    claim_note TEXT,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Index for high-speed spatial & status queries
CREATE INDEX IF NOT EXISTS idx_donations_status ON public.donations(status);
CREATE INDEX IF NOT EXISTS idx_donations_category ON public.donations(category);
CREATE INDEX IF NOT EXISTS idx_donations_expiry ON public.donations(expiry);

-- 2. Create Audit Events Log Table
CREATE TABLE IF NOT EXISTS public.events (
    id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    donation_id VARCHAR(32) REFERENCES public.donations(id) ON DELETE CASCADE,
    food_name VARCHAR(255),
    event VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_donation ON public.events(donation_id);

-- 3. Row Level Security (RLS) Configuration
ALTER TABLE public.donations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

-- Allow public read access for demo purposes
CREATE POLICY "Public Read Access on Donations" ON public.donations FOR SELECT USING (true);
CREATE POLICY "Public Insert on Donations" ON public.donations FOR INSERT WITH CHECK (true);
CREATE POLICY "Public Update on Donations" ON public.donations FOR UPDATE USING (true);

CREATE POLICY "Public Read on Events" ON public.events FOR SELECT USING (true);
CREATE POLICY "Public Insert on Events" ON public.events FOR INSERT WITH CHECK (true);
"""
        st.code(supabase_sql, language="sql")

    with st.expander("🔐 Streamlit Secrets Configuration (.streamlit/secrets.toml)", expanded=False):
        secrets_toml = """# .streamlit/secrets.toml (Local development or Streamlit Cloud Settings -> Secrets)
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key"
"""
        st.code(secrets_toml, language="toml")
        st.caption("Never commit `secrets.toml` to GitHub. The project's `.gitignore` automatically prevents secret leaks.")


# =========================================================
# PAGE 8: ABOUT & PRESENTATION GUIDE
# =========================================================
else:
    st.markdown("## ℹ️ About FoodRescue Cloud & Faculty Presentation Guide")
    st.markdown(
        "A cloud-based prototype addressing surplus food rescue and redistribution, developed for academic cloud computing evaluation."
    )

    t1, t2, t3 = st.tabs(["Project Motivation & Scope", "Cloud Computing Viva Q&A", "Ethical & Safety Disclaimers"])

    with t1:
        st.markdown(
            """
            ### Problem Statement
            Globally, over 1.3 billion tonnes of edible food is lost or wasted annually, contributing nearly 8-10% of global greenhouse gas emissions. Simultaneously, millions of people experience acute nutritional vulnerability. 
            
            **FoodRescue Cloud** bridges this systemic gap using accessible cloud architecture to empower food businesses (restaurants, cafeterias, bakeries) to broadcast surplus food to verified community kitchens, shelters, and volunteer networks before it spoils.

            ### Alignment with UN Sustainable Development Goals (SDGs)
            - **SDG 2: Zero Hunger** — Redirecting quality surplus food to vulnerable populations.
            - **SDG 12: Responsible Consumption and Production (Target 12.3)** — Halving per capita global food waste by 2030.
            - **SDG 13: Climate Action** — Mitigating methane emissions produced by decomposing organic waste in municipal landfills.
            """
        )

    with t2:
        st.markdown(
            """
            ### 🎓 Key Cloud Computing Concepts for Faculty Viva Defense

            **Q1: How does this project demonstrate Cloud Computing principles?**  
            - **PaaS (Platform as a Service):** Hosted on Streamlit Community Cloud with automatic container lifecycle orchestration.
            - **Decoupled Architecture:** Clean separation of Presentation (Streamlit), Business Logic (Python modules), and Persistence (Storage Adapter).
            - **Dual-Storage Backend:** Demonstrates cloud elasticity by supporting local persistent CSVs and multi-tenant Cloud PostgreSQL (Supabase).
            - **Stateless Application Tier:** User sessions and transactions are decoupled from container storage.

            **Q2: How is data consistency and race condition risk handled?**  
            - State transitions follow a strict unidirectional state machine (`Available` ➔ `Accepted` ➔ `Picked Up` ➔ `Completed`).
            - All status transitions log an immutable audit event recording timestamp, actor, and outcome.

            **Q3: How does the Smart Matching algorithm work?**  
            - It is an **explainable rule-based heuristic model**, not an opaque AI black box.
            - Scores candidates from 0 to 100 based on Location (30%), Category (25%), Quantity (25%), and Expiry Urgency (20%). Every score point can be individually inspected and explained.
            """
        )

    with t3:
        st.markdown(
            """
            ### ⚠️ Operational Disclaimers & Responsible Computing Notice
            - **Educational Prototype:** This application is developed strictly for collegiate software engineering and cloud computing demonstration.
            - **Simulated Role Switcher:** The sidebar role switcher (`Donor`, `NGO`, `Volunteer`, `Admin`) is a presentation tool to simulate workflows. In commercial production, it must be replaced by OAuth 2.0 / OpenID Connect (e.g. Supabase Auth or Google Workspace SSO) with cryptographic JSON Web Tokens (JWT).
            - **Food Safety Disclaimer:** This software coordinates logistics but does not perform physical microbiological inspection. Production deployments must integrate certified food handler standards (FSSAI / FDA regulations).
            """
        )
