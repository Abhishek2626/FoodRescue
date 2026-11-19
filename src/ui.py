"""
FoodRescue Cloud - UI/UX Design System and Shared Components
Modern food-tech SaaS aesthetics with green/neutral color palette,
card designs, status badges, and responsive layouts.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional
import streamlit as st

from src.config import (
    APP_ICON,
    APP_SUBTITLE,
    APP_TITLE,
    PRIMARY_GREEN,
    STATUS_BADGES,
    STATUS_AVAILABLE,
    STATUS_ACCEPTED,
    STATUS_PICKED_UP,
    STATUS_COMPLETED,
)


def inject_custom_css():
    """Injects responsive modern CSS styling for a polished SaaS look."""
    st.markdown(
        """
        <style>
        /* Base typography & layout */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .main .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3.5rem;
            max-width: 1250px;
        }

        /* Top Header banner */
        .app-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 14px;
            padding: 22px 28px;
            color: #ffffff;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }

        .app-header h1 {
            color: #ffffff !important;
            font-size: 1.65rem;
            font-weight: 800;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .app-header p {
            color: #94a3b8;
            margin: 4px 0 0 0;
            font-size: 0.92rem;
            font-weight: 500;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 16px 20px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.04);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px -2px rgba(22, 163, 74, 0.08);
            border-color: #cbd5e1;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
        }

        /* Status & Category Pills */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }

        .category-pill {
            display: inline-block;
            background: #f1f5f9;
            color: #334155;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1px solid #e2e8f0;
        }

        .urgent-pill {
            background: #fee2e2;
            color: #991b1b;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            border: 1px solid #fecaca;
        }

        /* Role Badge Pill */
        .demo-role-badge {
            background: rgba(22, 163, 74, 0.12);
            color: #166534;
            border: 1px solid rgba(22, 163, 74, 0.25);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Storage Badge Pill */
        .storage-badge {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            color: #475569;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Workflow timeline steps */
        .workflow-stepper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f8fafc;
            padding: 12px 18px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            margin: 10px 0 16px 0;
            gap: 8px;
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #94a3b8;
        }

        .step-item.active {
            color: #16a34a;
        }

        .step-item.completed {
            color: #0f172a;
        }

        .step-dot {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            background: #e2e8f0;
            color: #64748b;
        }

        .step-item.active .step-dot {
            background: #16a34a;
            color: #ffffff;
            box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
        }

        .step-item.completed .step-dot {
            background: #0f172a;
            color: #ffffff;
        }

        .step-connector {
            flex: 1;
            height: 2px;
            background: #e2e8f0;
        }

        .step-connector.completed {
            background: #16a34a;
        }

        /* Environmental Impact Banner */
        .impact-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #bbf7d0;
            border-radius: 12px;
            padding: 18px 22px;
            color: #14532d;
            margin-bottom: 20px;
        }

        /* Buttons styling */
        button[kind="primary"] {
            background-color: #16a34a !important;
            border-color: #16a34a !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }

        button[kind="primary"]:hover {
            background-color: #15803d !important;
            border-color: #15803d !important;
        }

        /* DataFrames */
        div[data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
        }

        /* Sidebar styling */
        div[data-testid="stSidebar"] {
            border-right: 1px solid #e2e8f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(role: str, storage_info: Dict[str, Any]):
    """Renders the top branding header with active role indicator and cloud storage pill."""
    storage_pill = f"""
    <span class="storage-badge" title="{storage_info.get('details', '')}">
        {storage_info.get('icon', '💾')} {storage_info.get('name', 'Local CSV')}
    </span>
    """

    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1>{APP_ICON} {APP_TITLE}</h1>
                <p>{APP_SUBTITLE}</p>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <span class="demo-role-badge">
                    👤 Demo Role: <strong>{role}</strong>
                </span>
                {storage_pill}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_pill(status: str) -> str:
    """Returns HTML for a status pill badge."""
    cfg = STATUS_BADGES.get(status, {"bg": "#f1f5f9", "text": "#475569", "icon": "⚪"})
    return f"""
    <span class="status-pill" style="background-color: {cfg['bg']}; color: {cfg['text']};">
        <span>{cfg['icon']}</span>
        <span>{status}</span>
    </span>
    """


def render_workflow_stepper(current_status: str):
    """Renders a 4-stage visual stepper for pickup progress."""
    stages = [
        ("Available", "1"),
        ("Accepted", "2"),
        ("Picked Up", "3"),
        ("Completed", "4"),
    ]

    status_ranks = {
        STATUS_AVAILABLE: 1,
        STATUS_ACCEPTED: 2,
        STATUS_PICKED_UP: 3,
        STATUS_COMPLETED: 4,
    }
    cur_rank = status_ranks.get(current_status, 1)

    html_parts = ['<div class="workflow-stepper">']
    for idx, (label, num) in enumerate(stages):
        step_num = idx + 1
        if step_num < cur_rank:
            cls = "step-item completed"
            icon = "✓"
        elif step_num == cur_rank:
            cls = "step-item active"
            icon = num
        else:
            cls = "step-item"
            icon = num

        html_parts.append(
            f"""
            <div class="{cls}">
                <div class="step-dot">{icon}</div>
                <span>{label}</span>
            </div>
            """
        )
        if idx < len(stages) - 1:
            conn_cls = "step-connector completed" if step_num < cur_rank else "step-connector"
            html_parts.append(f'<div class="{conn_cls}"></div>')

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_empty_state(title: str, message: str, icon: str = "📦", action_label: Optional[str] = None):
    """Renders a friendly empty state component."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align: center; padding: 32px 16px;">
                <div style="font-size: 2.8rem; margin-bottom: 8px;">{icon}</div>
                <h3 style="color: #1e293b; margin-bottom: 6px; font-weight: 700;">{title}</h3>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 480px; margin: 0 auto 16px auto;">{message}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def check_urgency(expiry_str: str) -> Tuple[bool, str]:
    """Returns whether donation is urgently expiring within 24-48 hours."""
    try:
        exp_date = datetime.strptime(str(expiry_str)[:10], "%Y-%m-%d").date()
        diff = (exp_date - date.today()).days
        if diff < 0:
            return True, f"Expired {abs(diff)}d ago"
        elif diff == 0:
            return True, "Expires TODAY"
        elif diff == 1:
            return True, "Expires TOMORROW"
        return False, f"{diff} days left"
    except Exception:
        return False, "Expiry unknown"
