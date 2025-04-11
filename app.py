import streamlit as st
import pandas as pd
from supabase import create_client

# Step 1: Load Supabase secrets
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    st.success("✅ Supabase secrets loaded successfully.")
except Exception as e:
    st.error(f"❌ Could not load Supabase secrets: {e}")
    st.stop()

# Step 2: Connect to Supabase
try:
    supabase = create_client(url, key)
    st.success("✅ Connected to Supabase.")
except Exception as e:
    st.error(f"❌ Failed to initialize Supabase client: {e}")
    st.stop()

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

# Step 3: Query Glassdoor insights
st.header("🔎 Glassdoor Insights")

try:
    with st.spinner("📡 Querying glassdoor_insights from Supabase..."):
        response = supabase.table("glassdoor_insights").select("*").execute()
        data = response.data
    st.success("✅ Data retrieved successfully.")
except Exception as e:
    st.error(f"❌ Error retrieving data from Supabase: {e}")
    st.stop()

# Step 4: Display results
if data:
    try:
        df = pd.DataFrame(data)
        df = df.rename(columns={
            "company": "Company",
            "current_rating": "Current Rating",
            "past_rating": "Rating 12mo Ago",
            "rating_delta": "Change",
            "review_title": "Review Title",
            "review_snippet": "Review Snippet"
        })
        st.dataframe(df[["Company", "Current Rating", "Rating 12mo Ago", "Change", "Review Title", "Review Snippet"]])
    except Exception as e:
        st.error(f"⚠️ Error formatting or displaying data: {e}")
else:
    st.info("ℹ️ No Glassdoor data available yet. Try running the monitor.")
    
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
