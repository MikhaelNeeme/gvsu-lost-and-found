"""External service adapters for GVSU Authentication System and Map API."""

from typing import Dict, List


class GVSUAuthService:
    """Adapter for the external GVSU Authentication System actor."""

    def __init__(self) -> None:
        """Initialize the authentication service with valid test accounts."""
        self._valid_accounts: Dict[str, str] = {
            "neemem": "gvsu2026",
            "student1": "lakers123",
            "faculty1": "anchorup",
        }

    def verify_credentials(self, username: str, password: str) -> bool:
        """Return True if the username and password are valid GVSU logins."""
        if not username or not password:
            return False
        expected = self._valid_accounts.get(username.strip().lower())
        return expected is not None and expected == password


class MapAPIService:
    """Adapter for the external Map API actor."""

    def __init__(self) -> None:
        """Initialize supported GVSU campus locations."""
        self._campus_locations: Dict[str, str] = {
            "Mackinac Hall": "42.9665 N, 85.8869 W",
            "Kirkhof Center": "42.9629 N, 85.8887 W",
            "Mary Idema Pew Library": "42.9628 N, 85.8913 W",
            "Fieldhouse": "42.9680 N, 85.8895 W",
            "Padnos Hall": "42.9658 N, 85.8878 W",
        }

    def list_locations(self) -> List[str]:
        """Return a list of valid campus locations from the Map API."""
        return list(self._campus_locations.keys())

    def display_map_for_location(self, location: str) -> str:
        """Simulate displaying the map and returning pin coordinates."""
        coords = self._campus_locations.get(
            location,
            "42.9634 N, 85.8885 W (GVSU Allendale Campus)",
        )
        return f"[Map API Pin: {location} @ {coords}]"
