import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import difflib
import smtplib
from email.mime.text import MIMEText

# --- File paths ---
CONFIG_FILE = "company_config.json"
DATA_FILE = "page_data.json"
SUBSCRIBERS_FILE = "subscribers.json"

# --- Config ---
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "rdxz ldtm sjva ffyj"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# --- Utility Functions ---
def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]): tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def load_json(path, default={}):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def diff_lines(old, new):
    return list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=''))

def extract_people(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return set(line for line in lines if any(role in line.lower() for role in [
        "ceo", "cto", "chief", "vp", "president", "director", "lead", "head", "officer"
    ]))

def send_email(subject, body, recipients):
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
        print(f"📧 Email sent to: {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- Main Monitoring Logic ---
def monitor_all():
    config = load_json(CONFIG_FILE)
    previous_data = load_json(DATA_FILE)
    subscribers = load_json(SUBSCRIBERS_FILE, [])

    change_summary = []

    for company, sections in config.items():
        for section, url in sections.items():
            print(f"🔍 Checking {company} - {section} @ {url}")
            new_text = fetch_page_text(url)
            if not new_text:
                continue

            key = f"{company}:{section}"
            old_text = previous_data.get(key, "")

            if new_text != old_text:
                summary = f"\n🛎️ Change detected in {company} - {section} ({url})"

                if section == "blog":
                    soup_new = BeautifulSoup(new_text, 'html.parser')
                    soup_old = BeautifulSoup(old_text, 'html.parser')
                    links_new = set(a['href'] for a in soup_new.find_all('a', href=True))
                    links_old = set(a['href'] for a in soup_old.find_all('a', href=True))
                    new_articles = links_new - links_old
                    if new_articles:
                        summary += "\n📰 New articles:\n" + "\n".join(f" - {link}" for link in new_articles)

                elif section == "team":
                    people_new = extract_people(new_text)
                    people_old = extract_people(old_text)
                    added = people_new - people_old
                    removed = people_old - people_new
                    if added:
                        summary += "\n👥 Added team members:\n" + "\n".join(f" + {p}" for p in added)
                    if removed:
                        summary += "\n👥 Removed team members:\n" + "\n".join(f" - {p}" for p in removed)

                elif section == "products":
                    diff = diff_lines(old_text, new_text)
                    summary += "\n🛠️ Product page diff:\n" + "\n".join(diff[:20])  # Limit lines for email

                change_summary.append(summary)
                previous_data[key] = new_text

    save_json(previous_data, DATA_FILE)

    # Send summary if there are changes
    if change_summary and subscribers:
        full_body = "\n\n".join(change_summary)
        send_email("📡 Company Monitor: Changes Detected", full_body, subscribers)
    elif change_summary:
        print("⚠️ Changes found but no subscribers to notify.")
    else:
        print("✅ No changes detected.")

if __name__ == "__main__":
    monitor_all()
