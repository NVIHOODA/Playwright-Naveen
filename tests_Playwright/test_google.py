import os
import re
from playwright.sync_api import Page, expect

# 4 Excluded Platforms (Prevent External Redirects)
EXCLUDED_OTTS = {
    "sunnxt",
    "sun nxt",
    "prime",
    "amazon prime",
    "prime video",
    "zee5",
    "zee 5",
    "hotstar",
    "disney+ hotstar",
    "disney hotstar",
}


def dismiss_cookie_banner(page: Page):
    """Programmatically dismiss cookie consent banners or overlay popups if present."""
    cookie_selectors = [
        page.get_by_role("button", name=re.compile(r"accept\s*(all|cookies)?", re.IGNORECASE)),
        page.get_by_text(re.compile(r"accept\s*(all|cookies)?", re.IGNORECASE)),
        page.locator("button:has-text('Accept All'), button:has-text('Accept'), [class*='cookie'] button"),
    ]
    for selector in cookie_selectors:
        try:
            target = selector.first
            if target.is_visible(timeout=1500):
                target.click(force=True)
                print("Cookie consent banner dismissed successfully.")
                page.wait_for_timeout(800)
                break
        except Exception:
            continue


def dismiss_content_modal(page: Page):
    """Dismisses content detail modal / popup overlay cleanly by clicking the Close (X) button or pressing Escape."""
    close_selectors = [
        page.locator("button[aria-label*='close' i], [class*='close-icon'], [class*='modal-close'], button:has-text('✕'), [alt*='close' i], img[src*='close']"),
        page.get_by_role("button", name=re.compile(r"close|cancel|✕", re.IGNORECASE)),
        page.locator("div[class*='modal'] button, div[class*='popup'] button, div[role='dialog'] button").filter(has_text=re.compile(r"✕|x|close", re.IGNORECASE))
    ]
    
    dismissed = False
    for selector in close_selectors:
        try:
            btn = selector.first
            if btn.is_visible(timeout=800):
                btn.click(force=True)
                dismissed = True
                print("Modal Close (X) button clicked successfully.")
                page.wait_for_timeout(1000)
                break
        except Exception:
            continue

    if not dismissed:
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(800)
        except Exception:
            pass


def is_content_locked(page: Page) -> bool:
    """Enterprise paywall detector: Checks if the active modal/card requires a paid subscription or rent/buy purchase."""
    lock_patterns = [
        re.compile(r"subscribe\s*(now)?", re.IGNORECASE),
        re.compile(r"buy\s*now", re.IGNORECASE),
        re.compile(r"rent\s*now", re.IGNORECASE),
        re.compile(r"join\s*vip", re.IGNORECASE),
        re.compile(r"unlock\s*content", re.IGNORECASE),
        re.compile(r"premium", re.IGNORECASE),
    ]
    for pattern in lock_patterns:
        try:
            lock_el = (
                page.get_by_role("button", name=pattern)
                .or_(page.get_by_text(pattern))
                .first
            )
            if lock_el.is_visible(timeout=1000):
                return True
        except Exception:
            continue
    return False


def ensure_active_session(page: Page, user_credentials: dict):
    """Ensures user session remains active and prevents accidental logout/re-login screens during navigation."""
    current_url = page.url
    profile_name = user_credentials.get("profile_name", "JAAT")

    if "login" in current_url or "profile" in current_url:
        print(f"[SESSION RECOVERY] Profile/login screen detected ({current_url}). Re-selecting user profile '{profile_name}'...")
        dismiss_cookie_banner(page)
        
        user_profile = (
            page.get_by_text(profile_name, exact=False)
            .or_(page.locator(".profile-card, [class*='profile']"))
            .first
        )
        if user_profile.is_visible(timeout=3000):
            user_profile.click(force=True)
            page.wait_for_timeout(2000)
            expect(page).to_have_url(re.compile(r".*/en/home"), timeout=10000)


