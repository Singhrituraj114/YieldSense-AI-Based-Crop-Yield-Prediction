"""
Visits deployed Streamlit apps with a real headless browser to prevent them
from sleeping after inactivity. A plain HTTP request does NOT work for this:
a sleeping Streamlit Cloud app returns a static HTML shell with a 200 status
without ever launching the underlying Python app, so only an actual browser
render (which Streamlit Cloud detects as real traffic) resets the sleep timer.
"""
import sys
import time
from playwright.sync_api import sync_playwright

APP_URLS = [
    "https://yieldsense-ai-based-crop-yield-prediction.streamlit.app/",
    "https://graphshield-fraud-detection.streamlit.app/",
    "https://airline-satisfaction-ai-n884vzrtwkqjelqzvjyg4x.streamlit.app/",
    "https://ironsight-industrial-safety-intelligence-app-cc3rvknsvgfsrjfhr.streamlit.app/",
    "https://r2js9oqssf2xiksi3gwuyd.streamlit.app/",
    "https://riskinsight-xgb-credit-risk-prediction-explainability.streamlit.app/",
]


def visit(page, url):
    page.goto(url, wait_until="networkidle", timeout=120_000)

    app_frame = None
    for _ in range(24):  # up to ~2 minutes for a cold start
        for f in page.frames:
            if "/~/+/" in f.url:
                app_frame = f
        if app_frame:
            try:
                if len(app_frame.inner_text("body")) > 200:
                    break
            except Exception:
                pass
        time.sleep(5)

    return bool(app_frame and len(app_frame.inner_text("body")) > 200)


def main():
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in APP_URLS:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            try:
                if visit(page, url):
                    print(f"[OK] {url} is awake and rendering content.")
                else:
                    print(f"[FAIL] {url} did not render expected content within the timeout.")
                    failures.append(url)
            finally:
                page.close()
        browser.close()

    if failures:
        print(f"\n{len(failures)} app(s) failed to wake: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
