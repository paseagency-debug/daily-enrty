import streamlit as st
import os
import json
from datetime import date
import plotly.express as px
from collections import Counter

# --- Config ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- Helper Functions ---
def get_entry_path(entry_date):
    return os.path.join(DATA_DIR, f"{entry_date}.json")

def save_entry(entry):
    with open(get_entry_path(entry["date"]), "w") as f:
        json.dump(entry, f, indent=4)

def load_entry(entry_date):
    try:
        with open(get_entry_path(entry_date), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def delete_entry(entry_date):
    try:
        os.remove(get_entry_path(entry_date))
    except FileNotFoundError:
        pass

def load_all_entries():
    entries = []
    for filename in sorted(os.listdir(DATA_DIR), reverse=True):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename)) as f:
                entries.append(json.load(f))
    return entries

# --- UI: Sidebar Navigation ---
st.sidebar.title("📘 Daily Entry App")
page = st.sidebar.radio("Go to", ["➕ New Entry", "📂 View Entries", "📊 Visualizations"])

# --- Page: New Entry ---
if page == "➕ New Entry":
    st.title("➕ Create or Update Entry")

    today = date.today().isoformat()
    entry_date = st.date_input("Date", date.fromisoformat(today)).isoformat()

    existing = load_entry(entry_date)
    if existing:
        st.info("An entry already exists for this date. Editing it.")
        default_title = existing["title"]
        default_content = existing["content"]
        default_mood = existing["mood"]
        default_tags = existing["tags"]
    else:
        default_title = ""
        default_content = ""
        default_mood = "😊"
        default_tags = ""

    title = st.text_input("Title", default_title)
    content = st.text_area("Detailed Entry", default_content, height=200)
    mood = st.selectbox("Mood", ["😊", "😐", "😔", "😡", "😄", "😭"], index=["😊", "😐", "😔", "😡", "😄", "😭"].index(default_mood))
    tags = st.text_input("Tags (comma-separated)", default_tags)
    uploaded_files = st.file_uploader("Upload files (optional)", accept_multiple_files=True)

    if st.button("💾 Save Entry"):
        file_names = []
        upload_dir = os.path.join(DATA_DIR, entry_date + "_files")
        os.makedirs(upload_dir, exist_ok=True)
        for uploaded_file in uploaded_files:
            filepath = os.path.join(upload_dir, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_names.append(uploaded_file.name)

        entry = {
            "date": entry_date,
            "title": title,
            "content": content,
            "mood": mood,
            "tags": tags,
            "files": file_names
        }
        save_entry(entry)
        st.success("Entry saved successfully!")

# --- Page: View Entries ---
elif page == "📂 View Entries":
    st.title("📂 Past Entries")
    entries = load_all_entries()

    search = st.text_input("🔍 Search by keyword (title/content/tags)")
    filter_mood = st.selectbox("🎭 Filter by Mood", ["All"] + ["😊", "😐", "😔", "😡", "😄", "😭"])
    
    if search:
        entries = [e for e in entries if search.lower() in e["title"].lower() or search.lower() in e["content"].lower() or search.lower() in e["tags"].lower()]
    if filter_mood != "All":
        entries = [e for e in entries if e["mood"] == filter_mood]

    for entry in entries:
        with st.expander(f"{entry['date']} — {entry['title']} {entry['mood']}"):
            st.write(entry["content"])
            st.markdown(f"**Tags:** `{entry['tags']}`")
            if entry.get("files"):
                st.markdown("**Attached Files:**")
                for file in entry["files"]:
                    st.markdown(f"- {file}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"📝 Edit {entry['date']}", key="edit"+entry["date"]):
                    st.experimental_set_query_params(page="edit", date=entry["date"])
                    st.rerun()
            with col2:
                if st.button(f"🗑️ Delete {entry['date']}", key="delete"+entry["date"]):
                    delete_entry(entry["date"])
                    st.warning(f"Deleted entry for {entry['date']}")
                    st.rerun()

# --- Page: Visualization ---
elif page == "📊 Visualizations":
    st.title("📊 Data Visualizations")
    entries = load_all_entries()

    if not entries:
        st.info("No data to visualize yet.")
    else:
        # --- Mood Pie Chart ---
        mood_counts = Counter([e["mood"] for e in entries])
        mood_fig = px.pie(
            names=list(mood_counts.keys()),
            values=list(mood_counts.values()),
            title="Mood Distribution"
        )
        st.plotly_chart(mood_fig)

        # --- Tag Pie Chart ---
        all_tags = []
        for e in entries:
            all_tags.extend([t.strip().lower() for t in e["tags"].split(",") if t.strip()])
        tag_counts = Counter(all_tags)
        if tag_counts:
            tag_fig = px.pie(
                names=list(tag_counts.keys()),
                values=list(tag_counts.values()),
                title="Tag Frequency"
            )
            st.plotly_chart(tag_fig)
