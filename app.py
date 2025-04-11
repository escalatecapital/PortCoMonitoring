import streamlit as st
from supabase import create_client
import pandas as pd

st.title("📡 Company Monitoring Dashboard")

# ✅ Load Supabase secrets safely
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("❌ Supabase secrets not configured properly.")
    st.stop()

# ✅ Connect to Supabase
try:
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"❌ Failed to initialize Supabase client: {e}")
    st.stop()

# ✅ Company Configuration Section
st.header("🛠️ Manage Companies")
try:
    with st.spinner("Loading existing company configurations..."):
        data = supabase.table("companies").select("*").execute().data
    company_map = {}
    for row in data:
        company_map.setdefault(row["name"], {})[row["section"]] = row["url"]
except Exception as e:
    st.error(f"❌ Could not load company data: {e}")
    st.stop()

with st.form("Add Company"):
    st.subheader("Add or Update a Company")
    name = st.text_input("Company Name")
    blog = st.text_input("Blog/News URL")
    team = st.text_input("Team/About URL")
    products = st.text_input("Products/Services URL")
    glassdoor = st.text_input("Glassdoor URL")
    if st.form_submit_button("Save Company"):
        try:
            supabase.table("companies").delete().eq("name", name).execute()
            for section, url in {
                "blog": blog,
                "team": team,
                "products": products,
                "glassdoor": glassdoor
            }.items():
                supabase.table("companies").insert({
                    "name": name,
                    "section": section,
                    "url": url
                }).execute()
            st.success(f"✅ Saved config for {name}")
        except Exception as e:
            st.error(f"❌ Failed to save company config: {e}")

st.subheader("📘 Current Companies Being Monitored")
for company, sections in company_map.items():
    st.write(f"### {company}")
    for section, url in sections.items():
        st.write(f"- **{section}**: {url}")

# ✅ Glassdoor Insights Table
st.header("🔎 Glassdoor Insights")
try:
    with st.spinner("Loading Glassdoor insights..."):
        response = supabase.table("glassdoor_insights").select("*").execute()
        insights = response.data
    if insights:
        df = pd.DataFrame(insights)
        df = df.rename(columns={
            "company": "Company",
            "current_rating": "Current Rating",
            "past_rating": "Rating 12mo Ago",
            "rating_delta": "Change",
            "review_title": "Review Title",
            "review_snippet": "Review Snippet"
        })
        st.dataframe(df[["Company", "Current Rating", "Rating 12mo Ago", "Change", "Review Title", "Review Snippet"]])
    else:
        st.info("ℹ️ No Glassdoor data available yet. Try running the monitor.")
except Exception as e:
    st.error(f"❌ Error loading Glassdoor data: {e}")

# ✅ Subscriber Management Section
st.header("📬 Subscriber List")
try:
    subscribers = supabase.table("subscribers").select("*").execute().data
except Exception as e:
    subscribers = []
    st.error(f"❌ Failed to load subscriber list: {e}")

new_email = st.text_input("Add subscriber email")
if st.button("Add Subscriber") and new_email:
    try:
        supabase.table("subscribers").insert({"email": new_email}).execute()
        st.success(f"✅ Added {new_email} to subscribers.")
    except Exception as e:
        st.error(f"❌ Failed to add subscriber: {e}")

st.write("### Current Subscribers")
for email in subscribers:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(email["email"])
    with col2:
        if st.button("Remove", key=email["email"]):
            try:
                supabase.table("subscribers").delete().eq("email", email["email"]).execute()
                st.success(f"Removed {email['email']}")
            except Exception as e:
                st.error(f"❌ Failed to remove {email['email']}: {e}")
