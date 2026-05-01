import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import http.cookiejar
from datetime import datetime

load_dotenv()

# --- CONFIG ---
COOKIE_FILE = "amazon_cookies.txt"   # Path to your exported Netscape cookies file
AMAZON_BASE = "https://www.amazon.co.uk"  # Change to amazon.com if needed
PRIME_URL = f"{AMAZON_BASE}/amazonprime"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def load_cookies(cookie_file: str) -> http.cookiejar.MozillaCookieJar:
    jar = http.cookiejar.MozillaCookieJar()
    jar.load(cookie_file, ignore_discard=True, ignore_expires=True)
    return jar


def send_discord_message(content: str, colour: int, title: str) -> None:
    """Send an embed message to a Discord channel via webhook."""
    payload = {
        "embeds": [
            {
                "title": title,
                "description": content,
                "color": colour,
                "footer": {"text": f"Checked at {datetime.now().strftime('%Y-%m-%d %H:%M')}"},
            }
        ]
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    if response.status_code not in (200, 204):
        print(f"  ⚠ Discord webhook failed ({response.status_code}): {response.text}")


def check_prime_status() -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Checking Amazon Prime status...")

    if not DISCORD_WEBHOOK_URL:
        print("  ⚠ DISCORD_WEBHOOK_URL is not set. Please add it to your .env file.")
        return

    try:
        cookies = load_cookies(COOKIE_FILE)
    except FileNotFoundError:
        print(f"  ⚠ Cookie file '{COOKIE_FILE}' not found.")
        send_discord_message(
            f"The cookie file `{COOKIE_FILE}` could not be found.\n"
            "Please export your Amazon cookies and place the file in the script directory.",
            colour=0xED4245,   # Discord red
            title="⚠️ Amazon Prime — Cookie File Missing",
        )
        return

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-GB,en;q=0.9",
    }

    session = requests.Session()
    session.cookies = cookies

    try:
        response = session.get(PRIME_URL, headers=headers, timeout=15)
    except requests.RequestException as exc:
        print(f"  ⚠ Network error: {exc}")
        return

    if response.status_code != 200:
        print(f"  ⚠ Unexpected HTTP status {response.status_code} — cookies may have expired.")
        send_discord_message(
            f"Amazon returned HTTP **{response.status_code}** when checking Prime status.\n"
            "Your cookies have likely expired. Please re-export them from your browser and "
            f"replace `{COOKIE_FILE}`.",
            colour=0xED4245,   # Discord red
            title="⚠️ Amazon Prime — Cookies Expired",
        )
        return

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text().lower()

    # Detect an un-authenticated session (sign-in wall)
    if "sign in" in page_text and "password" in page_text:
        print("  ⚠ Not logged in — cookies have expired.")
        send_discord_message(
            "Amazon is showing a sign-in page, which means your cookies have expired.\n"
            f"Please log into Amazon in your browser, re-export cookies to `{COOKIE_FILE}`, "
            "and re-run the script.",
            colour=0xED4245,   # Discord red
            title="⚠️ Amazon Prime — Cookies Expired",
        )
        return

    # Detect active Prime membership
    if "your amazon prime membership" in page_text:
        print("  ✅ Prime is ACTIVE on your account!")
        send_discord_message(
            "Your Amazon account currently has **Prime active**! 🎉\n"
            "Enjoy free delivery, Prime Video, and all other Prime perks.",
            colour=0x57F287,   # Discord green
            title="✅ Amazon Prime — Active",
        )
        return

    # No Prime detected — silent exit (no notification)
    if "try prime" in page_text or "join prime" in page_text or "start your" in page_text:
        print("  ❌ Prime is NOT active — no notification sent.")
        return

    # Ambiguous result — page layout may have changed
    print("  ❓ Could not determine Prime status. Page layout may have changed.")
    print(f"     Check manually: {PRIME_URL}")


if __name__ == "__main__":
    check_prime_status()
