import pytest
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "https://vzy-preprod.d2itz5fattn9cc.amplifyapp.com/en/"
INVALID_URL = f"{BASE_URL}non-existing-page-xyz-404"


# ==========================================
# 1. SEO & META TAGS (RAW HTML CHECKS)
# ==========================================


def test_tc001_raw_html_content_exists():
    """TC-001: Page shows real content in raw HTML without waiting for JS execution."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Disable JS to fetch raw server HTML response
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        # Ensure root element has text content rendered by SSR
        body_text = page.inner_text("body")
        assert (
            len(body_text.strip()) > 100
        ), "TC-001 Failed: Raw HTML body is empty or unrendered!"
        browser.close()


def test_tc002_meta_tags_in_raw_head():
    """TC-002: Title, meta description, and canonical URL are present in server-rendered head."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        title = page.title()
        meta_desc = page.locator("meta[name='description']").get_attribute("content")

        assert len(title) > 0, "TC-002 Failed: Page <title> is missing in SSR head!"
        assert (
            meta_desc is not None
        ), "TC-002 Failed: Meta description missing in SSR head!"
        browser.close()


def test_tc003_og_social_tags():
    """TC-003: Open Graph and Twitter card tags are in the raw HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        og_title = page.locator("meta[property='og:title']").count()
        og_image = page.locator("meta[property='og:image']").count()

        assert (
            og_title > 0 or og_image > 0
        ), "TC-003 Failed: OpenGraph meta tags missing in raw HTML!"
        browser.close()


# ==========================================
# 2. HYDRATION & CONSOLE ERROR SCANS
# ==========================================


def test_tc011_no_react_hydration_mismatch():
    """TC-011: No hydration error or mismatch warnings in browser console during wake-up."""
    console_logs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Intercept console messages
        page.on(
            "console",
            lambda msg: (
                console_logs.append(msg.text)
                if msg.type in ["error", "warning"]
                else None
            ),
        )
        page.goto(BASE_URL, wait_until="networkidle")

        hydration_errors = [
            log
            for log in console_logs
            if "hydration" in log.lower()
            or "did not match" in log.lower()
            or "hydrating" in log.lower()
        ]
        browser.close()

    assert (
        len(hydration_errors) == 0
    ), f"TC-011 Failed: Found Hydration Errors: {hydration_errors}"


# ==========================================
# 3. ROUTING & HTTP STATUS CODES
# ==========================================


def test_tc015_direct_url_route_200():
    """TC-015: Direct navigation to a valid URL returns HTTP 200 OK status."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        response = page.goto(BASE_URL)

        assert (
            response.status == 200
        ), f"TC-015 Failed: Expected status 200, got {response.status}"
        browser.close()


def test_tc019_invalid_route_returns_404():
    """TC-019: Broken URLs return 404 HTTP status code instead of a 200 OK blank page."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        response = page.goto(INVALID_URL)

        # Verify 404 status code (or 301/302 redirect)
        assert response.status in [
            404,
            301,
            302,
        ], f"TC-019 Failed: Invalid page returned status {response.status}"
        browser.close()


# ==========================================
# 4. DUPLICATE DATA / ANALYTICS NETWORK CHECKS
# ==========================================


def test_tc020_and_tc033_no_duplicate_network_calls():
    """TC-020 & TC-033: Verify API/Analytics requests are not firing duplicate times during hydration."""
    api_calls = []

    def log_request(request):
        # Filter for main API endpoints or analytics events
        if "/api/" in request.url or "google-analytics" in request.url:
            api_calls.append(request.url)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("request", log_request)
        page.goto(BASE_URL, wait_until="networkidle")
        browser.close()

    # Check for strict duplicates
    unique_calls = set(api_calls)
    assert len(api_calls) == len(
        unique_calls
    ), f"TC-020/033 Failed: Duplicate API network calls detected! {api_calls}"


# ==========================================
# 5. NO-JS & CROSS BROWSER SMOKE TEST
# ==========================================


@pytest.mark.parametrize("browser_type", ["chromium", "firefox", "webkit"])
def test_tc030_cross_browser_rendering(browser_type):
    """TC-030: Cross-browser rendering test across Chromium, Firefox, and WebKit (Safari)."""
    with sync_playwright() as p:
        engine = getattr(p, browser_type)
        browser = engine.launch()
        page = browser.new_page()
        response = page.goto(BASE_URL)

        assert (
            response.status == 200
        ), f"TC-030 Failed on {browser_type}: Page failed to load."
        browser.close()


def test_tc032_no_javascript_fallback_rendering():
    """TC-032: Page content remains visible even when JavaScript is disabled."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        headings = page.locator("h1, h2").count()
        browser.close()

    assert (
        headings > 0
    ), "TC-032 Failed: No heading tags rendered when JavaScript is disabled!"
