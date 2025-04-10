import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os

CONFIG_FILE = "company_config.json"
HASHES_FILE = "hashes.json"

def fetch_and_hash(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]): tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        normalized_text = ' '.join(text.split())
        page_hash = hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
        return page_hash, normalized_text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def monitor_company(company_name, config, previous_hashes):
    changes = []
    for section, url in config.items():
        print(f"Checking {company_name} - {section} @ {url}")
        new_hash, _ = fetch_and_hash(url)
        if not new_hash:
            continue
        key = f"{company_name}:{section}"
        old_hash = previous_hashes.get(key)
        if old_hash != new_hash:
            print(f"🔔 Change detected in {company_name} - {section}")
            changes.append((section, url))
            previous_hashes[key] = new_hash
    return changes

def monitor_all():
    company_config = load_json(CONFIG_FILE)
    previous_hashes = load_json(HASHES_FILE)
    summary = {}

    for company, config in company_config.items():
        changes = monitor_company(company, config, previous_hashes)
        if changes:
            summary[company] = changes

    save_json(previous_hashes, HASHES_FILE)
    return summary

if __name__ == "__main__":
    updates = monitor_all()
    if updates:
        print("\n=== Summary of Detected Changes ===")
        for company, changes in updates.items():
            print(f"\nCompany: {company}")
            for section, url in changes:
                print(f" - Changed: {section} @ {url}")
    else:
        print("✅ No changes detected.")