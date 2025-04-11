import streamlit as st
import requests
from supabase import create_client
from glassdoor_scraper import get_glassdoor_data
from glassdoor_wayback import get_historical_rating

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
    glassdoor = st.text_input("Glassdoor URL")
    if st.form_submit_button("Save Company"):
        save_company(name, {
            "blog": blog,
            "team": team,
            "products": products,
            "glassdoor": glassdoor
        })
        st.success(f"Saved {name}!")

st.title("📊 Company Monitoring Dashboard")

def load_companies():
    data = supabase.table("companies").select("*").execute().data
    company_map = {}
    for row in data:
        company_map.setdefault(row["name"], {})[row["section"]] = row["url"]
    return company_map

companies = load_companies()

glassdoor_rows = []

st.header("🔎 Glassdoor Insights")

for company, sections in companies.items():
    if "glassdoor" in sections:
        current_rating = "N/A"
        past_rating = "N/A"
        delta = "N/A"
        recent_review = "No recent review"

        try:
            current_rating, reviews = get_glassdoor_data(sections["glassdoor"])
            current_rating = float(current_rating)
        except:
            pass

        try:
            past_rating_text, _ = get_historical_rating(sections["glassdoor"])
            if past_rating_text:
                past_rating = float(past_rating_text)
        except:
            pass

        if isinstance(current_rating, float) and isinstance(past_rating, float):
            delta = round(current_rating - past_rating, 2)

        if reviews:
            top_review = reviews[0]
            recent_review = f"{top_review['title']} — {top_review['snippet']}"

        glassdoor_rows.append({
            "Company": company,
            "Current Rating": current_rating,
            "Rating 12mo Ago": past_rating,
            "Change": delta,
            "Most Recent Review": recent_review
        })

if glassdoor_rows:
    import pandas as pd
    df = pd.DataFrame(glassdoor_rows)
    st.dataframe(df)
else:
    st.info("No Glassdoor data available yet.")

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
