def test_google(page):
    page.goto("https://www.google.com")
    print("Page Title is:", page.title())
    assert "Google" in page.title()
