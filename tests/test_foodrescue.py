"""
FoodRescue Cloud - Comprehensive Test Suite
Validates core business logic, matching algorithm, state transitions,
data persistence, and impact calculations.
"""

import unittest
from datetime import date, datetime, timedelta
import pandas as pd

from src.analytics import calculate_impact_summary, export_donations_csv
from src.config import (
    FOOD_CATEGORIES,
    QUANTITY_UNITS,
    STATUS_ACCEPTED,
    STATUS_AVAILABLE,
    STATUS_COMPLETED,
    STATUS_PICKED_UP,
    STATUS_CANCELLED,
    UNIT_TO_KG,
)
from src.matching import get_recommendations, score_donation_match
from src.storage import (
    COLUMNS,
    create_donation,
    generate_donation_id,
    load_donations,
    load_events,
    reset_all_data,
    update_donation_status,
    validate_donation_input,
)


class TestFoodRescueStorageAndModels(unittest.TestCase):
    def setUp(self):
        # Ensure fresh state
        reset_all_data()

    def test_load_donations_returns_valid_dataframe(self):
        df = load_donations()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "load_donations() should never return an empty dataframe on fresh load")
        for col in COLUMNS:
            self.assertIn(col, df.columns, f"Missing expected column '{col}'")

    def test_generate_donation_id_format_and_uniqueness(self):
        ids = [generate_donation_id() for _ in range(100)]
        self.assertEqual(len(ids), len(set(ids)), "Generated donation IDs must be unique")
        for d_id in ids:
            self.assertTrue(d_id.startswith("FR-20"), f"ID {d_id} does not start with year prefix")
            self.assertEqual(len(d_id.split("-")), 3, f"ID {d_id} does not match expected format")

    def test_validate_donation_input_success(self):
        valid_payload = {
            "donor_name": "Test Cafe",
            "food_name": "Sandwiches",
            "category": "Cooked Meals",
            "quantity": 10.0,
            "unit": "meals",
            "expiry": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "location": "Koramangala, Bengaluru",
            "confirmed": True,
        }
        is_valid, errors = validate_donation_input(valid_payload)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_donation_input_rejections(self):
        # 1. Past expiry date
        past_payload = {
            "donor_name": "Test Cafe",
            "food_name": "Sandwiches",
            "category": "Cooked Meals",
            "quantity": 10.0,
            "unit": "meals",
            "expiry": (date.today() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "location": "Koramangala, Bengaluru",
            "confirmed": True,
        }
        is_valid, errors = validate_donation_input(past_payload)
        self.assertFalse(is_valid)
        self.assertTrue(any("past" in err.lower() for err in errors))

        # 2. Negative quantity
        neg_payload = {
            "donor_name": "Test Cafe",
            "food_name": "Sandwiches",
            "category": "Cooked Meals",
            "quantity": -5.0,
            "unit": "meals",
            "expiry": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "location": "Koramangala",
            "confirmed": True,
        }
        is_valid, errors = validate_donation_input(neg_payload)
        self.assertFalse(is_valid)
        self.assertTrue(any("greater than zero" in err.lower() for err in errors))

        # 3. Unconfirmed safety checkbox
        unconfirmed = {
            "donor_name": "Test Cafe",
            "food_name": "Sandwiches",
            "category": "Cooked Meals",
            "quantity": 5.0,
            "unit": "meals",
            "expiry": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "location": "Koramangala",
            "confirmed": False,
        }
        is_valid, errors = validate_donation_input(unconfirmed)
        self.assertFalse(is_valid)
        self.assertTrue(any("certify" in err.lower() for err in errors))

    def test_create_donation_persists_and_logs(self):
        payload = {
            "donor_name": "Automation Testing Kitchen",
            "food_name": "Fresh Test Soup",
            "category": "Cooked Meals",
            "quantity": 20.0,
            "unit": "litres",
            "expiry": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "location": "Whitefield, Bengaluru",
            "pickup_window": "Within 2 hours",
            "confirmed": True,
        }
        success, msg, created = create_donation(payload, actor="Donor")
        self.assertTrue(success)
        self.assertIsNotNone(created)
        d_id = created["id"]

        # Verify presence in database
        df = load_donations()
        matched = df[df["id"] == d_id]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched.iloc[0]["food_name"], "Fresh Test Soup")
        self.assertEqual(matched.iloc[0]["status"], STATUS_AVAILABLE)

        # Verify audit log
        events = load_events()
        event_match = [e for e in events if e.get("donation_id") == d_id]
        self.assertTrue(len(event_match) >= 1)
        self.assertEqual(event_match[0]["event"], "Created")

    def test_status_workflow_lifecycle(self):
        # Create a donation
        payload = {
            "donor_name": "Lifecycle Cafe",
            "food_name": "Lifecycle Meals",
            "category": "Cooked Meals",
            "quantity": 15.0,
            "unit": "meals",
            "expiry": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "location": "Indiranagar",
            "confirmed": True,
        }
        _, _, created = create_donation(payload)
        d_id = created["id"]

        # 1. Available -> Accepted
        ok, msg = update_donation_status(d_id, STATUS_ACCEPTED, "Food Bank A", "NGO", "Van booked")
        self.assertTrue(ok)
        df = load_donations()
        self.assertEqual(df.loc[df["id"] == d_id, "status"].values[0], STATUS_ACCEPTED)
        self.assertEqual(df.loc[df["id"] == d_id, "claimed_by"].values[0], "Food Bank A")

        # 2. Accepted -> Picked Up
        ok, msg = update_donation_status(d_id, STATUS_PICKED_UP, "Driver Dan", "Volunteer", "In transit")
        self.assertTrue(ok)
        df = load_donations()
        self.assertEqual(df.loc[df["id"] == d_id, "status"].values[0], STATUS_PICKED_UP)

        # 3. Picked Up -> Completed
        ok, msg = update_donation_status(d_id, STATUS_COMPLETED, "Food Bank A", "NGO", "Received and served")
        self.assertTrue(ok)
        df = load_donations()
        self.assertEqual(df.loc[df["id"] == d_id, "status"].values[0], STATUS_COMPLETED)
        self.assertTrue(bool(df.loc[df["id"] == d_id, "completed_at"].values[0]))

        # 4. Invalid transition: Completed -> Accepted should fail
        ok, msg = update_donation_status(d_id, STATUS_ACCEPTED, "Invalid", "NGO")
        self.assertFalse(ok)


