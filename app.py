import streamlit as st
import json
from datetime import date
import os
import plotly.express as px

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def save_entry(entry_date, content, category):
    entry = {"date": entry_date, "content": content, "category": category}
    with open(f"{DATA_DIR}/{entry_date}.json", "w") as f:
        json.dump(entry, f)

def load_entry(entry_date):
    path = f"{DATA_DIR}/{entry_date}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def delete_entry(entry_date):
    path = f"{DATA_DIR}/{entry_date}.json"
    if os.path.exists(path):
        os.remove(path)

def load_all_entries():
    entries = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(f"{DATA_DIR}/{filename}", "r") as f:
                entries.append(json.load(f))
    return sorted(entries, key=lambda x: x["date"], reverse=True)

st.set_page_config(page_title="Daily Entry App", layout="centered")
st.sidebar.title("📘 Daily Entry App")

# Handle edit redirect from session state
if "edit_date" in st.session_state:
    page = "➕ New Entry"
    editing_date = st.session_state.pop("edit_date")
else:
    page = st.sidebar.radio("Go to", ["➕ New Entry", "📂 View Entries", "📊 Visualizations"])
    editing_date = None

# 1. New Entry Page
if page == "➕ New Entry":
    st.header("New Daily Entry")

    entry_date_value = editing_date if editing_date else date.today().isoformat()
    entry_date = st.date_input("Date", date.fromisoformat(entry_date_value)).isoformat()

    existing = load_entry(entry_date)
    content = st.text_area("What's on your mind?", value=existing["content"] if existing else "", height=200)
    category = st.selectbox("Category", ["Work", "Personal", "Health", "Learning", "Other"],
                            index=["Work", "Personal", "Health", "Learning", "Other"].index(existing["category"]) if existing else 0)

    if st.button("💾 Save Entry"):
        save_entry(entry_date, content, category)
        st.success("Entry saved successfully!")

# 2. View Entries Page
elif page == "📂 View Entries":
    st.header("All Entries")
    entries = load_all_entries()

    if not entries:
        st.info("No entries found.")
    else:
        for entry in entries:
            with st.expander(f"{entry['date']} - {entry['category']}"):
                st.write(entry["content"])
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"📝 Edit {entry['date']}", key="edit" + entry["date"]):
                        st.session_state.edit_date = entry["date"]
                        st.rerun()
                with col2:
                    if st.button(f"🗑 Delete {entry['date']}", key="delete" + entry["date"]):
                        delete_entry(entry["date"])
                        st.warning("Entry deleted.")
                        st.rerun()

# 3. Visualization Page
elif page == "📊 Visualizations":
    st.header("Entry Overview")
    entries = load_all_entries()

    if not entries:
        st.info("No data to visualize.")
    else:
        category_counts = {}
        for entry in entries:
            category = entry["category"]
            category_counts[category] = category_counts.get(category, 0) + 1

        fig = px.pie(
            names=list(category_counts.keys()),
            values=list(category_counts.values()),
            title="Entries by Category"
        )
        st.plotly_chart(fig)
