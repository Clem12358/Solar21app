# Local setup for rooftop scraping

The rooftop lookup uses Selenium to launch a headless Chrome instance against Sonnendach. If Chrome/Chromium is missing, Selenium will fail to start with a WebDriverException.

For non-technical users who want a one-step setup on Debian/Ubuntu, run:

```bash
./scripts/bootstrap_browser.sh
```

What the script does:
- Detects whether Chrome/Chromium is already available and exits if so.
- Installs Google Chrome Stable via `apt` when no browser is found.
- Leaves chromedriver installation to `webdriver-manager`, which downloads a matching driver when the app starts.

If you deploy to a managed platform (e.g., Streamlit Cloud) that restricts `apt`, package a container image that already includes Chrome, or switch the Sonnendach integration to use a hosted API instead of Selenium.
