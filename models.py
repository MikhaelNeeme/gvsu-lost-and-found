"""Domain models for the GVSU Lost and Found System."""

from dataclasses import dataclass, field
from typing import List


class DuplicateClaimError(Exception):
    """Exception raised when a duplicate claim is submitted for an item."""


class AuthenticationError(Exception):
    """Exception raised when an unauthenticated user attempts a protected task."""


@dataclass
class User:
    """Represents a GVSU User interacting with the Lost and Found System.

    Attributes:
        username: The GVSU username or email of the user.
        is_authenticated: Boolean indicating whether the user is logged in.
    """

    username: str
    is_authenticated: bool = False


@dataclass
class Claim:
    """Represents an ownership claim submitted for a found item report.

    Attributes:
        claim_id: Unique identifier for the claim.
        report_id: Identifier of the associated found item report.
        claimant_username: Username of the GVSU User claiming the item.
        ownership_details: Proof of ownership provided by the claimant.
    """

    claim_id: int
    report_id: int
    claimant_username: str
    ownership_details: str


@dataclass
class ItemReport:
    """Represents a lost or found item report in the system.

    Attributes:
        report_id: Unique numeric identifier for the report.
        report_type: Either 'LOST' or 'FOUND'.
        description: Text description of the item.
        timestamp: Date and time when the item was lost or found.
        location: Campus location selected via the Map API.
        reporter_username: Username of the user who created the report.
        status: Current report status, either 'OPEN' or 'RESOLVED'.
        claims: List of Claim objects associated with this report.
    """

    report_id: int
    report_type: str
    description: str
    timestamp: str
    location: str
    reporter_username: str
    status: str = "OPEN"
    claims: List[Claim] = field(default_factory=list)

    def update_status(self, new_status: str) -> None:
        """Update the status of the report (e.g., 'OPEN' or 'RESOLVED')."""
        normalized = new_status.strip().upper()
        if normalized not in ("OPEN", "RESOLVED"):
            raise ValueError("Status must be 'OPEN' or 'RESOLVED'.")
        self.status = normalized

    def matches_query(
        self,
        keyword: str = "",
        location: str = "",
        date: str = "",
    ) -> bool:
        """Return True if this report is OPEN and matches search filters."""
        if self.status != "OPEN":
            return False
        kw_match = (
            not keyword
            or keyword.lower() in self.description.lower()
        )
        loc_match = (
            not location
            or location.lower() in self.location.lower()
        )
        date_match = (
            not date
            or date.lower() in self.timestamp.lower()
        )
        return kw_match and loc_match and date_match