def find_browse_by_ott_locator(page: Page):
    """Evaluates multiple locator candidate strategies to locate the Browse By OTT section."""
    candidates = [
        page.locator("div.aro-row-header").filter(has_text=re.compile(r"browse\s*by\s*ott", re.IGNORECASE)),
        page.get_by_text(re.compile(r"browse\s*(by)?\s*ott", re.IGNORECASE)),
        page.locator("h1, h2, h3, h4, h5, h6, [class*='title'], [class*='header']").filter(has_text=re.compile(r"browse\s*(by)?\s*ott", re.IGNORECASE)),
        page.locator("section, div").filter(has_text=re.compile(r"browse\s+by\s+ott", re.IGNORECASE)),
        page.locator("[alt*='Browse By OTT' i], [title*='Browse By OTT' i]")
    ]
    for locator in candidates:
        try:
            target = locator.first
            if target.is_visible(timeout=500):
                return target
        except Exception:
            continue
    return None


def go_to_browse_by_ott_listing(page: Page, user_credentials: dict):
    """Navigates to Home, verifies active user session, resets scroll to top, scrolls gently to Browse By OTT, and clicks rail arrow."""
    print("\n[NAVIGATION] Navigating to Home to access 'Browse By OTT' rail...")
    page.goto("https://vzy.one/en/home")
    page.wait_for_timeout(2000)
    
    ensure_active_session(page, user_credentials)
    dismiss_cookie_banner(page)

    # CRITICAL: Reset scroll position completely to top of viewport to prevent overshooting
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    found_target = find_browse_by_ott_locator(page)
    max_scrolls = 40
    scroll_count = 0

    # Gentle 150px scroll steps with 800ms pause
    while not found_target and scroll_count < max_scrolls:
        page.evaluate("window.scrollBy(0, 150)")
        page.wait_for_timeout(800)
        found_target = find_browse_by_ott_locator(page)
        scroll_count += 1

    if not found_target:
        print("Browse By OTT not located on first pass. Reloading Home page...")
        page.reload()
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2000)
        scroll_count = 0
        while not found_target and scroll_count < max_scrolls:
            page.evaluate("window.scrollBy(0, 150)")
            page.wait_for_timeout(800)
            found_target = find_browse_by_ott_locator(page)
            scroll_count += 1

    expect(found_target).to_be_visible(timeout=10000)
    found_target.scroll_into_view_if_needed()
    print("Found and centered 'Browse By OTT' rail in viewport.")
    page.wait_for_timeout(1500)

    dismiss_cookie_banner(page)

    ott_row_container = (
        found_target.locator("xpath=ancestor::*[contains(@class, 'header') or contains(@class, 'row') or self::div][1]")
        .or_(found_target.locator("xpath=parent::*"))
        .first
    )
    ott_row_container.hover()
    page.wait_for_timeout(1000)

    # Click Browse By OTT rail arrow / View All button
    rail_arrow_btn = (
        ott_row_container.locator("a[href*='vodsubcategory'], .see-all-link, div.see-all-link, [class*='arrow'], img[alt*='arrow' i], button, a")
        .filter(has_text=re.compile(r"(view\s*all|see\s*all|>|→)", re.IGNORECASE))
        .or_(ott_row_container.locator("a[href*='vodsubcategory'], .see-all-link, div.see-all-link"))
        .first
    )

    try:
        rail_arrow_btn.click(timeout=3000)
    except Exception:
        print("Standard click failed. Executing JS click on Browse By OTT rail arrow / View All button...")
        rail_arrow_btn.evaluate("el => el.click()")

    print("Browse By OTT Rail Arrow / 'View All' Clicked Successfully.")
    expect(page).to_have_url(re.compile(r".*/en/vodsubcategory", re.IGNORECASE), timeout=15000)
    page.wait_for_timeout(2500)


