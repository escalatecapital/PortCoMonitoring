import os
import json
import streamlit as st

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "company_config.json")
SUBSCRIBERS_FILE = os.path.join(BASE_DIR, "subscribers.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --- Company Config Management ---
st.title("📡 Company Monitoring Config Tool")

config = load_json(CONFIG_FILE, {})

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
        save_json(config, CONFIG_FILE)
        st.success(f"✅ Saved config for {company_name}")

st.subheader("🗑️ Remove Company From Monitoring")
if config:
    company_to_remove = st.selectbox("Select a company to remove", [""] + list(config.keys()))
    if st.button("Remove Selected Company") and company_to_remove:
        del config[company_to_remove]
        save_json(config, CONFIG_FILE)
        st.success(f"🗑️ Removed {company_to_remove} from configuration.")
else:
    st.info("No companies configured yet.")

st.subheader("📘 Current Companies Being Monitored")
if config:
    for company, urls in config.items():
        st.write(f"### {company}")
        for section, url in urls.items():
            st.write(f"- **{section}**: {url}")
else:
    st.info("No companies configured.")

# --- Subscriber Management ---
st.title("📬 Subscriber Management")

subscribers = load_json(SUBSCRIBERS_FILE, [])

new_email = st.text_input("Enter email to subscribe")
if st.button("Add Subscriber") and new_email:
    if new_email not in subscribers:
        subscribers.append(new_email)
        save_json(subscribers, SUBSCRIBERS_FILE)
        st.success(f"✅ Added {new_email} to subscribers.")
    else:
        st.warning("This email is already subscribed.")

if subscribers:
    st.write("### Current Subscribers")
    for i, email in enumerate(subscribers):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(email)
        with col2:
            if st.button(f"Remove", key=f"remove_{i}"):
                subscribers.pop(i)
                save_json(subscribers, SUBSCRIBERS_FILE)
                st.success(f"Removed {email}")
else:
    st.info("No subscribers yet.")
