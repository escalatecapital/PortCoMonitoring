import difflib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import os
from datetime import datetime
from supabase import create_client
from .glassdoor_scraper import get_glassdoor_data
from .glassdoor_wayback import get_historical_rating

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_page_text(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            return "403 Forbidden"
        elif response.status_code != 200:
            return f"Error {response.status_code}"
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]): tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return None

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
            server.sendmail(msg["From"], recipients, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor():
    changes = []

    companies = supabase.table("companies").select("*").execute().data
    subscribers = [row["email"] for row in supabase.table("subscribers").select("*").execute().data]

    for company in set(row["name"] for row in companies):
        sections = {row["section"]: row["url"] for row in companies if row["name"] == company}
        for section, url in sections.items():
            key = f"{company}:{section}"

            if section == "glassdoor":
                try:
                    rating, reviews = get_glassdoor_data(url)
                    past_rating, _ = get_historical_rating(url)

                    current = float(rating) if rating and rating.replace(".", "", 1).isdigit() else None
                    past = float(past_rating) if past_rating and past_rating.replace(".", "", 1).isdigit() else None
                    delta = round(current - past, 2) if current is not None and past is not None else None
                    top_review = reviews[0] if reviews else {"title": None, "snippet": None}

                    supabase.table("glassdoor_insights").upsert({
                        "company": company,
                        "current_rating": current,
                        "past_rating": past,
                        "rating_delta": delta,
                        "review_title": top_review["title"],
                        "review_snippet": top_review["snippet"],
                        "updated_at": datetime.utcnow().isoformat()
                    }, on_conflict=["company"]).execute()

                    summary = f"⭐ Glassdoor for {company}: {current}"
                    if past:
                        summary += f" (↓ from {past} a year ago)"
                    if top_review["title"]:
                        summary += f"\n📝 {top_review['title']} — {top_review['snippet']}"
                    changes.append(summary)
                except Exception as e:
                    changes.append(f"⚠️ Could not retrieve Glassdoor data for {company}: {str(e)}")
                continue

            new_text = fetch_page_text(url)
            row_key = {"company": company, "section": section}
            stored = supabase.table("snapshots").select("content").match(row_key).execute().data
            old_text = stored[0]["content"] if stored else ""

            if new_text and new_text != old_text:
                summary = f"🛎️ Change in {company} - {section} ({url})"
                if section == "team":
                    old_people = extract_people(old_text)
                    new_people = extract_people(new_text)
                    added = new_people - old_people
                    removed = old_people - new_people
                    if added:
                        summary += f"\n👥 Added: {', '.join(added)}"
                    if removed:
                        summary += f"\n👥 Removed: {', '.join(removed)}"
                elif section == "products":
                    diff = diff_lines(old_text, new_text)
                    summary += "\n🛠️ Product page diff:\n" + "\n".join(diff[:20])
                else:
                    summary += "\n📰 Content changed."
                changes.append(summary)

                if stored:
                    supabase.table("snapshots").update({
                        "content": new_text,
                        "captured_at": datetime.utcnow().isoformat()
                    }).match(row_key).execute()
                else:
                    supabase.table("snapshots").insert({
                        "company": company,
                        "section": section,
                        "content": new_text,
                        "captured_at": datetime.utcnow().isoformat()
                    }).execute()

    if changes and subscribers:
        full_body = "\n\n".join(changes)
        send_email("📡 Company Monitor: Changes Detected", full_body, subscribers)
    elif changes:
        print("Changes detected but no subscribers to notify.")
    else:
        print("✅ No changes detected.")

if __name__ == "__main__":
    monitor()
