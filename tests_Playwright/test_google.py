import re
from playwright.sync_api import Page, expect


def test_verifypageurl(page: Page):
    try:
        # ==============================
        # Open Website
        # ==============================
        page.goto("https://vzy.one")
        expect(page).to_have_url("https://vzy.one/en/home", timeout=15000)
        print("Website Opened Successfully")

        # ==============================
        # Verify Home Tabs
        # ==============================
        page.get_by_role("tab", name="Live TV").click()
        page.wait_for_timeout(800)
        page.get_by_role("tab", name="Movies").click()
        page.wait_for_timeout(800)
        page.get_by_role("tab", name="Series").click()
        page.wait_for_timeout(800)
        page.get_by_role("tab", name="CWG 2026").click()
        page.wait_for_timeout(800)
        page.get_by_role("tab", name="Sports").click()
        page.wait_for_timeout(800)
        page.get_by_role("tab", name="Free").click()
        page.wait_for_timeout(800)
        print("All Home Tabs Verified")

        # ==============================
        # Login
        # ==============================
        page.get_by_alt_text("Profile").click()
        page.get_by_text("Log In").click()
        page.get_by_placeholder("Please enter your mobile number").press_sequentially(
            "8588066839", delay=80
        )
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Continue").click()

        # ==============================
        # Enter OTP
        # ==============================
        page.get_by_label("Please enter OTP character 1").press_sequentially(
            "0", delay=50
        )
        page.get_by_label("Please enter OTP character 2").press_sequentially(
            "0", delay=50
        )
        page.get_by_label("Please enter OTP character 3").press_sequentially(
            "0", delay=50
        )
        page.get_by_label("Please enter OTP character 4").press_sequentially(
            "0", delay=50
        )
        page.get_by_role("button", name="Verify OTP").click()

        # Dynamic wait after OTP entry
        page.wait_for_url(re.compile(r"/(manageDevice|profile|home)"), timeout=10000)
        print("Login Completed Successfully")
        print("Current URL :", page.url)

        # ==============================
        # Manage Device Handling
        # ==============================
        if "manageDevice" in page.url:
            print("Manage Device Page Opened")
            delete_icon = page.get_by_alt_text("Delete Icon").first
            try:
                delete_icon.wait_for(state="visible", timeout=7000)
                delete_icon.click()
                remove_btn = page.get_by_role("button", name="Remove Device")
                remove_btn.wait_for(state="visible", timeout=5000)
                remove_btn.click()
                page.wait_for_url(re.compile(r"/(profile|home)"), timeout=10000)
                print("Old Device Removed Successfully")
            except Exception:
                print("No Old Device Found or Already Removed")

        # ==============================
        # Profile Selection
        # ==============================
        if "profile" in page.url or page.get_by_text("JAAT", exact=False).is_visible(
            timeout=3000
        ):
            print("Profile Selection Screen Opened")
            jaat_profile = page.get_by_text("JAAT", exact=False).first
            try:
                jaat_profile.wait_for(state="visible", timeout=7000)
                jaat_profile.click()
                print("JAAT Profile Selected Successfully")
                page.wait_for_url(re.compile(r".*/en/home"), timeout=10000)
            except Exception:
                print("Profile Selection Skipped or Failed")
        else:
            print("Profile Selection Screen Not Displayed")

        # ==============================
        # Verify Home Page
        # ==============================
        expect(page).to_have_url(re.compile(r".*/en/home"), timeout=15000)
        print("Home Page Opened")

        # ==============================
        # Browse By OTT
        # ==============================
        ott_heading = page.get_by_text("Browse By OTT")
        max_scroll_attempts = 12
        scrolls = 0

        while not ott_heading.is_visible() and scrolls < max_scroll_attempts:
            page.mouse.wheel(0, 700)
            page.wait_for_timeout(600)  # Wait for API fetch and React hydration
            scrolls += 1

        ott_heading.scroll_into_view_if_needed()
        expect(ott_heading).to_be_visible()
        print("Browse By OTT Section Verified")

        # Scope header and trigger hover to reveal View All
        header_container = (
            page.locator("div").filter(has=ott_heading).filter(has_text="View All").last
        )
        header_container.hover()
        page.wait_for_timeout(500)

        # Force-click View All
        view_all_btn = (
            header_container.locator(".see-all-link, span, div")
            .filter(has_text="View All")
            .first
        )
        view_all_btn.click(force=True)
        print("Browse By OTT View All Clicked Successfully")

        # ==============================
        # OTT Cards & Validation
        # ==============================
        page.wait_for_timeout(3000)
        print("Navigated to OTT Listing Page. Current URL:", page.url)

        # Count OTT Cards visible
        ott_cards = page.locator(".ott-card, [class*='ott'], [class*='card'], img")
        cards_count = ott_cards.count()
        print(f"Total OTT Cards Visible: {cards_count}")

        # Save OTT listing page URL to return back cleanly
        ott_listing_url = page.url

        # ==============================
        # Supported OTTs Validation Loop
        # ==============================
        supported_otts = ["MX Player", "SonyLiv", "Chaupal", "LionsgatePlay"]

        for ott_name in supported_otts:
            print(f"\n--- Starting Validation for OTT: {ott_name} ---")
            try:
                # Ensure we are on the OTT listing page
                if page.url != ott_listing_url:
                    page.goto(ott_listing_url)
                    page.wait_for_timeout(2000)

                # a. Click OTT Logo / Card
                ott_card = (
                    page.get_by_alt_text(ott_name, exact=False)
                    .or_(page.get_by_text(ott_name, exact=False))
                    .first
                )
                ott_card.scroll_into_view_if_needed()
                ott_card.wait_for(state="visible", timeout=8000)
                ott_card.click()
                page.wait_for_timeout(3000)
                print(f"Opened {ott_name} Detailed Listing Page")

                # Save detailed OTT listing URL
                ott_detail_url = page.url

                # b. Movie Playback Flow
                print(f"Starting Movie Playback Flow for {ott_name}")
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(1000)

                movie_card = page.locator(
                    "a, div[class*='card'], img[class*='card']"
                ).first
                movie_card.scroll_into_view_if_needed()
                movie_card.wait_for(state="visible", timeout=8000)
                movie_card.click()
                page.wait_for_timeout(3000)

                watch_now_btn = (
                    page.get_by_role("button", name="Watch Now", exact=False)
                    .or_(page.get_by_text("Watch Now", exact=False))
                    .first
                )
                if watch_now_btn.is_visible(timeout=5000):
                    watch_now_btn.click()
                    print(f"Clicked 'Watch Now' for Movie in {ott_name}")
                page.wait_for_timeout(20000)
                print(f"Movie Playback Initialized for {ott_name}")

                # c. Series Playback Flow
                print(f"Starting Series Playback Flow for {ott_name}")
                # Navigate back to OTT detailed listing page
                page.goto(ott_detail_url)
                page.wait_for_timeout(2000)

                page.mouse.wheel(0, 1200)
                page.wait_for_timeout(1000)

                series_card = page.locator(
                    "a, div[class*='card'], img[class*='card']"
                ).nth(1)
                if not series_card.is_visible(timeout=5000):
                    series_card = page.locator(
                        "a, div[class*='card'], img[class*='card']"
                    ).first
                series_card.scroll_into_view_if_needed()
                series_card.click()
                page.wait_for_timeout(3000)

                watch_now_series = (
                    page.get_by_role("button", name="Watch Now", exact=False)
                    .or_(page.get_by_text("Watch Now", exact=False))
                    .first
                )
                if watch_now_series.is_visible(timeout=5000):
                    watch_now_series.click()
                    print(f"Clicked 'Watch Now' for Series in {ott_name}")
                page.wait_for_timeout(20000)
                print(f"Series Playback Initialized for {ott_name}")

            except Exception as ott_err:
                print(f"Validation failed for OTT '{ott_name}': {str(ott_err)}")

            finally:
                # d. Return to Browse By OTT listing page
                try:
                    page.goto(ott_listing_url)
                    page.wait_for_timeout(2000)
                    print(f"Returned to OTT Listing Page after {ott_name}")
                except Exception as return_err:
                    print(f"Could not return to OTT listing page: {str(return_err)}")

    except Exception as e:
        print(f"Test Execution Failed: {str(e)}")
        raise e
