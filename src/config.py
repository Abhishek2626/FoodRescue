"""
FoodRescue Cloud - Global Configuration and Constants
"""

# App Metadata
APP_TITLE = "FoodRescue Cloud"
APP_SUBTITLE = "Cloud-Based Food Donation, Surplus Management & Community Redistribution Platform"
APP_ICON = "🥗"
APP_VERSION = "2.0.0"

# Color Palette
PRIMARY_GREEN = "#16a34a"
PRIMARY_DARK = "#15803d"
PRIMARY_LIGHT = "#dcfce7"
ACCENT_AMBER = "#f59e0b"
ACCENT_BLUE = "#3b82f6"
ACCENT_INDIGO = "#6366f1"
ACCENT_TEAL = "#0d9488"
ACCENT_RED = "#ef4444"
TEXT_DARK = "#0f172a"
BG_LIGHT = "#f8fafc"

# Food Categories
FOOD_CATEGORIES = [
    "Cooked Meals",
    "Bakery & Bread",
    "Fresh Produce",
    "Packaged Food",
    "Dairy Products",
    "Beverages",
    "Prepared Buffets",
    "Other",
]

# Quantity Units
QUANTITY_UNITS = [
    "kg",
    "meals",
    "boxes",
    "packets",
    "litres",
]

# Pickup Windows
PICKUP_WINDOWS = [
    "Within 1 hour (Urgent)",
    "Within 2 hours",
    "Today evening",
    "Tomorrow morning",
    "Flexible (Anytime today)",
]

# Storage Conditions
STORAGE_CONDITIONS = [
    "Ambient / Room Temperature",
    "Refrigerated (0°C to 4°C)",
    "Frozen (< -18°C)",
    "Hot Hold (> 60°C)",
    "Keep in dry, cool place",
]

# Common Allergen Options
ALLERGEN_OPTIONS = [
    "None / Pure Vegetarian",
    "Contains Dairy",
    "Contains Nuts / Peanuts",
    "Contains Gluten / Wheat",
    "Contains Soy",
    "Contains Eggs",
]

# Donation Statuses
STATUS_AVAILABLE = "Available"
STATUS_ACCEPTED = "Accepted"
STATUS_PICKED_UP = "Picked Up"
STATUS_COMPLETED = "Completed"
STATUS_CANCELLED = "Cancelled"

ALL_STATUSES = [
    STATUS_AVAILABLE,
    STATUS_ACCEPTED,
    STATUS_PICKED_UP,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
]

STATUS_COLORS = {
    STATUS_AVAILABLE: "#16a34a",     # Green
    STATUS_ACCEPTED: "#f59e0b",      # Amber
    STATUS_PICKED_UP: "#3b82f6",     # Blue
    STATUS_COMPLETED: "#0d9488",     # Teal
    STATUS_CANCELLED: "#ef4444",     # Red
}

STATUS_BADGES = {
    STATUS_AVAILABLE: {"bg": "#dcfce7", "text": "#166534", "icon": "🟢"},
    STATUS_ACCEPTED: {"bg": "#fef3c7", "text": "#92400e", "icon": "🟡"},
    STATUS_PICKED_UP: {"bg": "#e0e7ff", "text": "#3730a3", "icon": "🔵"},
    STATUS_COMPLETED: {"bg": "#ccfbf1", "text": "#115e59", "icon": "✅"},
    STATUS_CANCELLED: {"bg": "#fee2e2", "text": "#991b1b", "icon": "❌"},
}

# Demo Roles
ROLE_DONOR = "Donor"
ROLE_NGO = "NGO"
ROLE_VOLUNTEER = "Volunteer"
ROLE_ADMIN = "Admin"

DEMO_ROLES = [ROLE_DONOR, ROLE_NGO, ROLE_VOLUNTEER, ROLE_ADMIN]

ROLE_DESCRIPTIONS = {
    ROLE_DONOR: "Simulates food businesses, restaurants, cafeterias, and individuals listing surplus food.",
    ROLE_NGO: "Simulates community kitchens, shelters, and food banks claiming and receiving food.",
    ROLE_VOLUNTEER: "Simulates field drivers and volunteers picking up and delivering food.",
    ROLE_ADMIN: "Full system visibility, raw data audit, configuration, and sample data reset.",
}

# Unit to kg-equivalent conversion factors (illustrative standard benchmarks)
UNIT_TO_KG = {
    "kg": 1.0,
    "meals": 0.40,     # Standard 400g per meal portion
    "boxes": 2.50,     # Approx 2.5 kg box of produce/food
    "packets": 0.50,   # Approx 500g package
    "litres": 1.00,    # 1 L liquid ≈ 1 kg
}

# Environmental impact coefficients (UNEP / WRAP benchmarks)
# ~2.5 kg CO2e greenhouse gas avoided per kg of edible food rescued
CO2E_PER_KG = 2.50
# ~1,000 Liters of fresh water embedded per kg of edible food rescued
WATER_LITERS_PER_KG = 1000.0
# Standard meal size: 0.4 kg
KG_PER_MEAL = 0.40
