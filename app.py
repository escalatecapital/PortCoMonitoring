import streamlit as st
from supabase import create_client

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("📡 Company Monitoring Dashboard")

st.header("🛠️ Manage Companies")

def load_companies():
    data = supabase.table("companies").select("*").execute().data
    company_map = {}
    for row in data:
        company_map.setdefault(row["name"], {})[row["section"]] = row["url"]
    return company_map

def save_company(name, section_map):
    supabase.table("companies").delete().eq("name", name).execute()
    for section, url in section_map.items():
        supabase.table("companies").insert({
            "name": name,
            "section": section,
            "url": url
        }).execute()

companies = load_companies()

with st.form("Add Company"):
    st.subheader("Add or Update a Company")
    name = st.text_input("Company Name")
    blog = st.text_input("Blog/News URL")
    team = st.text_input("Team/About URL")
    products = st.text_input("Products/Services URL")
    if st.form_submit_button("Save Company"):
        save_company(name, {"blog": blog, "team": team, "products": products})
        st.success(f"Saved {name}!")

st.subheader("Companies Being Monitored")
for company, sections in companies.items():
    st.write(f"### {company}")
    for section, url in sections.items():
        st.write(f"- **{section}**: {url}")

st.header("📬 Subscriber List")

def load_subscribers():
    return [row["email"] for row in supabase.table("subscribers").select("*").execute().data]

def add_subscriber(email):
    supabase.table("subscribers").insert({"email": email}).execute()

def remove_subscriber(email):
    supabase.table("subscribers").delete().eq("email", email).execute()

subscribers = load_subscribers()
new_email = st.text_input("Add subscriber email")
if st.button("Add Subscriber"):
    if new_email not in subscribers:
        add_subscriber(new_email)
        st.success(f"Added {new_email}")

st.write("### Current Subscribers")
for email in subscribers:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(email)
    with col2:
        if st.button("Remove", key=email):
            remove_subscriber(email)
            st.success(f"Removed {email}")
