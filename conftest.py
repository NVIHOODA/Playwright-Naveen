import json
import os
import pytest
from playwright.sync_api import sync_playwright


def pytest_addoption(parser):
    parser.addoption(
        "--user",
        action="store",
        default="user1",
        help="Select user account to log in with (e.g. user1 or user2)",
    )


@pytest.fixture
def user_credentials(request):
    """Fixture that loads credentials for the selected user from users.json or environment variables."""
    user_key = os.getenv("TEST_USER") or request.config.getoption("--user") or "user1"

    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            users_data = json.load(f)
            if user_key in users_data:
                print(f"\n[AUTH CONFIG] Selected user profile: '{user_key}' ({users_data[user_key]['phone']})")
                return users_data[user_key]

    # Default fallback mapping
    default_users = {
        "user1": {"phone": "7291874212", "otp": "1234", "profile_name": "JAAT"},
        "user2": {"phone": "8588066839", "otp": "0000", "profile_name": "JAAT"},
    }
    selected = default_users.get(user_key, default_users["user1"])
    print(f"\n[AUTH CONFIG] Loaded user profile: '{user_key}' ({selected['phone']})")
    return selected


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        yield page
        browser.close()
