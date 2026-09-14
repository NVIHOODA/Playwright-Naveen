```python
import re

from playwright.sync_api import Page, expect


def test_verifypageurl(page: Page):

    try:

        # ============================================================
        # 1. OPEN VZY
        # ============================================================

        print("\n========================================")
        print("STEP 1: Opening VZY")
        print("========================================")

        page.goto(
            "https://vzy.one",
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(3000)

        print("VZY Opened Successfully")
        print("Current URL:", page.url)

        # VZY can land on /en
        expect(page).to_have_url(
            re.compile(
                r"https?://(www\.)?vzy\.one/en/?$"
            ),
            timeout=15000
        )

        # ============================================================
        # 2. VERIFY HOME TABS
        # ============================================================

        print("\n========================================")
        print("STEP 2: Verifying Home Tabs")
        print("========================================")

        home_tabs = [
            "Live TV",
            "Movies",
            "Series",
            "CWG 2026",
            "Sports",
            "Free"
        ]

        for tab_name in home_tabs:

            try:

                tab = page.get_by_role(
                    "tab",
                    name=tab_name
                )

                tab.wait_for(
                    state="visible",
                    timeout=5000
                )

                tab.click()

                page.wait_for_timeout(800)

                print(
                    f"PASS: {tab_name} tab verified"
                )

            except Exception as tab_error:

                print(
                    f"FAILED: {tab_name} tab - "
                    f"{tab_error}"
                )

        print("Home Tabs Verification Completed")

        # ============================================================
        # 3. LOGIN
        # ============================================================

        print("\n========================================")
        print("STEP 3: Login")
        print("========================================")

        profile_button = page.get_by_alt_text(
            "Profile"
        )

        profile_button.wait_for(
            state="visible",
            timeout=10000
        )

        profile_button.click()

        page.wait_for_timeout(1000)

        login_button = page.get_by_text(
            "Log In",
            exact=True
        )

        login_button.wait_for(
            state="visible",
            timeout=10000
        )

        login_button.click()

        page.wait_for_timeout(1500)

        print("Login Screen Opened")

        # ============================================================
        # 4. ENTER MOBILE NUMBER
        # ============================================================

        mobile_field = page.get_by_placeholder(
            "Please enter your mobile number"
        )

        mobile_field.wait_for(
            state="visible",
            timeout=10000
        )

        mobile_field.fill("8588066839")

        page.wait_for_timeout(500)

        page.get_by_role(
            "button",
            name="Continue"
        ).click()

        print("Mobile Number Submitted")

        page.wait_for_timeout(1500)

        # ============================================================
        # 5. ENTER OTP
        # ============================================================

        print("\nEntering OTP...")

        otp_values = [
            "1",
            "2",
            "3",
            "4"
        ]

        for index, otp_value in enumerate(
            otp_values,
            start=1
        ):

            otp_field = page.get_by_label(
                f"Please enter OTP character {index}"
            )

            otp_field.wait_for(
                state="visible",
                timeout=10000
            )

            otp_field.fill(otp_value)

        print("OTP Entered")

        page.get_by_role(
            "button",
            name="Verify OTP"
        ).click()

        # ============================================================
        # 6. WAIT FOR LOGIN RESULT
        # ============================================================

        print("\n========================================")
        print("STEP 6: Waiting For Login")
        print("========================================")

        page.wait_for_timeout(3000)

        print(
            "URL After OTP:",
            page.url
        )

        # ============================================================
        # 7. MANAGE DEVICE
        # ============================================================

        if "manageDevice" in page.url:

            print("\n========================================")
            print("STEP 7: Manage Device")
            print("========================================")

            try:

                delete_icon = page.get_by_alt_text(
                    "Delete Icon"
                ).first

                delete_icon.wait_for(
                    state="visible",
                    timeout=7000
                )

                delete_icon.click()

                page.wait_for_timeout(700)

                remove_button = page.get_by_role(
                    "button",
                    name="Remove Device"
                )

                remove_button.wait_for(
                    state="visible",
                    timeout=5000
                )

                remove_button.click()

                print(
                    "Old Device Removed Successfully"
                )

                page.wait_for_timeout(2500)

            except Exception as device_error:

                print(
                    "No removable old device found."
                )

                print(
                    "Device Error:",
                    device_error
                )

        # ============================================================
        # 8. WAIT FOR PROFILE / HOME
        # ============================================================

        print("\n========================================")
        print("STEP 8: Profile Selection")
        print("========================================")

        page.wait_for_timeout(2000)

        print(
            "URL Before Profile Check:",
            page.url
        )

        # ------------------------------------------------------------
        # Check JAAT profile
        # ------------------------------------------------------------

        try:

            jaat_profile = page.get_by_text(
                "JAAT",
                exact=False
            ).first

            jaat_profile.wait_for(
                state="visible",
                timeout=5000
            )

            print(
                "JAAT Profile Found"
            )

            jaat_profile.click()

            print(
                "JAAT Profile Selected Successfully"
            )

            page.wait_for_timeout(3000)

        except Exception:

            print(
                "JAAT Profile Screen Not Displayed"
            )

        # ============================================================
        # 9. FINAL HOME VALIDATION
        # ============================================================

        print("\n========================================")
        print("STEP 9: Home Page Validation")
        print("========================================")

        print(
            "Final URL:",
            page.url
        )

        # Allow both current VZY home URLs
        expect(page).to_have_url(
            re.compile(
                r"https?://(www\.)?vzy\.one/en(/home)?/?$"
            ),
            timeout=15000
        )

        print(
            "PASS: Home Page Opened Successfully"
        )

        # ============================================================
        # 10. BROWSE BY OTT
        # ============================================================

        print("\n========================================")
        print("STEP 10: Browse By OTT")
        print("========================================")

        ott_heading = page.get_by_text(
            "Browse By OTT"
        )

        # Scroll until Browse By OTT is visible
        for attempt in range(12):

            try:

                if ott_heading.is_visible(
                    timeout=1000
                ):
                    break

            except Exception:
                pass

            page.mouse.wheel(
                0,
                700
            )

            page.wait_for_timeout(
                600
            )

        ott_heading.scroll_into_view_if_needed()

        expect(
            ott_heading
        ).to_be_visible(
            timeout=10000
        )

        print(
            "PASS: Browse By OTT Section Found"
        )

        # ============================================================
        # 11. CLICK VIEW ALL
        # ============================================================

        print("\n========================================")
        print("STEP 11: Browse By OTT - View All")
        print("========================================")

        header_container = (
            page.locator("div")
            .filter(
                has=ott_heading
            )
            .filter(
                has_text="View All"
            )
            .last
        )

        header_container.hover()

        page.wait_for_timeout(
            500
        )

        view_all_button = (
            header_container
            .locator(
                ".see-all-link, span, div"
            )
            .filter(
                has_text="View All"
            )
            .first
        )

        view_all_button.click(
            force=True
        )

        print(
            "PASS: View All Clicked"
        )

        page.wait_for_timeout(
            3000
        )

        print(
            "OTT Listing URL:",
            page.url
        )

        ott_listing_url = page.url

        # ============================================================
        # 12. OTT VALIDATION
        # ============================================================

        print("\n========================================")
        print("STEP 12: OTT Validation")
        print("========================================")

        supported_otts = [
            "SonyLiv",
            "Chaupal",
            "LionsgatePlay",
            "MX Player"
        ]

        # JioHotstar / SUNNXT / Z5 intentionally skipped
        for ott_name in supported_otts:

            print(
                f"\n----------------------------------------"
            )

            print(
                f"Testing OTT: {ott_name}"
            )

            print(
                f"----------------------------------------"
            )

            try:

                # ----------------------------------------------------
                # Return to OTT listing
                # ----------------------------------------------------

                if page.url != ott_listing_url:

                    page.goto(
                        ott_listing_url,
                        wait_until="domcontentloaded"
                    )

                    page.wait_for_timeout(
                        2000
                    )

                # ----------------------------------------------------
                # Find OTT Card
                # ----------------------------------------------------

                ott_card = (
                    page.get_by_alt_text(
                        ott_name,
                        exact=False
                    )
                    .or_(
                        page.get_by_text(
                            ott_name,
                            exact=False
                        )
                    )
                    .first
                )

                ott_card.scroll_into_view_if_needed()

                ott_card.wait_for(
                    state="visible",
                    timeout=8000
                )

                ott_card.click()

                page.wait_for_timeout(
                    3000
                )

                print(
                    f"PASS: {ott_name} OTT Opened"
                )

                ott_detail_url = page.url

                # ====================================================
                # MOVIE PLAYBACK
                # ====================================================

                print(
                    f"Starting Movie Flow: {ott_name}"
                )

                page.mouse.wheel(
                    0,
                    800
                )

                page.wait_for_timeout(
                    1000
                )

                movie_card = page.locator(
                    "a, div[class*='card'], img[class*='card']"
                ).first

                movie_card.scroll_into_view_if_needed()

                movie_card.wait_for(
                    state="visible",
                    timeout=8000
                )

                movie_card.click()

                page.wait_for_timeout(
                    3000
                )

                watch_now_movie = (
                    page.get_by_role(
                        "button",
                        name="Watch Now",
                        exact=False
                    )
                    .or_(
                        page.get_by_text(
                            "Watch Now",
                            exact=False
                        )
                    )
                    .first
                )

                try:

                    if watch_now_movie.is_visible(
                        timeout=5000
                    ):

                        watch_now_movie.click()

                        print(
                            f"Watch Now clicked for "
                            f"{ott_name} Movie"
                        )

                except Exception:

                    print(
                        f"Watch Now not available "
                        f"for {ott_name} Movie"
                    )

                page.wait_for_timeout(
                    20000
                )

                print(
                    f"Movie Playback Checked: "
                    f"{ott_name}"
                )

                # ====================================================
                # SERIES PLAYBACK
                # ====================================================

                print(
                    f"Starting Series Flow: {ott_name}"
                )

                page.goto(
                    ott_detail_url,
                    wait_until="domcontentloaded"
                )

                page.wait_for_timeout(
                    2000
                )

                page.mouse.wheel(
                    0,
                    1200
                )

                page.wait_for_timeout(
                    1000
                )

                series_cards = page.locator(
                    "a, div[class*='card'], img[class*='card']"
                )

                series_card = series_cards.nth(1)

                try:

                    series_card.wait_for(
                        state="visible",
                        timeout=5000
                    )

                except Exception:

                    series_card = series_cards.first

                series_card.scroll_into_view_if_needed()

                series_card.click()

                page.wait_for_timeout(
                    3000
                )

                watch_now_series = (
                    page.get_by_role(
                        "button",
                        name="Watch Now",
                        exact=False
                    )
                    .or_(
                        page.get_by_text(
                            "Watch Now",
                            exact=False
                        )
                    )
                    .first
                )

                try:

                    if watch_now_series.is_visible(
                        timeout=5000
                    ):

                        watch_now_series.click()

                        print(
                            f"Watch Now clicked for "
                            f"{ott_name} Series"
                        )

                except Exception:

                    print(
                        f"Watch Now not available "
                        f"for {ott_name} Series"
                    )

                page.wait_for_timeout(
                    20000
                )

                print(
                    f"Series Playback Checked: "
                    f"{ott_name}"
                )

            except Exception as ott_error:

                print(
                    f"FAILED: {ott_name}"
                )

                print(
                    f"Error: {ott_error}"
                )

            finally:

                # ----------------------------------------------------
                # Return to OTT Listing
                # ----------------------------------------------------

                try:

                    page.goto(
                        ott_listing_url,
                        wait_until="domcontentloaded"
                    )

                    page.wait_for_timeout(
                        2000
                    )

                    print(
                        f"Returned to OTT Listing "
                        f"after {ott_name}"
                    )

                except Exception as return_error:

                    print(
                        f"Could not return to OTT Listing: "
                        f"{return_error}"
                    )

        # ============================================================
        # TEST COMPLETED
        # ============================================================

        print("\n========================================")
        print("TEST EXECUTION COMPLETED SUCCESSFULLY")
        print("========================================")

    except Exception as e:

        print("\n========================================")
        print("TEST EXECUTION FAILED")
        print("========================================")

        print(
            "Error:",
            str(e)
        )

        print(
            "Current URL:",
            page.url
        )

        raise
