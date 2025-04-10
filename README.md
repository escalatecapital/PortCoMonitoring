# PortCoMonitoring

🕵️‍♂️ Company Monitor Tool
Track changes to company websites, including team pages, blog posts, and product offerings — and easily manage monitored companies through a web UI.

🔧 Features
Monitor any company's key pages (team, blog/news, products)

Detect specific changes:

New blog articles (with links)

Team member additions/removals (by name/title)

Text differences in product/services pages

Simple web UI (via Streamlit) for adding/removing companies

Fully local and free-tier compatible (no paid APIs needed)

📁 Project Structure
bash
Copy
Edit
company-monitor/
│
├── app.py                # Streamlit UI for managing company config
├── monitor.py            # Script to detect and report changes
├── company_config.json   # Configuration file with company URLs
├── page_data.json        # Stores previous page snapshots
├── README.md             # You're here!
🚀 Getting Started
1. Clone the repo
bash
Copy
Edit
git clone https://github.com/your-username/company-monitor.git
cd company-monitor
2. Install dependencies
We recommend using a virtual environment.

bash
Copy
Edit
pip install -r requirements.txt
Or manually install:

bash
Copy
Edit
pip install streamlit beautifulsoup4 requests
3. Run the Streamlit UI
bash
Copy
Edit
streamlit run app.py
This launches a web app where your team can:

Add/update company URLs

Remove companies from the monitoring list

4. Run the Monitor Script
bash
Copy
Edit
python monitor.py
This will:

Fetch each configured URL

Detect changes since the last run

Print new blog articles, team changes, or page diffs to the console

🧪 Example Output
css
Copy
Edit
🔍 Checking acme_corp - blog @ https://acme.com/news
📰 New articles found:
 - https://acme.com/news/ai-announcement

🔍 Checking acme_corp - team @ https://acme.com/team
👥 Team page changes:
➖ Removed:
   - Jane Doe – VP of Marketing
➕ Added:
   - John Smith – Director of Sales

🔍 Checking acme_corp - products @ https://acme.com/products
🛠️ Products page changed:
- Old feature description
+ New feature added!
📌 Configuration Format
Example company_config.json:

json
Copy
Edit
{
  "acme_corp": {
    "blog": "https://acme.com/news",
    "team": "https://acme.com/about/team",
    "products": "https://acme.com/products"
  }
}
📬 Future Additions (Ideas)
Email notifications when changes are detected

Dashboard with change history

More robust entity extraction (e.g., actual names, titles, blog titles)

Database or cloud support for scale

🛡️ Disclaimer
This tool uses basic HTML scraping. Ensure your usage complies with the target websites' Terms of Service. For production use, consider APIs or serverless infrastructure.
