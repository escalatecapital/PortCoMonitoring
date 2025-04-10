import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import difflib

# File paths
CONFIG_FILE = "company_config.json"
DATA_FILE = "page_data.json"

def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]): tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def diff_lines(old, new):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
    return diff

def extract_links(text):
    soup = BeautifulSoup(text, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def extract_people(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return set(line for line in lines if any(role in line.lower() for role in [
        "ceo", "cto", "cro", "cfo", "svp", "chief", "vp", "president", "director", "lead", "head", "officer","sales","product","business development","partnerships","finance","accounting","controller"
    ]))

def monitor_all():
    if not os.path.exists(CONFIG_FILE):
        print("❌ No company_config.json file found.")
        return

    config = load_config()
    previous_data = load_data()
    results = {}

    for company, sections in config.items():
        results[company] = []
        for section, url in sections.items():
            print(f"🔍 Checking {company} - {section} @ {url}")
            new_text = fetch_page_text(url)
            if not new_text:
                continue

            key = f"{company}:{section}"
            old_text = previous_data.get(key, "")

            if new_text != old_text:
                if section == "blog":
                    new_soup = BeautifulSoup(new_text, 'html.parser')
                    old_soup = BeautifulSoup(old_text, 'html.parser')
                    new_links = set(a['href'] for a in new_soup.find_all('a', href=True))
                    old_links = set(a['href'] for a in old_soup.find_all('a', href=True))
                    new_articles = new_links - old_links
                    print("📰 New articles found:")
                    for link in new_articles:
                        print(f" - {link}")

                elif section == "team":
                    new_people = extract_people(new_text)
                    old_people = extract_people(old_text)
                    added = new_people - old_people
                    removed = old_people - new_people
                    print("👥 Team page changes:")
                    if added:
                        print("➕ Added:")
                        for person in added:
                            print(f"   - {person}")
                    if removed:
                        print("➖ Removed:")
                        for person in removed:
                            print(f"   - {person}")

                elif section == "products":
                    diff = diff_lines(old_text, new_text)
                    print("🛠️ Products page changed:")
                    for line in diff:
                        print(line)

                # Save new text to storage
                previous_data[key] = new_text

    save_data(previous_data)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    monitor_all()
