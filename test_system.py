"""Unit and integration test suite for the GVSU Lost and Found System."""

import unittest
from typing import Iterator
import app
from models import AuthenticationError, DuplicateClaimError
from system import LostAndFoundSystem


class TestLostAndFoundSystem(unittest.TestCase):
    """Test cases covering UC1 through UC7 and all requirements R1.1-R7.2."""

    def setUp(self) -> None:
        """Create a fresh LostAndFoundSystem instance before each test."""
        self.system = LostAndFoundSystem()

    def test_log_in_valid_and_invalid(self) -> None:
        """Verify R2.1 and R2.2 for UC2: Log In."""
        self.assertFalse(self.system.log_in("", ""))
        self.assertFalse(self.system.log_in("neemem", "wrong_pass"))
        self.assertIsNone(self.system.current_user)

        self.assertTrue(self.system.log_in("neemem", "gvsu2026"))
        self.assertIsNotNone(self.system.current_user)
        self.system.log_out()
        self.assertIsNone(self.system.current_user)

    def test_unauthenticated_actions_blocked(self) -> None:
        """Verify precondition that Log In is required for UC3, UC4, UC5, UC6."""
        with self.assertRaises(AuthenticationError):
            self.system.report_lost_item("Wallet", "2026-11-04", "Kirkhof")
        with self.assertRaises(AuthenticationError):
            self.system.report_found_item("Keys", "2026-11-04", "Kirkhof")
        with self.assertRaises(AuthenticationError):
            self.system.claim_item(1, "My keys")
        with self.assertRaises(AuthenticationError):
            self.system.update_report_status(1, "RESOLVED")

    def test_report_lost_and_found_items(self) -> None:
        """Verify R3.1, R3.2, R4.1, and R4.2 for UC3 and UC4."""
        self.system.log_in("neemem", "gvsu2026")
        locations = self.system.map_service.list_locations()
        self.assertIn("Mackinac Hall", locations)

        lost = self.system.report_lost_item(
            "Black Umbrella",
            "2026-11-01 08:00",
            "Mackinac Hall",
        )
        self.assertEqual(lost.report_type, "LOST")
        self.assertEqual(lost.status, "OPEN")

        found = self.system.report_found_item(
            "Silver Watch",
            "2026-11-01 10:00",
            "Kirkhof Center",
        )
        self.assertEqual(found.report_type, "FOUND")
        self.assertEqual(found.status, "OPEN")

    def test_search_for_item_and_details(self) -> None:
        """Verify R1.1 and R1.2 for UC1: Search for Item."""
        self.system.log_in("neemem", "gvsu2026")
        self.system.report_lost_item(
            "Green Notebook",
            "2026-11-02",
            "Padnos Hall",
        )
        self.system.report_found_item(
            "Red Scarf",
            "2026-11-03",
            "Fieldhouse",
        )
        self.system.log_out()

        by_kw = self.system.search_for_item(keyword="Notebook")
        self.assertEqual(len(by_kw), 1)
        details = self.system.get_report_details(by_kw[0].report_id)
        self.assertEqual(details.location, "Padnos Hall")

        with self.assertRaises(KeyError):
            self.system.get_report_details(999)

    def test_claim_item_and_reject_duplicate_claim(self) -> None:
        """Verify R5.1, R5.2, R7.1, and R7.2 for UC5 and UC7."""
        self.system.log_in("neemem", "gvsu2026")
        lost = self.system.report_lost_item(
            "Missing Laptop",
            "2026-11-02",
            "Mackinac Hall",
        )
        found = self.system.report_found_item(
            "Blue Hydro Flask",
            "2026-11-02",
            "Kirkhof Center",
        )

        with self.assertRaises(ValueError):
            self.system.claim_item(lost.report_id, "Cannot claim lost report")

        claim = self.system.claim_item(
            found.report_id,
            "Has a GVSU sticker on the lid",
        )
        self.assertEqual(claim.report_id, found.report_id)

        with self.assertRaises(DuplicateClaimError):
            self.system.claim_item(
                found.report_id,
                "Second duplicate claim attempt",
            )

    def test_update_report_status(self) -> None:
        """Verify R6.1 and R6.2 for UC6: Update Report Status."""
        self.system.log_in("neemem", "gvsu2026")
        found = self.system.report_found_item(
            "Calculator",
            "2026-11-03",
            "Mackinac Hall",
        )

        with self.assertRaises(ValueError):
            self.system.update_report_status(found.report_id, "INVALID")

        updated = self.system.update_report_status(
            found.report_id,
            "RESOLVED",
        )
        self.assertEqual(updated.status, "RESOLVED")
        self.assertEqual(
            len(self.system.search_for_item(keyword="Calculator")),
            0,
        )

    def test_automated_demo_and_interactive_cli(self) -> None:
        """Verify automated demo and interactive CLI flows in app.py."""
        app.run_automated_demo()

        inputs: Iterator[str] = iter([
            "1", "Hydro", "",
            "2", "wrong", "creds",
            "3", "Item", "2026-11-04", "Kirkhof Center",
            "2", "neemem", "gvsu2026",
            "3", "Lost Jacket", "2026-11-04", "Kirkhof Center",
            "4", "Found Ring", "2026-11-04", "Mackinac Hall",
            "5", "4", "Gold band with initials",
            "5", "4", "Duplicate claim attempt",
            "6", "4", "INVALID_STATUS",
            "6", "4", "RESOLVED",
            "99",
            "7",
        ])
        app.run_interactive_cli(input_fn=lambda _prompt: next(inputs))


if __name__ == "__main__":
    unittest.main()
