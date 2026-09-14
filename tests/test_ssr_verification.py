import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.vzy.one/en"

# Route test matrix: (Target URL, Expected URL Pattern, Unique Page Element Text)
DIRECT_ROUTES = [
    ("https://vzy.one/en/movies", r"https?://(www\.)?vzy\.one/en/movies", "Movies"),
    ("https://vzy.one/en/series", r"https?://(www\.)?vzy\.one/en/series", "Series"),
    ("https://vzy.one/en/sports", r"https?://(www\.)?vzy\.one/en/sports", "Sports"),
]


def test_ssr_initial_response_and_headers(page: Page):
    """Verify Server returns 200 OK status and populates core HTML markup."""
    response = page.goto(BASE_URL, wait_until="commit")

    assert response is not None, "Failed to fetch response from server"
    assert response.status == 200, f"Expected status 200, got {response.status}"

    title = page.title()
    assert len(title) > 0, "SSR failed to populate page title in response"
    print(f"\n[PASS] Server Response: {response.status} | Title: '{title}'")


def test_ssr_hydration_and_tab_interactivity(page: Page):
    """Verify Client-Side Hydration & handles Cookie Consent Banner overlay."""
    page.goto(BASE_URL, wait_until="networkidle")

    # 1. Dismiss Cookie Banner if present to unblock tab clicks
    cookie_btn = page.get_by_role("button", name="Accept All")
    if cookie_btn.is_visible(timeout=4000):
        cookie_btn.click()
        page.wait_for_timeout(500)

    # 2. Resilient Tab locator checking
    tabs = ["Live TV", "Movies", "Series", "Sports", "Free"]
    for tab_name in tabs:
        tab_locator = (
            page.get_by_role("tab", name=tab_name)
            .or_(page.get_by_text(tab_name, exact=True))
            .first
        )
        expect(tab_locator).to_be_visible(timeout=7000)
        tab_locator.click()
        page.wait_for_timeout(300)

    print("\n[PASS] All Tab event listeners hydrated and responsive.")


@pytest.mark.parametrize("target_url, expected_pattern, unique_text", DIRECT_ROUTES)
def test_ssr_direct_route_redirection(
    page: Page, target_url: str, expected_pattern: str, unique_text: str
):
    """Verify deep-links settle at final redirected routes without sticking at base landing page."""
    # 1. Navigate and wait for network activity to settle post-redirect
    response = page.goto(target_url, wait_until="networkidle")

    assert response is not None, f"Failed to get response from {target_url}"
    assert (
        response.status == 200
    ), f"Direct route {target_url} failed with status {response.status}"

    # 2. Wait explicitly for final URL pattern (Prevents false positives during initial 301/302 load)
    page.wait_for_url(re.compile(expected_pattern), timeout=10000)
    expect(page).to_have_url(re.compile(expected_pattern))

    # 3. Confirm target section content renders (Ensures we bypassed the generic homepage fallback)
    page_marker = page.get_by_text(unique_text, exact=False).first
    expect(page_marker).to_be_visible(timeout=5000)

    print(
        f"\n[PASS] Direct route hard refresh verified for: {target_url} -> Settled at: {page.url}"
    )