class TestSmartMatchingEngine(unittest.TestCase):
    def test_scoring_dimensions(self):
        sample_row = {
            "id": "FR-TEST-01",
            "donor_name": "Bengaluru Kitchen",
            "food_name": "Biryani Trays",
            "category": "Cooked Meals",
            "quantity": 25.0,
            "unit": "meals",
            "expiry": (date.today() + timedelta(days=0)).strftime("%Y-%m-%d"),  # Expires TODAY
            "location": "Indiranagar, Bengaluru",
            "status": STATUS_AVAILABLE,
        }

        # Match with high alignment: Indiranagar, Cooked Meals, 20 needed, expires today
        result = score_donation_match(
            sample_row,
            preferred_area="Indiranagar",
            preferred_category="Cooked Meals",
            needed_quantity=20.0,
        )

        self.assertGreaterEqual(result["score"], 85, "Exact match expiring today should score in top tier")
        self.assertEqual(result["breakdown"]["location"], 30)
        self.assertEqual(result["breakdown"]["category"], 25)
        self.assertEqual(result["breakdown"]["quantity"], 25)
        self.assertEqual(result["breakdown"]["urgency"], 20)
        self.assertIn("Top Match", result["tier"])

        # Match with low alignment: Different area, different category, high need
        low_result = score_donation_match(
            sample_row,
            preferred_area="Delhi",
            preferred_category="Fresh Produce",
            needed_quantity=100.0,
        )
        self.assertLess(low_result["score"], result["score"])

    def test_recommendations_ranking(self):
        df = load_donations()
        recs = get_recommendations(
            donations_df=df,
            preferred_area="Indiranagar",
            preferred_category="Cooked Meals",
            needed_quantity=30.0,
        )
        self.assertFalse(recs.empty)
        # Verify scores are sorted descending
        scores = recs["match_score"].tolist()
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestAnalyticsEngine(unittest.TestCase):
    def test_calculate_impact_summary(self):
        df = load_donations()
        impact = calculate_impact_summary(df)

        self.assertGreater(impact["total_donations"], 0)
        self.assertGreaterEqual(impact["rescued_count"], 0)
        self.assertGreaterEqual(impact["rescued_kg_equivalent"], 0)
        self.assertGreaterEqual(impact["meals_saved"], 0)
        self.assertGreaterEqual(impact["co2_prevented_kg"], 0)
        self.assertGreaterEqual(impact["water_saved_liters"], 0)

    def test_empty_dataframe_impact_does_not_crash(self):
        empty_df = pd.DataFrame(columns=COLUMNS)
        impact = calculate_impact_summary(empty_df)
        self.assertEqual(impact["total_donations"], 0)
        self.assertEqual(impact["rescued_kg_equivalent"], 0.0)

    def test_export_csv(self):
        df = load_donations()
        csv_text = export_donations_csv(df)
        self.assertTrue(len(csv_text) > 50)
        self.assertIn("donor_name", csv_text)
        self.assertIn("food_name", csv_text)


if __name__ == "__main__":
    unittest.main()
