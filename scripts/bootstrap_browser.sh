#!/usr/bin/env bash
set -euo pipefail

# Best-effort installer for a headless Chrome + chromedriver stack on Debian/Ubuntu.
# - Installs Google Chrome Stable if no Chrome/Chromium is found on the PATH.
# - Ensures chromedriver is present via webdriver-manager at runtime.
# Usage: ./scripts/bootstrap_browser.sh

if command -v google-chrome >/dev/null || command -v google-chrome-stable >/dev/null || command -v chromium-browser >/dev/null || command -v chromium >/dev/null; then
  echo "Chrome/Chromium already installed. Skipping browser install."
  exit 0
fi

if ! command -v curl >/dev/null; then
  echo "Installing curl (required to download Chrome)..."
  sudo apt-get update && sudo apt-get install -y curl
fi

echo "Installing Google Chrome Stable (headless capable)..."
curl -fsSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /tmp/google-chrome-stable.deb
sudo apt-get update
sudo apt-get install -y /tmp/google-chrome-stable.deb

echo "Chrome installation complete. webdriver-manager will fetch a matching driver at runtime."
