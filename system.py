"""Core controller for the GVSU Lost and Found System."""

from typing import Dict, List, Optional
from models import (
    AuthenticationError,
    Claim,
    DuplicateClaimError,
    ItemReport,
    User,
)
from services import GVSUAuthService, MapAPIService


class LostAndFoundSystem:
    """Controller implementing all 7 GVSU Lost and Found System use cases."""

    def __init__(
        self,
        auth_service: Optional[GVSUAuthService] = None,
        map_service: Optional[MapAPIService] = None,
    ) -> None:
        """Initialize the system with external services and empty storage."""
        self.auth_service = auth_service or GVSUAuthService()
        self.map_service = map_service or MapAPIService()
        self.reports: Dict[int, ItemReport] = {}
        self.current_user: Optional[User] = None
        self._next_report_id: int = 1
        self._next_claim_id: int = 1

    def log_in(self, username: str, password: str) -> bool:
        """UC2: Log In via the GVSU Authentication System."""
        is_valid = self.auth_service.verify_credentials(username, password)
        if is_valid:
            self.current_user = User(
                username=username.strip().lower(),
                is_authenticated=True,
            )
            return True
        self.current_user = None
        return False

    def log_out(self) -> None:
        """Log out the currently authenticated user."""
        self.current_user = None

    def _require_login(self) -> User:
        """Ensure the current user has completed the Log In use case."""
        if self.current_user is None or not self.current_user.is_authenticated:
            raise AuthenticationError(
                "User must complete the Log In use case before this action."
            )
        return self.current_user

    def report_lost_item(
        self,
        description: str,
        time_lost: str,
        location: str,
    ) -> ItemReport:
        """UC3: Report Lost Item (includes Log In, uses Map API)."""
        user = self._require_login()
        self.map_service.display_map_for_location(location)
        report = ItemReport(
            report_id=self._next_report_id,
            report_type="LOST",
            description=description.strip(),
            timestamp=time_lost.strip(),
            location=location.strip(),
            reporter_username=user.username,
            status="OPEN",
        )
        self.reports[report.report_id] = report
        self._next_report_id += 1
        return report

    def report_found_item(
        self,
        description: str,
        time_found: str,
        location: str,
    ) -> ItemReport:
        """UC4: Report Found Item (includes Log In, uses Map API)."""
        user = self._require_login()
        self.map_service.display_map_for_location(location)
        report = ItemReport(
            report_id=self._next_report_id,
            report_type="FOUND",
            description=description.strip(),
            timestamp=time_found.strip(),
            location=location.strip(),
            reporter_username=user.username,
            status="OPEN",
        )
        self.reports[report.report_id] = report
        self._next_report_id += 1
        return report

    def search_for_item(
        self,
        keyword: str = "",
        location: str = "",
        date: str = "",
    ) -> List[ItemReport]:
        """UC1: Search for Item across saved open reports."""
        return [
            report
            for report in self.reports.values()
            if report.matches_query(
                keyword=keyword,
                location=location,
                date=date,
            )
        ]

    def get_report_details(self, report_id: int) -> ItemReport:
        """Retrieve a specific report's details by report_id."""
        if report_id not in self.reports:
            raise KeyError(f"Report #{report_id} does not exist.")
        return self.reports[report_id]

    def reject_duplicate_claim(self, report: ItemReport) -> None:
        """UC7: Reject Duplicate Claim (extends Claim Item)."""
        if len(report.claims) > 0:
            raise DuplicateClaimError(
                f"Item report #{report.report_id} has already been claimed."
            )

    def claim_item(
        self,
        report_id: int,
        ownership_details: str,
    ) -> Claim:
        """UC5: Claim Item (includes Log In, extended by UC7)."""
        user = self._require_login()
        report = self.get_report_details(report_id)
        if report.report_type != "FOUND":
            raise ValueError("Claims can only be filed for FOUND reports.")
        self.reject_duplicate_claim(report)
        claim = Claim(
            claim_id=self._next_claim_id,
            report_id=report.report_id,
            claimant_username=user.username,
            ownership_details=ownership_details.strip(),
        )
        report.claims.append(claim)
        self._next_claim_id += 1
        return claim

    def update_report_status(
        self,
        report_id: int,
        new_status: str,
    ) -> ItemReport:
        """UC6: Update Report Status (includes Log In)."""
        self._require_login()
        report = self.get_report_details(report_id)
        report.update_status(new_status)
        return report
