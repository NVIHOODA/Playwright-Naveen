from playwright.sync_api import Page, expect

def test_verifypageurl(page: Page):

    # Open Website
    page.goto("https://vzy.one")

    # Verify Home Page
    expect(page).to_have_url("https://vzy.one/en/home")

    # Live TV
    page.get_by_role("tab", name="Live TV").click()
    page.wait_for_timeout(2000)

    # Movies
    page.get_by_role("tab", name="Movies").click()
    page.wait_for_timeout(2000)

    # Series
    page.get_by_role("tab", name="Series").click()
    page.wait_for_timeout(2000)

    # Sports
    page.get_by_role("tab", name="Sports").click()
    page.wait_for_timeout(2000)

    # Profile Icon
    page.get_by_alt_text("Profile").click()
    page.wait_for_timeout(2000)

    # Login Button
    page.get_by_text("Log In").click()
    page.wait_for_timeout(2000)

    # Mobile Number
    page.get_by_placeholder(
        "Please enter your mobile number"
    ).fill("8588066839")

    # Continue
    page.get_by_role("button", name="Continue").click()
    page.wait_for_timeout(3000)

    # OTP
    page.get_by_label("Please enter OTP character 1").fill("0")
    page.get_by_label("Please enter OTP character 2").fill("0")
    page.get_by_label("Please enter OTP character 3").fill("0")
    page.get_by_label("Please enter OTP character 4").fill("0")

    page.wait_for_timeout(1000)

    # Verify OTP
    page.get_by_role("button", name="Verify OTP").click()

    page.wait_for_timeout(5000)

    print("Current URL =", page.url)
    print("Login Flow Completed Successfully")

    # Browser yahin ruk jayega
    page.pause()