"""
FoodRescue Cloud - Analytics & Visualizations Engine
Generates interactive Plotly figures and environmental impact calculations.
"""

from datetime import date, datetime
from typing import Any, Dict, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    CO2E_PER_KG,
    FOOD_CATEGORIES,
    KG_PER_MEAL,
    STATUS_ACCEPTED,
    STATUS_AVAILABLE,
    STATUS_COMPLETED,
    STATUS_PICKED_UP,
    STATUS_COLORS,
    UNIT_TO_KG,
    WATER_LITERS_PER_KG,
)


def calculate_impact_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes system-wide impact metrics including environmental indices.
    Standardizes units to kg-equivalents.
    """
    if df is None or df.empty:
        return {
            "total_donations": 0,
            "available_donations": 0,
            "accepted_donations": 0,
            "in_transit_donations": 0,
            "completed_donations": 0,
            "rescued_count": 0,
            "total_raw_quantity": 0.0,
            "rescued_kg_equivalent": 0.0,
            "meals_saved": 0,
            "co2_prevented_kg": 0.0,
            "water_saved_liters": 0.0,
        }

    total_count = len(df)
    available_count = int((df["status"] == STATUS_AVAILABLE).sum())
    accepted_count = int((df["status"] == STATUS_ACCEPTED).sum())
    in_transit_count = int((df["status"] == STATUS_PICKED_UP).sum())
    completed_count = int((df["status"] == STATUS_COMPLETED).sum())
    rescued_count = in_transit_count + completed_count

    # Calculate rescued kg-equivalent
    rescued_rows = df[df["status"].isin([STATUS_PICKED_UP, STATUS_COMPLETED])].copy()

    rescued_kg = 0.0
    for _, r in rescued_rows.iterrows():
        try:
            qty = float(r.get("quantity", 0.0))
            unit = str(r.get("unit", "kg")).lower()
            factor = UNIT_TO_KG.get(unit, 1.0)
            rescued_kg += qty * factor
        except Exception:
            pass

    # Total quantity listed (all statuses)
    total_raw_quantity = float(pd.to_numeric(df["quantity"], errors="coerce").sum())

    # Environmental indicators
    meals_saved = int(round(rescued_kg / KG_PER_MEAL))
    co2_prevented = round(rescued_kg * CO2E_PER_KG, 1)
    water_saved = round(rescued_kg * WATER_LITERS_PER_KG, 0)

    return {
        "total_donations": total_count,
        "available_donations": available_count,
        "accepted_donations": accepted_count,
        "in_transit_donations": in_transit_count,
        "completed_donations": completed_count,
        "rescued_count": rescued_count,
        "total_raw_quantity": round(total_raw_quantity, 1),
        "rescued_kg_equivalent": round(rescued_kg, 1),
        "meals_saved": meals_saved,
        "co2_prevented_kg": co2_prevented,
        "water_saved_liters": water_saved,
    }


def create_status_donut_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a modern donut chart showing donation status breakdown."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No donation records available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    color_map = {status: STATUS_COLORS.get(status, "#94a3b8") for status in status_counts["Status"]}

    fig = px.pie(
        status_counts,
        values="Count",
        names="Status",
        hole=0.55,
        color="Status",
        color_discrete_map=color_map,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#ffffff", width=2)),
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=10, b=30),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_category_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a clean horizontal or vertical bar chart of donations by category."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No category data available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    cat_summary = df.groupby("category", as_index=False).agg(
        Count=("id", "count"),
        Total_Quantity=("quantity", "sum"),
    ).sort_values("Count", ascending=True)

    fig = px.bar(
        cat_summary,
        x="Count",
        y="category",
        orientation="h",
        text="Count",
        labels={"category": "Food Category", "Count": "Number of Donations"},
        color_discrete_sequence=["#16a34a"],
    )
    fig.update_traces(
        textposition="outside",
        marker=dict(cornerradius=4),
    )
    fig.update_layout(
        margin=dict(l=10, r=20, t=10, b=20),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=False),
    )
    return fig


def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Plots daily submissions trend line over time."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No timeline data available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    temp_df = df.copy()
    temp_df["date"] = pd.to_datetime(temp_df["created_at"], errors="coerce").dt.date
    daily = temp_df.groupby("date", as_index=False).size().sort_values("date")
    daily.columns = ["Date", "Donations"]

    # Calculate cumulative
    daily["Cumulative"] = daily["Donations"].cumsum()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=daily["Date"],
            y=daily["Donations"],
            name="Daily Listed",
            marker_color="#86efac",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily["Date"],
            y=daily["Cumulative"],
            name="Cumulative Total",
            mode="lines+markers",
            line=dict(color="#15803d", width=3),
            marker=dict(size=7),
            yaxis="y2",
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Daily Donations"),
        yaxis2=dict(
            title="Cumulative Donations",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )
    return fig


def create_donor_leaderboard(df: pd.DataFrame) -> go.Figure:
    """Visualizes top contributing donor entities."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No donor records", showarrow=False)
        return fig

    donors = df.groupby("donor_name", as_index=False).agg(
        Donations=("id", "count"),
        Total_Quantity=("quantity", "sum"),
    ).sort_values("Donations", ascending=False).head(7)

    fig = px.bar(
        donors,
        x="donor_name",
        y="Donations",
        text="Donations",
        color="Donations",
        color_continuous_scale=["#bbf7d0", "#15803d"],
        labels={"donor_name": "Donor Organization", "Donations": "Donations Listed"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(tickangle=-20),
    )
    return fig


def create_ngo_activity_chart(df: pd.DataFrame) -> go.Figure:
    """Visualizes NGO / Volunteer claims and distributions."""
    claimed_df = df[df["claimed_by"].str.strip() != ""].copy()
    if claimed_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No NGO claims recorded yet", showarrow=False, font=dict(color="#64748b"))
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
        return fig

    ngos = claimed_df.groupby("claimed_by", as_index=False).agg(
        Claims=("id", "count")
    ).sort_values("Claims", ascending=True)

    fig = px.bar(
        ngos,
        x="Claims",
        y="claimed_by",
        orientation="h",
        text="Claims",
        labels={"claimed_by": "Recipient / NGO", "Claims": "Donations Claimed"},
        color_discrete_sequence=["#0d9488"],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def export_donations_csv(df: pd.DataFrame) -> str:
    """Generates sanitized CSV representation for faculty reporting."""
    if df.empty:
        return ""
    return df.to_csv(index=False)
