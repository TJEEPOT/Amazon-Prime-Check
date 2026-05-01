# 🛒 Amazon Prime Checker

A lightweight Python script that checks whether your Amazon account currently has Prime active, and notifies you via a **Discord webhook**. Useful for shared accounts where Prime may come and go without warning.

Notifications are only sent when:
- ✅ Prime **is active** on your account
- ⚠️ Your **cookies have expired** and need to be refreshed

No notification is sent when Prime is simply inactive — keeping your Discord channel noise-free.

---

## How It Works

Since Amazon has no public API for consumer Prime status, the script mimics a logged-in browser session using exported cookies. It fetches your Prime membership page, parses the response, and posts a colour-coded embed to a Discord channel.

---

## Requirements

- Python 3.8+
- The following Python packages:

```bash
pip install requests beautifulsoup4 python-dotenv
```

- A browser extension to export cookies in Netscape format, such as **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)** (Chrome / Firefox)
- A Discord server where you have permission to create a webhook

---

## Setup

### 1. Export Your Amazon Cookies

1. Install the **Get cookies.txt LOCALLY** browser extension
2. Log into your Amazon account ([amazon.co.uk](https://www.amazon.co.uk) or [amazon.com](https://www.amazon.com))
3. Click the extension and export cookies for the Amazon domain
4. Save the file as `amazon_cookies.txt` in the same directory as the script

> **Note:** Cookies will eventually expire (typically within a few weeks to months). When they do, the script will notify you via Discord and you'll need to re-export them.

### 2. Create a Discord Webhook

1. Open Discord and go to the channel you want notifications in
2. Click **Edit Channel → Integrations → Webhooks → New Webhook**
3. Copy the webhook URL — it will look like:
   `https://discord.com/api/webhooks/123456789/abcdefghij...`

### 3. Configure the Script

Copy the example environment file and fill in your webhook URL:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder with your real webhook URL:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

If you'd also like to use `amazon.com` instead of `amazon.co.uk`, or change the cookie file path, edit the config block near the top of `prime_check.py`:

```python
COOKIE_FILE = "amazon_cookies.txt"        # Path to your exported cookies
AMAZON_BASE = "https://www.amazon.co.uk"  # Or https://www.amazon.com
```

### 4. Run It

```bash
python prime_check.py
```

---

## Scheduling (Recommended: Weekly)

Running the script once a week is enough to stay informed without excessive requests to Amazon.

### macOS / Linux — cron

Open your crontab with `crontab -e` and add:

```cron
# Run every Monday at 09:00
0 9 * * 1 /usr/bin/python3 /path/to/prime_check.py >> /path/to/prime_check.log 2>&1
```

### Windows — Task Scheduler

1. Open **Task Scheduler** and click *Create Basic Task*
2. Set the trigger to **Weekly** on your preferred day
3. Set the action to **Start a Program**:
   - Program: `python`
   - Arguments: `C:\path\to\prime_check.py`
   - Start in: `C:\path\to\script\directory`

---

## Project Structure

```
amazon-prime-checker/
├── prime_check.py        # Main script
├── amazon_cookies.txt    # Your exported cookies (DO NOT commit this)
├── .env                  # Your secrets — webhook URL (DO NOT commit this)
├── .env.example          # Template to copy for new setups
├── .gitignore
└── README.md
```

---

## .gitignore

Make sure you never accidentally commit your cookies or secrets:

```gitignore
amazon_cookies.txt
.env
*.log
__pycache__/
*.pyc
```

---

## Limitations & Caveats

- **No public API** — Amazon does not expose Prime status via any consumer-facing API, so cookie-based scraping is the only option.
- **Cookies expire** — you'll need to re-export them periodically. The script will alert you in Discord when this happens.
- **Page layout changes** — if Amazon redesigns the membership page, the keyword matching may stop working. In this case, the script will print a warning to the console but won't send a Discord notification. Open a GitHub issue if this happens.
- **Amazon ToS** — this script replicates what you would do manually in a browser. Keep usage light (weekly checks) to avoid any issues.

---

## Notification Examples

| Situation | Discord Colour | Sent? |
|---|---|---|
| Prime is active | 🟢 Green | ✅ Yes |
| Cookies expired / HTTP error | 🔴 Red | ✅ Yes |
| Prime is not active | — | ❌ No |
| Page layout unrecognised | — | ❌ No (console warning only) |

---

## License

MIT — do whatever you like with it.