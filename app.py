"""Interactive CLI and automated demo for the GVSU Lost and Found System."""

import sys
from typing import Callable, List
from models import AuthenticationError, DuplicateClaimError
from system import LostAndFoundSystem


def seed_sample_data(system: LostAndFoundSystem) -> None:
    """Populate initial reports for demonstration purposes."""
    system.log_in("neemem", "gvsu2026")
    system.report_lost_item(
        description="TI-84 Plus Calculator in black case",
        time_lost="2026-11-02 09:30",
        location="Mackinac Hall",
    )
    system.report_found_item(
        description="Blue Hydro Flask water bottle",
        time_found="2026-11-03 14:15",
        location="Kirkhof Center",
    )
    system.log_out()


def run_automated_demo() -> None:
    """Execute a complete walkthrough of all 7 use cases for demo/testing."""
    print("=== GVSU LOST AND FOUND SYSTEM: RELEASE 1 PROTOTYPE DEMO ===")
    system = LostAndFoundSystem()
    seed_sample_data(system)

    print("\n[1] UC1: Search for Item (Guest User searching 'Hydro Flask')")
    results = system.search_for_item(keyword="Hydro Flask")
    for item in results:
        print(
            f" -> Found Match: ID #{item.report_id} [{item.report_type}] "
            f"{item.description} @ {item.location} ({item.status})"
        )

    print("\n[2] UC2: Log In (Invalid followed by Valid Credentials)")
    failed = system.log_in("neemem", "wrongpassword")
    print(f" -> Login with invalid password succeeded? {failed}")
    success = system.log_in("student1", "lakers123")
    print(f" -> Login with valid GVSU credentials succeeded? {success}")

    print("\n[3] UC3 & UC4: Report Lost Item & Report Found Item (w/ Map API)")
    pin = system.map_service.display_map_for_location("Mary Idema Pew Library")
    print(f" -> Map API Response: {pin}")
    lost_rep = system.report_lost_item(
        description="AirPods Pro charging case",
        time_lost="2026-11-04 11:00",
        location="Mary Idema Pew Library",
    )
    print(f" -> Created Lost Report #{lost_rep.report_id}: {lost_rep.status}")

    found_rep = system.report_found_item(
        description="GVSU Lanyard with room key",
        time_found="2026-11-04 12:00",
        location="Fieldhouse",
    )
    print(f" -> Created Found Report #{found_rep.report_id}: {found_rep.status}")

    print("\n[4] UC5: Claim Item (Valid Claim on Report #2)")
    claim = system.claim_item(
        report_id=2,
        ownership_details="Has a GVSU Rowing sticker on the bottom.",
    )
    print(
        f" -> Claim #{claim.claim_id} saved for Report #{claim.report_id} "
        f"by {claim.claimant_username}."
    )

    print("\n[5] UC7: Reject Duplicate Claim (Second Claim on Report #2)")
    try:
        system.claim_item(
            report_id=2,
            ownership_details="Trying to claim the same bottle again.",
        )
    except DuplicateClaimError as exc:
        print(f" -> Duplicate Claim Rejected: {exc}")

    print("\n[6] UC6: Update Report Status (Mark Report #2 as RESOLVED)")
    updated = system.update_report_status(report_id=2, new_status="RESOLVED")
    print(f" -> Report #{updated.report_id} status is now: {updated.status}")
    post_search = system.search_for_item(keyword="Hydro Flask")
    print(
        f" -> Open search results for 'Hydro Flask' after resolution: "
        f"{len(post_search)} items."
    )
    print("\n=== DEMO COMPLETE ===")


def run_interactive_cli(
    input_fn: Callable[[str], str] = input,
) -> None:
    """Run the interactive text menu for live user testing."""
    system = LostAndFoundSystem()
    seed_sample_data(system)

    menu_lines: List[str] = [
        "\n--- GVSU Lost and Found System ---",
        "1. Search for Item (UC1)",
        "2. Log In (UC2)",
        "3. Report Lost Item (UC3)",
        "4. Report Found Item (UC4)",
        "5. Claim Item (UC5 / UC7)",
        "6. Update Report Status (UC6)",
        "7. Exit",
    ]

    while True:
        for line in menu_lines:
            print(line)
        choice = input_fn("Select an option (1-7): ").strip()

        if choice == "1":
            kw = input_fn("Enter search keyword (or blank): ").strip()
            loc = input_fn("Enter location filter (or blank): ").strip()
            matches = system.search_for_item(keyword=kw, location=loc)
            print(f"Found {len(matches)} matching open report(s):")
            for rep in matches:
                print(
                    f"  [#{rep.report_id}] ({rep.report_type}) "
                    f"{rep.description} - {rep.location} @ {rep.timestamp}"
                )
        elif choice == "2":
            user = input_fn("GVSU Username: ").strip()
            pw = input_fn("Password: ").strip()
            if system.log_in(user, pw):
                print(f"Logged in successfully as '{user}'.")
            else:
                print("Error: Invalid GVSU credentials.")
        elif choice in ("3", "4"):
            desc = input_fn("Item description: ").strip()
            when = input_fn("Date/Time (YYYY-MM-DD HH:MM): ").strip()
            print(
                "Available Map API Locations: "
                + ", ".join(system.map_service.list_locations())
            )
            loc = input_fn("Select location: ").strip()
            try:
                if choice == "3":
                    rep = system.report_lost_item(desc, when, loc)
                else:
                    rep = system.report_found_item(desc, when, loc)
                print(f"Report #{rep.report_id} saved as OPEN.")
            except AuthenticationError as exc:
                print(f"Authentication Required: {exc}")
        elif choice == "5":
            rep_id = int(input_fn("Enter Found Report ID to claim: ").strip())
            proof = input_fn("Enter proof of ownership details: ").strip()
            try:
                clm = system.claim_item(rep_id, proof)
                print(f"Claim #{clm.claim_id} submitted successfully.")
            except (
                AuthenticationError,
                DuplicateClaimError,
                KeyError,
                ValueError,
            ) as exc:
                print(f"Claim Error: {exc}")
        elif choice == "6":
            rep_id = int(input_fn("Enter Report ID to update: ").strip())
            status = input_fn("New status (OPEN or RESOLVED): ").strip()
            try:
                rep = system.update_report_status(rep_id, status)
                print(f"Report #{rep.report_id} updated to {rep.status}.")
            except (AuthenticationError, KeyError, ValueError) as exc:
                print(f"Update Error: {exc}")
        elif choice == "7":
            print("Exiting GVSU Lost and Found System.")
            break
        else:
            print("Invalid option. Please choose 1-7.")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_automated_demo()
    else:
        run_interactive_cli()
