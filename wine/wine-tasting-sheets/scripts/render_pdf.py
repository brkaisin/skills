#!/usr/bin/env python3
"""Print the HTML sheets to a PDF with a headless Chromium-family browser.

Usage:
  python3 render_pdf.py sheets.html sheets.pdf

Looks for Chrome, Chromium, Edge or Brave (or the path in $CHROME_PATH).
Standard library only. If no browser is found, it explains how to print by hand.
"""
import os, pathlib, shutil, subprocess, sys

CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "brave-browser", "chrome"]

def find_browser():
    for c in CANDIDATES:
        if c and os.path.exists(c):
            return c
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    return None

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    browser = find_browser()
    if not browser:
        sys.exit("No Chrome/Chromium/Edge found. Set CHROME_PATH, or open the HTML in a browser and print it: "
                 "destination 'Save as PDF', layout Landscape, margins None, 'Background graphics' on.")
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-first-run",
           "--virtual-time-budget=20000", f"--print-to-pdf={out}", src.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not out.exists() or out.stat().st_size == 0:
        # older browsers do not know --headless=new
        cmd[1] = "--headless"
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not out.exists() or out.stat().st_size == 0:
        sys.exit("PDF not produced.\n" + r.stderr[-2000:])
    print(f"Wrote {out} with {os.path.basename(browser)}")

if __name__ == "__main__":
    main()