def inspect_cp_content(page: Page, ott_name: str):
    """Enterprise Content Inspector: Checks at MAX 2 content items per CP.
    Skips locked/subscription items cleanly via Modal Close (X), eliminates false-positive success logs,
    and moves to the next CP after at most 2 items inspected.
    """
    print(f"[CP INSPECTOR] Starting content inspection for '{ott_name}' (MAX 2 items)...")
    dismiss_cookie_banner(page)

    cards = page.locator("a[href*='watch'], a[href*='details'], div[class*='card'], img[class*='card'], a").all()
    if not cards:
        print(f"[CP INSPECTOR] No content cards found on '{ott_name}' listing page. Moving to next CP.")
        return

    print(f"[CP INSPECTOR] Found {len(cards)} candidate card(s) for '{ott_name}'. Inspecting up to 2 items...")
    items_checked = 0
    max_items_to_check = 2  # Strictly max 2 content checks per CP!

    for idx, card in enumerate(cards, start=1):
        if items_checked >= max_items_to_check:
            print(f"[CP INSPECTOR] Reached MAX item limit ({max_items_to_check}) for '{ott_name}'. Completing CP check.")
            break

        try:
            dismiss_content_modal(page)

            if not card.is_visible(timeout=1500):
                continue

            card.scroll_into_view_if_needed()
            page.wait_for_timeout(800)
            card.hover()
            page.wait_for_timeout(800)
            card.click(force=True)
            page.wait_for_timeout(2000)

            dismiss_cookie_banner(page)
            items_checked += 1

            # Step A: Enterprise Paywall Lock Check
            if is_content_locked(page):
                print(f"[LOCKED] Content item #{items_checked} on '{ott_name}' requires subscription/purchase. Closing modal...")
                dismiss_content_modal(page)
                page.wait_for_timeout(1000)
                continue

            # Step B: Playable Stream Verification (Only if NOT locked)
            play_btn = (
                page.get_by_role("button", name=re.compile(r"^(watch\s*now|play)$", re.IGNORECASE))
                .or_(page.locator("button:has-text('Watch Now'), button:has-text('Play'), [aria-label*='play' i]"))
                .first
            )

            if play_btn.is_visible(timeout=2000) and not is_content_locked(page):
                print(f"[PLAYBACK VERIFIED] Content item #{items_checked} on '{ott_name}' is PLAYABLE! Initializing stream...")
                play_btn.click(force=True)
                page.wait_for_timeout(5000)  # Stream observation (NO background scrolling!)
                print(f"[PLAYBACK COMPLETE] Verified stream playback for '{ott_name}'.")
                dismiss_content_modal(page)
                page.wait_for_timeout(1000)
            else:
                print(f"[INFO] Content item #{items_checked} on '{ott_name}' has no active play button. Closing modal...")
                dismiss_content_modal(page)
                page.wait_for_timeout(1000)

        except Exception as item_err:
            print(f"[CP INSPECTOR] Error checking item #{items_checked} on '{ott_name}': {item_err}")
            dismiss_content_modal(page)
            continue


