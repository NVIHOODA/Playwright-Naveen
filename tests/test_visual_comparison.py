import os
from pathlib import Path
import webbrowser
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright

LIVE_URL = "https://www.vzy.one/en"
STAGE_URL = "https://vzy-preprod.d2itz5fattn9cc.amplifyapp.com/en/"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "snapshots"
TEST_RESULTS_DIR = PROJECT_ROOT / "test-results"

BASELINE_PATH = SNAPSHOT_DIR / "live_homepage_baseline.png"
STAGE_PATH = SNAPSHOT_DIR / "stage_homepage_current.png"
DIFF_PATH = SNAPSHOT_DIR / "visual_diff.png"
REPORT_PATH = SNAPSHOT_DIR / "visual_report.html"
TRACE_PATH = TEST_RESULTS_DIR / "trace.zip"


def generate_html_report(bugs: list):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    rows_html = ""
    for b in bugs:
        rows_html += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px; text-align: center;"><b style="background:#ef4444; color:#fff; padding: 4px 10px; border-radius:4px;">BUG #{b['id']}</b></td>
            <td style="padding: 12px; font-weight: bold; color:#f87171;">{b['name']}</td>
            <td style="padding: 12px;">{b['pos']}</td>
            <td style="padding: 12px;">{b['size']}</td>
            <td style="padding: 12px; color:#f59e0b;">{b['desc']}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visual Bug Detector</title>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 20px; }}
            .summary {{ font-size: 22px; font-weight: bold; margin-bottom: 20px; color: #ef4444; }}
            .img-container {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-bottom: 30px; }}
            .card {{ background: #1e293b; padding: 10px; border-radius: 8px; width: 31%; border: 1px solid #334155; }}
            .card img {{ width: 100%; border-radius: 4px; border: 1px solid #475569; }}
            table {{ margin: 0 auto; width: 95%; border-collapse: collapse; background: #1e293b; border-radius: 8px; font-size: 15px; text-align: left; }}
            th {{ background: #0f172a; padding: 12px; color: #38bdf8; border-bottom: 2px solid #334155; }}
        </style>
    </head>
    <body>
        <h2>VZY Visual Bug Highlights</h2>
        <div class="summary">Total UI Bugs Found: {len(bugs)}</div>

        <div class="img-container">
            <div class="card">
                <h4 style="color:#38bdf8;">1. Live Production</h4>
                <img src="live_homepage_baseline.png">
            </div>
            <div class="card">
                <h4 style="color:#38bdf8;">2. Stage Build</h4>
                <img src="stage_homepage_current.png">
            </div>
            <div class="card">
                <h4 style="color:#ef4444;">3. Visual Diff (Clear Red Markers)</h4>
                <img src="visual_diff.png">
            </div>
        </div>

        <h3>Detailed Bug Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">Bug ID</th>
                    <th>Issue Type</th>
                    <th>Screen Location</th>
                    <th>Element Dimensions</th>
                    <th>Description / Reason</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else "<tr><td colspan='5' style='padding:20px; text-align:center;'>No visual bugs found! Everything matches 100%.</td></tr>"}
            </tbody>
        </table>
    </body>
    </html>
    """
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)


def scan_and_isolate_bugs(img1: Image.Image, img2: Image.Image, box_grid=60):
    diff = ImageChops.difference(img1, img2).convert("L")
    width, height = img1.size
    pix = diff.load()

    raw_cells = []
    # Grid scan for sharp differences
    for y in range(0, height, box_grid):
        for x in range(0, width, box_grid):
            diff_count = 0
            for gy in range(y, min(y + box_grid, height)):
                for gx in range(x, min(x + box_grid, width)):
                    if pix[gx, gy] > 40:
                        diff_count += 1
            if diff_count > 40:  # Minimum pixel threshold to ignore micro shimmers
                raw_cells.append(
                    [x, y, min(x + box_grid, width), min(y + box_grid, height)]
                )

    if not raw_cells:
        return []

    # Merge nearby cells into tight component boxes
    merged = []
    while raw_cells:
        curr = raw_cells.pop(0)
        has_overlap = True
        while has_overlap:
            has_overlap = False
            for i in range(len(raw_cells) - 1, -1, -1):
                other = raw_cells[i]
                if not (
                    curr[2] + 20 < other[0]
                    or curr[0] - 20 > other[2]
                    or curr[3] + 20 < other[1]
                    or curr[1] - 20 > other[3]
                ):
                    curr[0] = min(curr[0], other[0])
                    curr[1] = min(curr[1], other[1])
                    curr[2] = max(curr[2], other[2])
                    curr[3] = max(curr[3], other[3])
                    raw_cells.pop(i)
                    has_overlap = True
        merged.append(curr)

    return merged


def test_full_visual_comparison_suite():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # Standard Desktop Viewport
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print(f"\n[1/2] Capturing Live Viewport Baseline: {LIVE_URL}")
        page.goto(LIVE_URL, wait_until="networkidle")

        try:
            btn = page.get_by_role("button", name="Accept All")
            if btn.is_visible(timeout=2000):
                btn.click()
        except Exception:
            pass

        # Viewport screenshot instead of full-page so elements stay large & legible
        page.screenshot(path=str(BASELINE_PATH), full_page=False)

        print(f"[2/2] Capturing Stage Viewport: {STAGE_URL}")
        page.goto(STAGE_URL, wait_until="networkidle")

        try:
            btn = page.get_by_role("button", name="Accept All")
            if btn.is_visible(timeout=2000):
                btn.click()
        except Exception:
            pass

        page.screenshot(path=str(STAGE_PATH), full_page=False)
        browser.close()

    img_baseline = Image.open(BASELINE_PATH).convert("RGB")
    img_stage = Image.open(STAGE_PATH).convert("RGB")

    if img_baseline.size != img_stage.size:
        img_stage = img_stage.resize(img_baseline.size)

    # Find distinct visual bug areas
    boxes = scan_and_isolate_bugs(img_baseline, img_stage)

    annotated_diff = img_stage.copy()
    draw = ImageDraw.Draw(annotated_diff)
    bugs_data = []

    for idx, box in enumerate(boxes, 1):
        x1, y1, x2, y2 = box
        w, h = (x2 - x1), (y2 - y1)

        # Categorize Issue
        if w > 400 or h > 300:
            name = "Section Layout Shift"
            desc = "Poora container ya main image block displace ho gaya hai."
        elif w < 120 and h < 60:
            name = "Text / Button Mismatch"
            desc = "CTA Button, Font Color, ya Text Content missing/changed hai."
        else:
            name = "UI Component Mismatch"
            desc = "Card size, spacing margin, ya padding match nahi ho rahi."

        bugs_data.append(
            {
                "id": idx,
                "name": name,
                "pos": f"X: {x1}px | Y: {y1}px",
                "size": f"{w}px × {h}px",
                "desc": desc,
            }
        )

        # 1. Thick Red Box around bug
        draw.rectangle([x1, y1, x2, y2], outline="#ef4444", width=5)

        # 2. Pointer Arrow Target Line
        draw.line([(x1 - 30, y1 - 30), (x1, y1)], fill="#ef4444", width=4)
        draw.ellipse([x1 - 5, y1 - 5, x1 + 5, y1 + 5], fill="#ef4444")

        # 3. Yellow High-Contrast Badge for Readability
        badge_title = f" BUG #{idx}: {name} "
        draw.rectangle([x1, max(0, y1 - 30), x1 + 320, max(0, y1)], fill="#f59e0b")
        draw.text((x1 + 8, max(0, y1 - 22)), badge_title, fill="#000000")

    annotated_diff.save(DIFF_PATH)
    generate_html_report(bugs_data)

    print(f"\n[SUMMARY] Test Done! Found {len(bugs_data)} isolated UI bugs.")
    print(f"[INFO] Report file generated at: {REPORT_PATH}")

    if len(bugs_data) > 0:
        webbrowser.open(f"file://{REPORT_PATH.resolve()}")
        raise AssertionError(
            f"Visual Mismatch Detected! Found {len(bugs_data)} UI bugs. Check opened HTML Report."
        )
