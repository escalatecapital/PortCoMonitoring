import streamlit as st
import json
import os

CONFIG_FILE = "company_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

st.title("📡 Company Monitoring Config Tool")

config = load_config()

# Add or update company
with st.form("Add/Update Company"):
    st.subheader("Add or Update Company Configuration")
    company_name = st.text_input("Company Name (e.g., acme_corp)")
    blog_url = st.text_input("Blog/News/Press URL")
    team_url = st.text_input("Team/About URL")
    product_url = st.text_input("Products/Services URL")

    submitted = st.form_submit_button("Save Company")
    if submitted and company_name:
        config[company_name] = {
            "blog": blog_url,
            "team": team_url,
            "products": product_url
        }
        save_config(config)
        st.success(f"✅ Saved config for {company_name}")

# Display current config
st.subheader("📘 Current Companies Being Monitored")
if config:
    for company, urls in config.items():
        st.write(f"### {company}")
        for section, url in urls.items():
            st.write(f"- **{section}**: {url}")
else:
    st.info("No companies configured yet.")