"""
FoodRescue Cloud - Smart Food Recommendation Engine
Transparent, explainable, rule-based heuristic matching system.
Designed for student demonstration to showcase algorithmic redistribution logic
without misrepresenting it as an opaque machine learning model.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Tuple
import pandas as pd

from src.config import STATUS_AVAILABLE


def parse_expiry_date(expiry_val: Any) -> date:
    """Parses expiry date safely from string, date, or timestamp."""
    if isinstance(expiry_val, date) and not isinstance(expiry_val, datetime):
        return expiry_val
    if isinstance(expiry_val, datetime):
        return expiry_val.date()
    try:
        return datetime.strptime(str(expiry_val).strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return date.today()


def score_donation_match(
    row: Dict[str, Any],
    preferred_area: str = "",
    preferred_category: str = "Any",
    needed_quantity: float = 0.0,
    max_days_window: int = 7,
) -> Dict[str, Any]:
    """
    Evaluates a single donation candidate against recipient preferences.
    Scores from 0 to 100 points across 4 explainable dimensions:
    1. Location Alignment (30 pts)
    2. Category Compatibility (25 pts)
    3. Quantity Fulfillment (25 pts)
    4. Expiry Urgency / Rescue Priority (20 pts)
    """
    reasons = []

    # ---------------------------------------------------------
    # 1. Location Alignment (Max 30 pts)
    # ---------------------------------------------------------
    loc_str = str(row.get("location", "")).lower()
    pref_area_clean = preferred_area.strip().lower()

    if not pref_area_clean:
        location_score = 22
        reasons.append("Location: Universal range (+22 pts - no area filter applied)")
    elif pref_area_clean in loc_str:
        location_score = 30
        reasons.append(f"Location: Direct match for '{preferred_area}' (+30 pts)")
    elif any(common in loc_str for common in ["bengaluru", "bangalore", "city", "metro"]):
        location_score = 20
        reasons.append("Location: Same metropolitan area (+20 pts)")
    else:
        location_score = 10
        reasons.append("Location: Extended transit distance (+10 pts)")

    # ---------------------------------------------------------
    # 2. Food Category Compatibility (Max 25 pts)
    # ---------------------------------------------------------
    cat = str(row.get("category", ""))
    if preferred_category in ["Any", "All", ""]:
        category_score = 25
        reasons.append("Category: Compatible with any food type (+25 pts)")
    elif cat.lower() == preferred_category.lower():
        category_score = 25
        reasons.append(f"Category: Exact match for '{cat}' (+25 pts)")
    elif (
        ("cooked" in cat.lower() and "buffet" in preferred_category.lower())
        or ("produce" in cat.lower() and "packaged" in preferred_category.lower())
    ):
        category_score = 16
        reasons.append(f"Category: Complementary food group ({cat}) (+16 pts)")
    else:
        category_score = 8
        reasons.append(f"Category: Alternative food group ({cat}) (+8 pts)")

    # ---------------------------------------------------------
    # 3. Quantity Fulfillment (Max 25 pts)
    # ---------------------------------------------------------
    qty = float(row.get("quantity", 0.0))
    unit = str(row.get("unit", "units"))

    if needed_quantity <= 0:
        quantity_score = 25
        reasons.append(f"Quantity: Available batch of {qty:g} {unit} fits need (+25 pts)")
    elif qty >= needed_quantity:
        quantity_score = 25
        reasons.append(f"Quantity: Fully covers requirement ({qty:g} >= {needed_quantity:g} {unit}) (+25 pts)")
    elif qty >= (needed_quantity * 0.5):
        quantity_score = 18
        reasons.append(f"Quantity: High partial fulfillment ({qty:g} of {needed_quantity:g} {unit}) (+18 pts)")
    else:
        ratio = qty / max(needed_quantity, 1.0)
        quantity_score = max(5, round(25 * ratio))
        reasons.append(f"Quantity: Partial batch ({qty:g} {unit}, {int(ratio*100)}% of target) (+{quantity_score} pts)")

    # ---------------------------------------------------------
    # 4. Expiry Urgency / Rescue Priority (Max 20 pts)
    # ---------------------------------------------------------
    today = date.today()
    exp_date = parse_expiry_date(row.get("expiry"))
    days_left = (exp_date - today).days

    if days_left < 0:
        urgency_score = 0
        reasons.append(f"Urgency: Expired ({abs(days_left)} days past date) (+0 pts)")
    elif days_left == 0:
        urgency_score = 20
        reasons.append("Urgency: Critical rescue! Expires TODAY (+20 pts)")
    elif days_left == 1:
        urgency_score = 17
        reasons.append("Urgency: High priority - expires tomorrow (+17 pts)")
    elif days_left <= 3:
        urgency_score = 13
        reasons.append(f"Urgency: Moderate urgency - {days_left} days left (+13 pts)")
    elif days_left <= max_days_window:
        urgency_score = 9
        reasons.append(f"Urgency: Standard shelf life ({days_left} days left) (+9 pts)")
    else:
        urgency_score = 6
        reasons.append(f"Urgency: Extended shelf life ({days_left} days left) (+6 pts)")

    # Composite Total
    total_score = min(100, location_score + category_score + quantity_score + urgency_score)

    # Determine qualitative tier
    if total_score >= 85:
        tier = "Top Match"
        tier_color = "#16a34a"
    elif total_score >= 70:
        tier = "Good Match"
        tier_color = "#3b82f6"
    elif total_score >= 50:
        tier = "Moderate Match"
        tier_color = "#f59e0b"
    else:
        tier = "Low Match"
        tier_color = "#64748b"

    return {
        "score": total_score,
        "tier": tier,
        "tier_color": tier_color,
        "breakdown": {
            "location": location_score,
            "category": category_score,
            "quantity": quantity_score,
            "urgency": urgency_score,
        },
        "reasons": reasons,
        "summary": " • ".join(reasons[:2]),
    }


def get_recommendations(
    donations_df: pd.DataFrame,
    preferred_area: str = "",
    preferred_category: str = "Any",
    needed_quantity: float = 0.0,
    max_days_window: int = 7,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Ranks available food donations using the explainable heuristic model.
    Returns sorted DataFrame with match score and breakdown columns.
    """
    if donations_df is None or donations_df.empty:
        return pd.DataFrame()

    # Filter to Available donations only
    available = donations_df[donations_df["status"] == STATUS_AVAILABLE].copy()
    if available.empty:
        return pd.DataFrame()

    scores_data = []
    for _, row in available.iterrows():
        res = score_donation_match(
            row=row.to_dict(),
            preferred_area=preferred_area,
            preferred_category=preferred_category,
            needed_quantity=needed_quantity,
            max_days_window=max_days_window,
        )
        scores_data.append(res)

    available["match_score"] = [s["score"] for s in scores_data]
    available["match_tier"] = [s["tier"] for s in scores_data]
    available["match_reasons"] = [s["reasons"] for s in scores_data]
    available["match_summary"] = [s["summary"] for s in scores_data]
    available["score_loc"] = [s["breakdown"]["location"] for s in scores_data]
    available["score_cat"] = [s["breakdown"]["category"] for s in scores_data]
    available["score_qty"] = [s["breakdown"]["quantity"] for s in scores_data]
    available["score_urg"] = [s["breakdown"]["urgency"] for s in scores_data]

    # Rank by match score descending, then expiry ascending
    ranked = available.sort_values(
        by=["match_score", "expiry"],
        ascending=[False, True],
    ).head(limit)

    return ranked
