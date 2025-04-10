import difflib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
from supabase import create_client
import os

# Supabase from environment variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]): tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
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
            server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
        print(f"Email sent to: {', '.join(recipients)}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor():
    changes = []
    data_store = {}

    companies = supabase.table("companies").select("*").execute().data
    subscribers = [row["email"] for row in supabase.table("subscribers").select("*").execute().data]

    for company in set(row["name"] for row in companies):
        sections = {row["section"]: row["url"] for row in companies if row["name"] == company}
        for section, url in sections.items():
            key = f"{company}:{section}"
            new_text = fetch_page_text(url)
            row_key = {"company": company, "section": section}
            stored = supabase.table("snapshots").select("content").match(row_key).execute().data
            old_text = stored[0]["content"] if stored else ""

            if new_text and new_text != old_text:
                summary = f"Change in {company} - {section} ({url})"
                if section == "team":
                    old_people = extract_people(old_text)
                    new_people = extract_people(new_text)
                    added = new_people - old_people
                    removed = old_people - new_people
                    summary += f"\n+ {', '.join(added)}\n- {', '.join(removed)}"
                elif section == "products":
                    diff = diff_lines(old_text, new_text)
                    summary += "\n" + "\n".join(diff[:20])
                else:
                    summary += "\nContent changed."

                changes.append(summary)

                if stored:
                    supabase.table("snapshots").update({"content": new_text}).match(row_key).execute()
                else:
                    supabase.table("snapshots").insert({"company": company, "section": section, "content": new_text}).execute()

    if changes and subscribers:
        full_body = "\n\n".join(changes)
        send_email("Company Monitor: Updates Detected", full_body, subscribers)

if __name__ == "__main__":
    monitor()
