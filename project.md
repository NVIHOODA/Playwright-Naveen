# Playwright Test Suite Project Specification (`PROJECT.md`)

## Project Context & Tech Stack
* [cite_start]**Framework:** Python 3.11 + Pytest + Playwright (Sync API) [cite: 5, 60, 66]
* [cite_start]**Target Application:** `https://vzy.one` [cite: 2]
* [cite_start]**Primary Test File:** `tests_Playwright/test_google.py` [cite: 1, 66]

---

## Known Issues to Resolve
1. [cite_start]**Browse By OTT Timeout Error:** `ott_heading.scroll_into_view_if_needed()` times out after 30000ms.
   * [cite_start]**Root Cause:** `page.mouse.wheel()` fails to scroll the internal container viewport, or exact text matching fails due to dynamic text rendering[cite: 107, 109].
   * [cite_start]**Required Fix:** Replace `mouse.wheel` with keyboard navigation (`PageDown`) or element scroll triggers, and use case-insensitive regex matching for `"Browse By OTT"`[cite: 109].

2. [cite_start]**Excessive Idle Sleeps:** Remove arbitrary `page.wait_for_timeout()` calls where Playwright web-first assertions (`expect(...)`) can be used instead[cite: 12, 13, 15].

---

## Short-Term Objectives & Flow

### 1. Navigation & Authentication
* [cite_start]Open `https://vzy.one` and verify navigation tabs (`Live TV`, `Movies`, `Series`, `CWG 2026`, `Sports`, `Free`)[cite: 2].
* [cite_start]Execute user login using mobile number and OTP[cite: 3].
* [cite_start]Dynamically handle the **Manage Device** screen (remove old device if present)[cite: 3].
* [cite_start]Handle **Profile Selection** screen (`JAAT` profile) if prompted[cite: 4].

### 2. OTT Rail Navigation & Filtering (Core Goal)
* [cite_start]Scroll down to reveal the **"Browse By OTT"** section reliably[cite: 77, 78].
* [cite_start]Scope the header container and click **"View All"**[cite: 78, 79].
* [cite_start]Fetch available OTT platform cards from the listing page[cite: 81].

### 3. Streaming Platform Exclusions & Validation
* **Exclusion List (Do NOT click or open):**
  * `SunNXT`
  * `Prime` (Amazon Prime)
  * `Zee5`
  * `Hotstar` (Disney+ Hotstar)
  *(Reason: These platforms redirect externally out of the web application context).*

* **Allowed Platform Validation:**
  * [cite_start]Iterate through all remaining OTT cards (e.g., `MX Player`, `SonyLiv`, `Chaupal`, `LionsgatePlay`, etc.)[cite: 82].
  * [cite_start]Open the detailed listing page for each allowed OTT platform[cite: 85].
  * [cite_start]Validate Movie and Series playback initialization flows[cite: 86, 89].
  * [cite_start]Return cleanly to the OTT listing page after each iteration[cite: 94].

---

## Guidelines for Code Refactoring
* [cite_start]**Web-First Assertions:** Use `expect(locator).to_be_visible()` instead of manual visibility checks followed by hardcoded timeouts[cite: 15, 20].
* [cite_start]**Resilient Selectors:** Prefer ARIA roles, exact text regex, or standard element locators over brittle CSS paths[cite: 22].
* [cite_start]**Error Handling:** Ensure exceptions inside individual OTT iterations do not crash the remaining platform tests[cite: 18, 93].