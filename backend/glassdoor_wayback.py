import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_historical_rating(glassdoor_url):
    # Get the date 12 months ago
    target_date = (datetime.utcnow() - timedelta(days=365)).strftime("%Y%m%d")

    wayback_api = f"https://archive.org/wayback/available?url={glassdoor_url}&timestamp={target_date}"
    try:
        response = requests.get(wayback_api, timeout=10)
        data = response.json()

        if "archived_snapshots" not in data or "closest" not in data["archived_snapshots"]:
            print("⚠️ No Wayback snapshot found for this date.")
            return None, None

        snapshot_url = data["archived_snapshots"]["closest"]["url"]

        snapshot_resp = requests.get(snapshot_url, timeout=10)
        soup = BeautifulSoup(snapshot_resp.text, "html.parser")

        # Attempt to extract rating from the snapshot
        rating_element = soup.find("span", {"data-test": "rating"})
        if rating_element:
            return rating_element.text.strip(), snapshot_url
        else:
            # Fallback: look for plain text star rating
            text = soup.get_text()
            for line in text.splitlines():
                if "stars" in line.lower() and any(c.isdigit() for c in line):
                    return line.strip(), snapshot_url
            return None, snapshot_url
    except Exception as e:
        print(f"❌ Error retrieving historical rating: {e}")
        return None, None
