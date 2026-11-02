import re
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        try:
            print("\n========================================")
            print("STEP 1: Opening VZY")
            print("========================================")
            page.goto("https://vzy.one", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            print("VZY Opened Successfully")
            print("Current URL:", page.url)

            print("\n========================================")
            print("STEP 2: Verifying Home Tabs")
            print("========================================")
            home_tabs = ["Live TV", "Movies", "Series", "CWG 2026", "Sports", "Free"]
            for tab_name in home_tabs:
                try:
                    tab = page.get_by_role("tab", name=tab_name)
                    tab.wait_for(state="visible", timeout=5000)
                    tab.click()
                    page.wait_for_timeout(800)
                    print(f"PASS: {tab_name} tab verified")
                except Exception as tab_error:
                    print(f"FAILED: {tab_name} tab - {tab_error}")
            print("Home Tabs Verification Completed")

            print("\n========================================")
            print("STEP 3: Login")
            print("========================================")
            profile_button = page.get_by_alt_text("Profile")
            profile_button.wait_for(state="visible", timeout=10000)
            profile_button.click()
            page.wait_for_timeout(1000)
            login_button = page.get_by_text("Log In", exact=True)
            login_button.wait_for(state="visible", timeout=10000)
            login_button.click()
            page.wait_for_timeout(1500)
            print("Login Screen Opened")

            print("\n========================================")
            print("STEP 4: Enter Mobile Number")
            print("========================================")
            mobile_field = page.get_by_placeholder("Please enter your mobile number")
            mobile_field.wait_for(state="visible", timeout=10000)
            mobile_field.fill("8588066839")
            page.wait_for_timeout(500)
            page.get_by_role("button", name="Continue").click()
            print("Mobile Number Submitted")
            page.wait_for_timeout(1500)

            print("\nEntering OTP...")
            otp_values = ["1", "2", "3", "4"]
            for index, otp_value in enumerate(otp_values, start=1):
                otp_field = page.get_by_label(f"Please enter OTP character {index}")
                otp_field.wait_for(state="visible", timeout=10000)
                otp_field.fill(otp_value)
            print("OTP Entered")
            page.get_by_role("button", name="Verify OTP").click()

            print("\n========================================")
            print("STEP 6: Waiting For Login")
            print("========================================")
            page.wait_for_timeout(3000)
            print("URL After OTP:", page.url)

            # Baaki steps yahan execute honge...
            print("\nTest flow reached successfully!")

        except Exception as main_error:
            print(f"\n❌ Test Failed with Error: {main_error}")

        finally:
            print("\n========================================")
            input("Test finished/paused. Press ENTER in this terminal to close the browser...")
            browser.close()

if __name__ == "__main__":
    run()
