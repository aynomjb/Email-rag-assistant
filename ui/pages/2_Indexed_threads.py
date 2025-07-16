import streamlit as st
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

st.set_page_config(page_title="📄 Email List & Preview", layout="wide")

# Load vectorstore and documents
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="chroma_email_db_3", embedding_function=embedding_model)
print("🔍 Total documents in Chroma DB:", vectorstore._collection.count())

docs = vectorstore.similarity_search(" ", k=1000)

# Safely extract metadata
meta = []
for i, doc in enumerate(docs):
    metadata = doc.metadata
    subject = metadata.get("subject", "No Subject")
    sender = metadata.get("from", "Unknown")
    raw_date = metadata.get("date", "1970-01-01")
    try:
        date_parsed = pd.to_datetime(raw_date)
    except Exception:
        date_parsed = pd.to_datetime("1970-01-01")

    meta.append({
        "index": i,
        "subject": subject,
        "from": sender,
        "date": raw_date,
        "date_parsed": date_parsed
    })

df = pd.DataFrame(meta)

# Filters
st.sidebar.title("📂 Filters")
if df.empty:
    st.error("❌ No documents found in Chroma DB.")
    st.stop()
df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
df["date_parsed"].fillna(pd.to_datetime("1970-01-01"), inplace=True)
min_date = df["date_parsed"].min()
max_date = df["date_parsed"].max()

date_range = st.sidebar.date_input("📅 Date Range", (min_date, max_date))
senders = df["from"].unique().tolist()
selected_senders = st.sidebar.multiselect("✉️ Sender", senders, default=senders)

# Filter based on date and sender
filtered_df = df[
    (df["from"].isin(selected_senders)) &
    (df["date_parsed"] >= pd.to_datetime(date_range[0])) &
    (df["date_parsed"] <= pd.to_datetime(date_range[1]))
]

# Render list labels
doc_labels = [
    f"{row['subject']} | {row['date_parsed'].date()} | {row['from']}"
    for _, row in filtered_df.iterrows()
]

# Sidebar selection
index_options = filtered_df["index"].tolist()
if index_options:
    selected_index = st.sidebar.radio(
        "Select an email:",
        options=index_options,
        format_func=lambda i: doc_labels[filtered_df.index.get_loc(i)]
    )

    # Preview
    selected_doc = docs[selected_index]
    st.subheader("📄 Email Preview")
    st.markdown(f"**Subject:** {selected_doc.metadata.get('subject', 'No Subject')}")
    st.markdown(f"**From:** {selected_doc.metadata.get('from', 'Unknown')}")
    st.markdown(f"**To:** {selected_doc.metadata.get('to', 'Unknown')}")
    st.markdown(f"**Date:** {selected_doc.metadata.get('date', 'Unknown')}")
    st.text_area("Content", selected_doc.page_content[:2000], height=300)
else:
    st.info("No emails match the selected filters.")
