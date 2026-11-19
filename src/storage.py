"""
FoodRescue Cloud - Data Storage and Persistence Layer
Supports dual backend:
1. Local CSV persistence with guaranteed auto-seeding (Zero configuration demo mode)
2. Optional Cloud Supabase PostgreSQL database with graceful fallback
"""

import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from src.config import (
    FOOD_CATEGORIES,
    QUANTITY_UNITS,
    STATUS_AVAILABLE,
    STATUS_ACCEPTED,
    STATUS_PICKED_UP,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    ALL_STATUSES,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DONATIONS_FILE = DATA_DIR / "donations.csv"
EVENTS_FILE = DATA_DIR / "events.csv"

COLUMNS = [
    "id",
    "donor_name",
    "food_name",
    "category",
    "quantity",
    "unit",
    "expiry",
    "location",
    "pickup_window",
    "contact",
    "description",
    "storage_conditions",
    "allergens",
    "status",
    "created_at",
    "claimed_by",
    "claim_note",
    "completed_at",
]

EVENT_COLUMNS = [
    "id",
    "timestamp",
    "donation_id",
    "food_name",
    "event",
    "actor",
    "details",
]


def get_relative_date(days_offset: int) -> str:
    """Helper to generate dates relative to runtime so sample data is never expired."""
    return (date.today() + timedelta(days=days_offset)).strftime("%Y-%m-%d")


def get_initial_sample_donations() -> List[Dict[str, Any]]:
    """
    Returns realistic initial sample donations relative to current runtime.
    Covers diverse categories, urban areas, and lifecycle statuses.
    """
    return [
        {
            "id": "FR-2026-1001",
            "donor_name": "Green Leaf Organic Cafe",
            "food_name": "Nutritious Veg Meal Trays",
            "category": "Cooked Meals",
            "quantity": 35.0,
            "unit": "meals",
            "expiry": get_relative_date(1),
            "location": "Indiranagar, Bengaluru",
            "pickup_window": "Within 2 hours",
            "contact": "mgr.indiranagar@greenleaf.demo",
            "description": "Steamed brown rice, mixed dal, and roasted seasonal vegetables packed in bio-trays.",
            "storage_conditions": "Hot Hold (> 60°C)",
            "allergens": "None / Pure Vegetarian",
            "status": STATUS_AVAILABLE,
            "created_at": (datetime.now() - timedelta(hours=3)).isoformat(timespec="seconds"),
            "claimed_by": "",
            "claim_note": "",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1002",
            "donor_name": "Sunrise Artisan Bakery",
            "food_name": "Sourdough & Multigrain Loaves",
            "category": "Bakery & Bread",
            "quantity": 14.0,
            "unit": "kg",
            "expiry": get_relative_date(2),
            "location": "Koramangala 4th Block, Bengaluru",
            "pickup_window": "Today evening",
            "contact": "contact@sunrisebakery.demo",
            "description": "Day-end artisan loaves and dinner rolls, paper bagged and sealed.",
            "storage_conditions": "Ambient / Room Temperature",
            "allergens": "Contains Gluten / Wheat",
            "status": STATUS_AVAILABLE,
            "created_at": (datetime.now() - timedelta(hours=5)).isoformat(timespec="seconds"),
            "claimed_by": "",
            "claim_note": "",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1003",
            "donor_name": "Campus Dining Hall - Tech University",
            "food_name": "Fresh Apple & Orange Crates",
            "category": "Fresh Produce",
            "quantity": 25.0,
            "unit": "boxes",
            "expiry": get_relative_date(4),
            "location": "Jayanagar 7th Block, Bengaluru",
            "pickup_window": "Tomorrow morning",
            "contact": "catering.lead@techuniv.demo",
            "description": "Whole seasonal fresh fruits in ventilated wooden crates. High quality.",
            "storage_conditions": "Keep in dry, cool place",
            "allergens": "None / Pure Vegetarian",
            "status": STATUS_ACCEPTED,
            "created_at": (datetime.now() - timedelta(hours=8)).isoformat(timespec="seconds"),
            "claimed_by": "Hope Community Kitchen",
            "claim_note": "Scheduled volunteer van pickup for tomorrow breakfast program.",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1004",
            "donor_name": "Metro Food Mart",
            "food_name": "Sealed Oats & Granola Packs",
            "category": "Packaged Food",
            "quantity": 50.0,
            "unit": "packets",
            "expiry": get_relative_date(18),
            "location": "Whitefield IT Park, Bengaluru",
            "pickup_window": "Flexible (Anytime today)",
            "contact": "surplus@metrofoodmart.demo",
            "description": "Factory-sealed breakfast oat packets nearing inventory clearance date.",
            "storage_conditions": "Ambient / Room Temperature",
            "allergens": "Contains Gluten / Wheat",
            "status": STATUS_COMPLETED,
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(timespec="seconds"),
            "claimed_by": "City Care Foundation",
            "claim_note": "Distributed across 3 youth rehabilitation centers.",
            "completed_at": (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds"),
        },
        {
            "id": "FR-2026-1005",
            "donor_name": "Royal Banquet Hall & Convention",
            "food_name": "Paneer Biryani & Dal Makhani",
            "category": "Prepared Buffets",
            "quantity": 60.0,
            "unit": "meals",
            "expiry": get_relative_date(0),
            "location": "Malleshwaram, Bengaluru",
            "pickup_window": "Within 1 hour (Urgent)",
            "contact": "banquet.desk@royalhall.demo",
            "description": "Surplus banquet buffet cooked 2 hours ago. Kept in food-grade thermal containers.",
            "storage_conditions": "Hot Hold (> 60°C)",
            "allergens": "Contains Dairy",
            "status": STATUS_AVAILABLE,
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat(timespec="seconds"),
            "claimed_by": "",
            "claim_note": "",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1006",
            "donor_name": "FarmFresh Organic Supermarket",
            "food_name": "Mixed Crisp Vegetables (Carrots, Beans, Bell Peppers)",
            "category": "Fresh Produce",
            "quantity": 30.0,
            "unit": "kg",
            "expiry": get_relative_date(3),
            "location": "HSR Layout Sector 2, Bengaluru",
            "pickup_window": "Within 2 hours",
            "contact": "operations@farmfresh.demo",
            "description": "Grade-A vegetables slightly misshapen for retail shelves, 100% fresh and nutritious.",
            "storage_conditions": "Refrigerated (0°C to 4°C)",
            "allergens": "None / Pure Vegetarian",
            "status": STATUS_PICKED_UP,
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat(timespec="seconds"),
            "claimed_by": "Nourish India NGO",
            "claim_note": "Volunteer driver Raj assigned with cold storage van.",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1007",
            "donor_name": "Pure Pastures Dairy Cooperative",
            "food_name": "Pasteurized Milk & Fresh Yogurt",
            "category": "Dairy Products",
            "quantity": 20.0,
            "unit": "litres",
            "expiry": get_relative_date(1),
            "location": "Electronic City Phase 1, Bengaluru",
            "pickup_window": "Today evening",
            "contact": "distro@purepastures.demo",
            "description": "Surplus chilled milk pouches and setting yogurt in food-grade tubs.",
            "storage_conditions": "Refrigerated (0°C to 4°C)",
            "allergens": "Contains Dairy",
            "status": STATUS_AVAILABLE,
            "created_at": (datetime.now() - timedelta(hours=4)).isoformat(timespec="seconds"),
            "claimed_by": "",
            "claim_note": "",
            "completed_at": "",
        },
        {
            "id": "FR-2026-1008",
            "donor_name": "Summit Corporate Cafeteria",
            "food_name": "Sandwiches & Fruit Yogurt Cups",
            "category": "Cooked Meals",
            "quantity": 40.0,
            "unit": "meals",
            "expiry": get_relative_date(0),
            "location": "MG Road, Bengaluru",
            "pickup_window": "Within 2 hours",
            "contact": "canteen.help@summitcorp.demo",
            "description": "Freshly wrapped veggie sandwiches and individually sealed fruit yogurts.",
            "storage_conditions": "Refrigerated (0°C to 4°C)",
            "allergens": "Contains Dairy, Contains Gluten / Wheat",
            "status": STATUS_COMPLETED,
            "created_at": (datetime.now() - timedelta(days=1, hours=4)).isoformat(timespec="seconds"),
            "claimed_by": "Youth Relief Network",
            "claim_note": "Picked up on time and distributed to evening shelter.",
            "completed_at": (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds"),
        },
    ]


def get_initial_sample_events() -> List[Dict[str, Any]]:
    """Returns realistic initial audit events corresponding to sample donations."""
    now = datetime.now()
    return [
        {
            "id": "EVT-101",
            "timestamp": (now - timedelta(days=2)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1004",
            "food_name": "Sealed Oats & Granola Packs",
            "event": "Created",
            "actor": "Metro Food Mart (Donor)",
            "details": "Listed 50 packets for Whitefield redistribution.",
        },
        {
            "id": "EVT-102",
            "timestamp": (now - timedelta(days=1, hours=18)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1004",
            "food_name": "Sealed Oats & Granola Packs",
            "event": "Accepted",
            "actor": "City Care Foundation (NGO)",
            "details": "Accepted for community youth centers.",
        },
        {
            "id": "EVT-103",
            "timestamp": (now - timedelta(days=1, hours=12)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1004",
            "food_name": "Sealed Oats & Granola Packs",
            "event": "Completed",
            "actor": "Volunteer Driver (Volunteer)",
            "details": "Successfully delivered to shelter pantries.",
        },
        {
            "id": "EVT-104",
            "timestamp": (now - timedelta(hours=8)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1003",
            "food_name": "Fresh Apple & Orange Crates",
            "event": "Created",
            "actor": "Campus Dining Hall (Donor)",
            "details": "Published 25 boxes of fresh produce.",
        },
        {
            "id": "EVT-105",
            "timestamp": (now - timedelta(hours=5)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1003",
            "food_name": "Fresh Apple & Orange Crates",
            "event": "Accepted",
            "actor": "Hope Community Kitchen (NGO)",
            "details": "Accepted for morning breakfast distribution.",
        },
        {
            "id": "EVT-106",
            "timestamp": (now - timedelta(hours=6)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1006",
            "food_name": "Mixed Crisp Vegetables",
            "event": "Picked Up",
            "actor": "Volunteer Raj (Volunteer)",
            "details": "Collected from HSR Layout; en route to distribution hub.",
        },
        {
            "id": "EVT-107",
            "timestamp": (now - timedelta(hours=1)).isoformat(timespec="seconds"),
            "donation_id": "FR-2026-1005",
            "food_name": "Paneer Biryani & Dal Makhani",
            "event": "Created",
            "actor": "Royal Banquet Hall (Donor)",
            "details": "Listed urgent hot meals needing immediate rescue.",
        },
    ]


# ---------------------------------------------------------
# Storage Backend Resolver (Local CSV vs Cloud Supabase)
# ---------------------------------------------------------

_supabase_client = None
_supabase_initialized = False


def get_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Fetches Supabase URL and key from Streamlit secrets or environment variables."""
    url = None
    key = None
    try:
        import streamlit as st  # type: ignore
        if hasattr(st, "secrets"):
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
    except Exception:
        pass

    if not url:
        url = os.getenv("SUPABASE_URL")
    if not key:
        key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    return url, key


def get_supabase_client():
    """Initializes and returns Supabase client if configured, else None."""
    global _supabase_client, _supabase_initialized
    if _supabase_initialized:
        return _supabase_client

    _supabase_initialized = True
    url, key = get_supabase_credentials()
    if url and key:
        try:
            from supabase import create_client  # type: ignore
            _supabase_client = create_client(url, key)
        except Exception as e:
            # Fall back gracefully to CSV mode
            _supabase_client = None
    return _supabase_client


def get_storage_backend_info() -> Dict[str, Any]:
    """Returns metadata describing active storage mode for UI display."""
    client = get_supabase_client()
    url, _ = get_supabase_credentials()
    if client is not None and url:
        # Masked URL
        masked = url.split("//")[-1].split(".")[0] + "..." if "//" in url else "Configured"
        return {
            "mode": "supabase",
            "name": "Cloud Supabase PostgreSQL",
            "badge_color": "green",
            "icon": "☁️",
            "details": f"Connected to Supabase ({masked})",
            "is_cloud": True,
        }
    return {
        "mode": "csv",
        "name": "Local CSV Demo Storage",
        "badge_color": "blue",
        "icon": "💾",
        "details": "Persisting to data/donations.csv & data/events.csv (Zero-Setup Demo)",
        "is_cloud": False,
    }


# ---------------------------------------------------------
# Core Storage Functions (with fallback & guaranteed seeding)
# ---------------------------------------------------------

def ensure_data_directory():
    """Ensures data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_donations(reset: bool = False) -> pd.DataFrame:
    """
    Loads donation records into a Pandas DataFrame.
    If reset=True, or if file is missing/empty, auto-populates with rich sample data.
    """
    ensure_data_directory()

    # Try Supabase if available
    client = get_supabase_client()
    if client and not reset:
        try:
            res = client.table("donations").select("*").execute()
            if res.data and len(res.data) > 0:
                df = pd.DataFrame(res.data)
                for col in COLUMNS:
                    if col not in df.columns:
                        df[col] = ""
                return df[COLUMNS]
        except Exception:
            # Fall back to CSV
            pass

    # CSV path
    needs_seeding = reset or (not DONATIONS_FILE.exists())

    if not needs_seeding:
        try:
            # Check if file has at least 1 data row
            df_check = pd.read_csv(DONATIONS_FILE)
            if df_check.empty or len(df_check) == 0:
                needs_seeding = True
        except Exception:
            needs_seeding = True

    if needs_seeding:
        initial_data = get_initial_sample_donations()
        df = pd.DataFrame(initial_data, columns=COLUMNS)
        save_donations(df)
        return df

    try:
        df = pd.read_csv(DONATIONS_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        # Ensure quantity is float
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
        return df[COLUMNS]
    except Exception:
        initial_data = get_initial_sample_donations()
        df = pd.DataFrame(initial_data, columns=COLUMNS)
        save_donations(df)
        return df


def save_donations(df: pd.DataFrame) -> bool:
    """Persists donations DataFrame to CSV (and Supabase if configured)."""
    ensure_data_directory()
    try:
        # Standardize columns
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        clean_df = df[COLUMNS].copy()
        clean_df.to_csv(DONATIONS_FILE, index=False)

        # Optional sync to Supabase
        client = get_supabase_client()
        if client:
            try:
                # Upsert records
                records = clean_df.to_dict("records")
                client.table("donations").upsert(records).execute()
            except Exception:
                pass
        return True
    except Exception:
        return False


def load_events() -> List[Dict[str, Any]]:
    """Loads audit events log. Seeds initial events if empty."""
    ensure_data_directory()

    client = get_supabase_client()
    if client:
        try:
            res = client.table("events").select("*").order("timestamp", desc=True).execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    if not EVENTS_FILE.exists():
        initial_events = get_initial_sample_events()
        save_events(initial_events)
        return initial_events

    try:
        df = pd.read_csv(EVENTS_FILE)
        if df.empty or len(df) == 0:
            initial_events = get_initial_sample_events()
            save_events(initial_events)
            return initial_events
        return df.to_dict("records")
    except Exception:
        initial_events = get_initial_sample_events()
        save_events(initial_events)
        return initial_events


def save_events(events: List[Dict[str, Any]]) -> bool:
    """Saves audit events to CSV (and Supabase if configured)."""
    ensure_data_directory()
    try:
        df = pd.DataFrame(events)
        for col in EVENT_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[EVENT_COLUMNS]
        df.to_csv(EVENTS_FILE, index=False)

        client = get_supabase_client()
        if client and events:
            try:
                client.table("events").upsert(events[-10:]).execute()
            except Exception:
                pass
        return True
    except Exception:
        return False


def log_event(donation_id: str, food_name: str, event_name: str, actor: str, details: str = "") -> Dict[str, Any]:
    """Appends an event to the audit trail."""
    evt = {
        "id": f"EVT-{uuid.uuid4().hex[:6].upper()}",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "donation_id": donation_id,
        "food_name": food_name,
        "event": event_name,
        "actor": actor,
        "details": details,
    }
    events = load_events()
    events.insert(0, evt)  # newest first
    save_events(events)
    return evt


# ---------------------------------------------------------
# Donation CRUD Operations & State Machine Transitions
# ---------------------------------------------------------

def generate_donation_id() -> str:
    """Generates a collision-free human-friendly donation identifier."""
    year_prefix = datetime.now().strftime("%Y")
    hex_token = uuid.uuid4().hex[:4].upper()
    return f"FR-{year_prefix}-{hex_token}"


def validate_donation_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Strict validation for food donation submissions.
    Ensures safe, complete, and legally conscientious records.
    """
    errors = []

    # Required text fields
    donor = str(data.get("donor_name", "")).strip()
    if len(donor) < 2:
        errors.append("Donor / Organization name is required (minimum 2 characters).")

    food = str(data.get("food_name", "")).strip()
    if len(food) < 2:
        errors.append("Food name is required (minimum 2 characters).")

    location = str(data.get("location", "")).strip()
    if len(location) < 3:
        errors.append("Pickup area / address is required (minimum 3 characters).")

    # Category validation
    category = data.get("category")
    if category not in FOOD_CATEGORIES:
        errors.append(f"Please select a valid food category from {FOOD_CATEGORIES}.")

    # Quantity validation
    try:
        qty = float(data.get("quantity", 0))
        if qty <= 0:
            errors.append("Quantity must be greater than zero.")
    except (ValueError, TypeError):
        errors.append("Quantity must be a valid number.")

    unit = data.get("unit")
    if unit not in QUANTITY_UNITS:
        errors.append(f"Please select a valid measurement unit from {QUANTITY_UNITS}.")

    # Expiry validation
    expiry_val = data.get("expiry")
    if not expiry_val:
        errors.append("Expiry or use-by date is required.")
    else:
        try:
            if isinstance(expiry_val, str):
                exp_date = datetime.strptime(expiry_val, "%Y-%m-%d").date()
            elif isinstance(expiry_val, (date, datetime)):
                exp_date = expiry_val.date() if isinstance(expiry_val, datetime) else expiry_val
            else:
                exp_date = date.today()

            if exp_date < date.today():
                errors.append(f"Expiry date ({exp_date}) cannot be in the past. Food must be fresh.")
        except Exception:
            errors.append("Invalid expiry date format. Please use YYYY-MM-DD.")

    # Food safety confirmation
    if not data.get("confirmed", False):
        errors.append("You must certify that the food details are accurate and safe for consumption.")

    return len(errors) == 0, errors


def create_donation(donation_dict: Dict[str, Any], actor: str = "Donor") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validates and persists a new food donation record.
    Returns (success, message, created_record).
    """
    is_valid, errors = validate_donation_input(donation_dict)
    if not is_valid:
        return False, " | ".join(errors), None

    donation_id = generate_donation_id()
    new_record = {
        "id": donation_id,
        "donor_name": str(donation_dict["donor_name"]).strip(),
        "food_name": str(donation_dict["food_name"]).strip(),
        "category": str(donation_dict["category"]),
        "quantity": float(donation_dict["quantity"]),
        "unit": str(donation_dict["unit"]),
        "expiry": str(donation_dict["expiry"]),
        "location": str(donation_dict["location"]).strip(),
        "pickup_window": str(donation_dict.get("pickup_window", "Flexible")),
        "contact": str(donation_dict.get("contact", "demo@example.com")).strip(),
        "description": str(donation_dict.get("description", "")).strip(),
        "storage_conditions": str(donation_dict.get("storage_conditions", "Ambient / Room Temperature")),
        "allergens": str(donation_dict.get("allergens", "None / Pure Vegetarian")),
        "status": STATUS_AVAILABLE,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "claimed_by": "",
        "claim_note": "",
        "completed_at": "",
    }

    df = load_donations()
    # Check ID collision safety
    while donation_id in df["id"].values:
        donation_id = generate_donation_id()
        new_record["id"] = donation_id

    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    save_donations(df)

    log_event(
        donation_id=donation_id,
        food_name=new_record["food_name"],
        event_name="Created",
        actor=f"{new_record['donor_name']} ({actor})",
        details=f"Listed {new_record['quantity']} {new_record['unit']} at {new_record['location']}",
    )

    return True, f"Donation {donation_id} successfully published!", new_record


def update_donation_status(
    donation_id: str,
    new_status: str,
    actor_name: str,
    actor_role: str,
    note: str = "",
) -> Tuple[bool, str]:
    """
    Transitions donation through lifecycle:
    Available -> Accepted -> Picked Up -> Completed (or Cancelled)
    Records timestamped event in audit log.
    """
    if new_status not in ALL_STATUSES:
        return False, f"Invalid status: {new_status}"

    df = load_donations()
    matches = df[df["id"] == donation_id]
    if matches.empty:
        return False, f"Donation {donation_id} not found."

    idx = matches.index[0]
    current_status = df.loc[idx, "status"]
    food_name = df.loc[idx, "food_name"]

    # Valid transitions check
    valid_transitions = {
        STATUS_AVAILABLE: [STATUS_ACCEPTED, STATUS_CANCELLED],
        STATUS_ACCEPTED: [STATUS_PICKED_UP, STATUS_CANCELLED, STATUS_AVAILABLE],
        STATUS_PICKED_UP: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_COMPLETED: [],
        STATUS_CANCELLED: [STATUS_AVAILABLE],
    }

    if new_status not in valid_transitions.get(current_status, []):
        return False, f"Cannot transition from '{current_status}' to '{new_status}'."

    # Apply updates
    df.loc[idx, "status"] = new_status
    if new_status == STATUS_ACCEPTED:
        df.loc[idx, "claimed_by"] = actor_name or actor_role
        if note:
            df.loc[idx, "claim_note"] = note
    elif new_status == STATUS_COMPLETED:
        df.loc[idx, "completed_at"] = datetime.now().isoformat(timespec="seconds")
        if note:
            existing_note = str(df.loc[idx, "claim_note"])
            df.loc[idx, "claim_note"] = f"{existing_note} | Completion Note: {note}" if existing_note else note

    save_donations(df)

    # Log audit event
    actor_label = f"{actor_name} ({actor_role})" if actor_name else actor_role
    action_details = f"Status changed from {current_status} to {new_status}."
    if note:
        action_details += f" Note: {note}"

    log_event(
        donation_id=donation_id,
        food_name=food_name,
        event_name=new_status,
        actor=actor_label,
        details=action_details,
    )

    return True, f"Donation {donation_id} updated to '{new_status}'."


def reset_all_data() -> None:
    """Restores sample donations and initial events for faculty demonstration."""
    load_donations(reset=True)
    initial_events = get_initial_sample_events()
    save_events(initial_events)
    log_event(
        donation_id="SYSTEM",
        food_name="System",
        event_name="Reset",
        actor="Admin",
        details="Sample data restored to clean demonstration state.",
    )