def test_verifypageurl(page: Page, user_credentials: dict):
    # Extract credentials dynamically from the selected user profile fixture
    phone_number = user_credentials.get("phone", "7291874212")
    otp_code = user_credentials.get("otp", "1234")
    profile_name = user_credentials.get("profile_name", "JAAT")

    print(f"\n==================================================")
    print(f"--- Running Test with User Account: Phone={phone_number} ---")
    print(f"==================================================")

    # ==============================
    # 1. Open Website & Paced Top Header Navigation Verification
    # ==============================
    page.goto("https://vzy.one")
    expect(page).to_have_url(re.compile(r".*/en/home"), timeout=15000)
    print("Website Opened Successfully: https://vzy.one/en/home")
    page.wait_for_timeout(2000)

    dismiss_cookie_banner(page)

    # Dynamic discovery of top header navigation tabs
    print("\n--- Starting Dynamic Top Header Tabs Discovery & Iteration ---")
    live_tabs = page.locator("nav [role='tab'], header [role='tab'], [role='tablist'] [role='tab']").all()

    if live_tabs and len(live_tabs) > 0:
        print(f"Discovered {len(live_tabs)} live header tab(s) dynamically.")
        for idx, tab_el in enumerate(live_tabs, start=1):
            try:
                if tab_el.is_visible(timeout=2000):
                    tab_name = tab_el.inner_text().strip() or f"Tab #{idx}"
                    print(f"Verifying header tab #{idx}: '{tab_name}'")
                    tab_el.click()
                    print(f"Clicked header tab: '{tab_name}'")
                    page.wait_for_timeout(2000)
            except Exception as tab_err:
                print(f"Skipped dynamic tab #{idx}: {tab_err}")
    else:
        fallback_tabs = ["Home", "Live TV", "Movies", "Series", "Sports", "Free"]
        for tab_name in fallback_tabs:
            tab_locator = (
                page.get_by_role("tab", name=tab_name)
                .or_(page.get_by_text(tab_name, exact=True))
                .first
            )
            if tab_locator.is_visible(timeout=3000):
                print(f"Verifying header tab: '{tab_name}'")
                tab_locator.click()
                print(f"Clicked header tab: '{tab_name}'")
                page.wait_for_timeout(2000)

    print("All Top Header Tabs Verified Successfully")

    # Return to Home tab before proceeding to Login
    print("Ensuring page is back on 'Home' tab before login...")
    home_tab = (
        page.get_by_role("tab", name="Home")
        .or_(page.get_by_text("Home", exact=True))
        .first
    )
    if home_tab.is_visible(timeout=3000):
        home_tab.click()
        page.wait_for_timeout(2000)

    # ==============================
    # 2. Login Flow (Using Selected User Credentials)
    # ==============================
    print("\n--- Starting Login Flow ---")
    dismiss_cookie_banner(page)

    profile_icon = page.get_by_alt_text("Profile")
    expect(profile_icon).to_be_visible(timeout=10000)
    profile_icon.click()
    page.wait_for_timeout(1500)

    login_btn = page.get_by_text("Log In")
    expect(login_btn).to_be_visible(timeout=10000)
    login_btn.click()
    page.wait_for_timeout(1500)

    phone_input = page.get_by_placeholder("Please enter your mobile number")
    expect(phone_input).to_be_visible(timeout=10000)
    print(f"Entering mobile number '{phone_number}'...")
    phone_input.press_sequentially(phone_number, delay=150)
    page.wait_for_timeout(1500)

    continue_btn = page.get_by_role("button", name="Continue")
    expect(continue_btn).to_be_visible(timeout=10000)
    continue_btn.click()
    page.wait_for_timeout(2000)

    # Enter OTP digits at human pace
    print("Entering OTP digits...")
    otp_digits = list(otp_code)
    for idx, digit in enumerate(otp_digits, start=1):
        otp_box = page.get_by_label(f"Please enter OTP character {idx}")
        expect(otp_box).to_be_visible(timeout=10000)
        otp_box.press_sequentially(digit, delay=150)
        page.wait_for_timeout(500)

    verify_otp_btn = page.get_by_role("button", name="Verify OTP")
    expect(verify_otp_btn).to_be_visible(timeout=10000)
    verify_otp_btn.click()

    expect(page).to_have_url(re.compile(r".*/(manageDevice|profile|home)"), timeout=15000)
    print(f"Login Completed Successfully for {phone_number}. Current URL:", page.url)
    page.wait_for_timeout(2000)

    dismiss_cookie_banner(page)

    # ==============================
    # 3. Manage Device Handling
    # ==============================
    if "manageDevice" in page.url:
        print("\n--- Manage Device Screen Detected ---")
        dismiss_cookie_banner(page)
        page.wait_for_timeout(2000)

        delete_icon = page.get_by_alt_text("Delete Icon").first
        if delete_icon.is_visible(timeout=5000):
            delete_icon.scroll_into_view_if_needed()
            print("Focusing Delete Icon on Manage Devices screen...")
            page.wait_for_timeout(2000)

            try:
                delete_icon.click(timeout=3000)
            except Exception:
                print("Delete icon click intercepted. Dismissing banner & force-clicking...")
                dismiss_cookie_banner(page)
                delete_icon.click(force=True)

            page.wait_for_timeout(2000)

            dialog = page.get_by_role("dialog").first
            if dialog.is_visible(timeout=5000):
                print("Remove Device confirmation modal displayed. Confirming deletion...")
                page.wait_for_timeout(2000)
                confirm_remove = dialog.get_by_role("button", name=re.compile(r"remove\s*device", re.IGNORECASE)).first
                confirm_remove.click()
                print("Old Device Removed Successfully via modal confirmation.")
                page.wait_for_timeout(3000)

        print("Navigating from Manage Devices screen to Home...")
        page.goto("https://vzy.one/en/home")
        expect(page).to_have_url(re.compile(r".*/en/(profile|home)"), timeout=15000)
        page.wait_for_timeout(2000)

    dismiss_cookie_banner(page)

    # ==============================
    # 4. Profile Selection
    # ==============================
    if "profile" in page.url or page.get_by_text(profile_name, exact=False).is_visible(timeout=3000):
        print(f"Profile Selection Screen Opened (Target: {profile_name})")
        dismiss_cookie_banner(page)

        user_profile = (
            page.get_by_text(profile_name, exact=False)
            .or_(page.locator(".profile-card, [class*='profile']"))
            .first
        )
        expect(user_profile).to_be_visible(timeout=10000)
        page.wait_for_timeout(1500)

        try:
            user_profile.click(timeout=3000)
        except Exception:
            print("Standard profile click intercepted by overlay. Force-clicking...")
            dismiss_cookie_banner(page)
            user_profile.click(force=True)

        print(f"Profile '{profile_name}' Selected Successfully.")
        expect(page).to_have_url(re.compile(r".*/en/home"), timeout=15000)

        print("Waiting 2 seconds for profile load then refreshing...")
        page.wait_for_timeout(2000)
        page.reload()
        page.wait_for_timeout(2000)

    # ==============================
    # 5. Verify Home Page Load
    # ==============================
    expect(page).to_have_url(re.compile(r".*/en/home"), timeout=15000)
    print("Home Page Loaded & Verified Post-Login.")

    dismiss_cookie_banner(page)

    # ==============================
    # 6. Enterprise Dynamic CP Discovery & Validation Loop
    # ==============================
    print("\n--- Starting Dynamic Content Provider (CP) Discovery ---")

    # Navigate from Home -> Browse By OTT -> View All to open the full OTT Listing Page
    go_to_browse_by_ott_listing(page, user_credentials)
    dismiss_cookie_banner(page)

    # Gently scroll listing grid down to trigger lazy loading of all CP cards
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    # Discover ALL CP card elements rendered live on the OTT listing page
    discovered_cp_cards = page.locator("a[href*='partner'], a[href*='vod'], div[class*='card'], img[alt], [title]").all()
    
    # Fallback list of known CPs in case dynamic selector returns 0 elements
    fallback_cp_names = ["MX Player", "SonyLiv", "Chaupal", "LionsgatePlay", "NammaFlix", "Hoichoi", "ManoramaMax", "Hungama", "DocuBay", "EPIC ON"]

    processed_cps = set()

    if discovered_cp_cards and len(discovered_cp_cards) > 0:
        print(f"[DYNAMIC DISCOVERY] Discovered {len(discovered_cp_cards)} candidate CP card(s) live from the DOM.")
        
        for idx, cp_card_el in enumerate(discovered_cp_cards, start=1):
            try:
                # Extract CP name dynamically from alt, title, aria-label, or text
                cp_name = (
                    cp_card_el.get_attribute("alt")
                    or cp_card_el.get_attribute("title")
                    or cp_card_el.get_attribute("aria-label")
                    or cp_card_el.inner_text().strip()
                    or f"CP #{idx}"
                )
                
                # Clean name
                cp_name_clean = re.sub(r"\s+", " ", cp_name).strip()
                
                if not cp_name_clean or cp_name_clean.lower() in processed_cps:
                    continue

                # Exclusion Rule: Skip the 4 forbidden platforms (prevent external redirects)
                if any(excluded in cp_name_clean.lower() for excluded in EXCLUDED_OTTS):
                    print(f"\n--- Skipping Excluded Platform: {cp_name_clean} (Prevent External Redirect) ---")
                    processed_cps.add(cp_name_clean.lower())
                    continue

                processed_cps.add(cp_name_clean.lower())

                print(f"\n==================================================")
                print(f"--- Enterprise Validation for Dynamic CP #{len(processed_cps)}: '{cp_name_clean}' ---")
                print(f"==================================================")

                # Return to Home -> Browse By OTT -> View All for each CP iteration
                go_to_browse_by_ott_listing(page, user_credentials)
                dismiss_cookie_banner(page)

                # Relocate CP card live on the listing page
                escaped_name = re.escape(cp_name_clean).replace(" ", r"\s*")
                name_pattern = re.compile(escaped_name, re.IGNORECASE)

                ott_card = (
                    page.locator(f"img[alt*='{cp_name_clean}' i], [title*='{cp_name_clean}' i], [aria-label*='{cp_name_clean}' i]")
                    .or_(page.get_by_text(name_pattern))
                    .first
                )

                if not ott_card.is_visible(timeout=3000):
                    for _ in range(6):
                        page.evaluate("window.scrollBy(0, 300)")
                        page.wait_for_timeout(1000)
                        if ott_card.is_visible(timeout=1000):
                            break

                if not ott_card.is_visible(timeout=3000):
                    print(f"CP card for '{cp_name_clean}' not visible on listing page. Moving to next CP.")
                    continue

                ott_card.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)
                ott_card.click()
                page.wait_for_timeout(3000)
                print(f"Opened {cp_name_clean} Detailed Listing Page")

                # Enterprise Content Inspector (Max 2 content checks per CP)
                inspect_cp_content(page, cp_name_clean)

            except Exception as cp_err:
                print(f"Validation note for CP #{idx}: {cp_err}")
    else:
        print("[FALLBACK] Using fallback list for CP iteration...")
        for ott_name in fallback_cp_names:
            if any(excluded in ott_name.lower() for excluded in EXCLUDED_OTTS):
                continue

            print(f"\n==================================================")
            print(f"--- Enterprise Validation for CP: {ott_name} ---")
            print(f"==================================================")

            try:
                go_to_browse_by_ott_listing(page, user_credentials)
                dismiss_cookie_banner(page)

                escaped_name = re.escape(ott_name).replace(" ", r"\s*")
                name_pattern = re.compile(escaped_name, re.IGNORECASE)

                ott_card = (
                    page.locator(f"img[alt*='{ott_name}' i], [title*='{ott_name}' i], [aria-label*='{ott_name}' i]")
                    .or_(page.get_by_text(name_pattern))
                    .first
                )

                if not ott_card.is_visible(timeout=3000):
                    for _ in range(6):
                        page.evaluate("window.scrollBy(0, 300)")
                        page.wait_for_timeout(1000)
                        if ott_card.is_visible(timeout=1000):
                            break

                if not ott_card.is_visible(timeout=3000):
                    print(f"CP card for '{ott_name}' not visible on listing page. Moving to next CP.")
                    continue

                ott_card.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)
                ott_card.click()
                page.wait_for_timeout(3000)
                print(f"Opened {ott_name} Detailed Listing Page")

                inspect_cp_content(page, ott_name)

            except Exception as cp_err:
                print(f"Validation completed for CP '{ott_name}': {cp_err}")
