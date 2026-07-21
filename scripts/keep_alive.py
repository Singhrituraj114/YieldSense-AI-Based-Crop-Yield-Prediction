"""
Visits the deployed Streamlit app with a real headless browser to prevent it
from sleeping after inactivity. A plain HTTP request does NOT work for this:
a sleeping Streamlit Cloud app returns a static HTML shell with a 200 status
without ever launching the underlying Python app, so only an actual browser
render (which Streamlit Cloud detects as real traffic) resets the sleep timer.
"""
import sys
import time
from playwright.sync_api import sync_playwright

APP_URL = "https://yieldsense-ai-based-crop-yield-prediction.streamlit.app/"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(APP_URL, wait_until="networkidle", timeout=120_000)

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

        if app_frame and len(app_frame.inner_text("body")) > 200:
            print("App is awake and rendering content.")
            browser.close()
            return 0

        print("App did not render expected content within the timeout.")
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
