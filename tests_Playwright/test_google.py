from playwright.sync_api import Page, expect


def test_verifypageurl(page: Page):

    # ==============================
    # Open Website
    # ==============================

    page.goto("https://vzy.one")

    expect(page).to_have_url("https://vzy.one/en/home", timeout=15000)

    page.wait_for_timeout(3000)

    print("Website Opened Successfully")

    # ==============================
    # Verify Home Tabs
    # ==============================

    page.get_by_role("tab", name="Live TV").click()

    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Movies").click()

    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Series").click()

    page.wait_for_timeout(2000)

    page.get_by_role("tab", name="Sports").click()

    page.wait_for_timeout(2000)

    print("All Home Tabs Verified")

    # ==============================
    # Login
    # ==============================

    page.get_by_alt_text("Profile").click()

    page.wait_for_timeout(2000)

    page.get_by_text("Log In").click()

    page.wait_for_timeout(2000)

    page.get_by_placeholder("Please enter your mobile number").fill("8588066839")

    page.get_by_role("button", name="Continue").click()

    page.wait_for_timeout(3000)

    # ==============================
    # Enter OTP
    # ==============================

    page.get_by_label("Please enter OTP character 1").fill("0")

    page.get_by_label("Please enter OTP character 2").fill("0")

    page.get_by_label("Please enter OTP character 3").fill("0")

    page.get_by_label("Please enter OTP character 4").fill("0")

    page.wait_for_timeout(1000)

    page.get_by_role("button", name="Verify OTP").click()

    page.wait_for_timeout(5000)

    print("Login Completed Successfully")

    print("Current URL :", page.url)

    # ==============================
    # Manage Device Handling
    # ==============================

    if "manageDevice" in page.url:

        print("Manage Device Page Opened")

        delete_icons = page.get_by_alt_text("Delete Icon")

        if delete_icons.count() > 0:

            delete_icons.first.click()

            page.wait_for_timeout(2000)

            page.get_by_role("button", name="Remove Device").click()

            page.wait_for_timeout(5000)

            print("Old Device Removed Successfully")

        else:

            print("No Old Device Found")
    # ==============================
    # Profile Selection
    # ==============================

    page.wait_for_timeout(3000)

    if page.get_by_text("JAAT").count() > 0:

        page.get_by_text("JAAT").first.click()

        page.wait_for_timeout(5000)

        print("JAAT Profile Selected Successfully")

    else:

        print("Profile Selection Screen Not Displayed")

    # ==============================
    # Verify Home Page
    # ==============================

    expect(page).to_have_url("https://vzy.one/en/home", timeout=15000)

    print("Home Page Opened")

    # ==============================
    # Scroll Home Page
    # ==============================

    for i in range(3):

        page.mouse.wheel(0, 1500)

        page.wait_for_timeout(2000)

    print("Home Page Scroll Completed")

    # ==============================
    # Browse By OTT
    # ==============================

    browse_section = page.get_by_text("Browse By OTT", exact=False)

    browse_section.wait_for(state="visible", timeout=15000)

    browse_section.scroll_into_view_if_needed()

    page.wait_for_timeout(3000)

    print("Browse By OTT Section Found")

    # ==============================
    # Click View All
    # ==============================

    view_all = page.locator(".see-all-link").filter(has_text="View All")

    view_all.first.wait_for(state="visible", timeout=10000)

    view_all.first.click()

    page.wait_for_timeout(5000)

    print("Browse By OTT View All Clicked Successfully")
