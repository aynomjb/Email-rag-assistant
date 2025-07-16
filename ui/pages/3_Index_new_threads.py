import streamlit as st
import os
import sys
import time
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from helpers.credits import init_credits, show_credit_sidebar, use_credit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
print("📂 Project root added to path:", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from helpers.indexer_by_thread import index_email_uploaded

init_credits()
show_credit_sidebar()
st.set_page_config(page_title="📥 Index New Emails", layout="wide")
st.title("📥 Index New Email Text Files")


# File uploader
uploaded_files = st.file_uploader("Upload one or more .txt files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    documents = []
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        # print(content)
        metadata = {"source": file.name}

        # Preview file
        with st.expander(f"📄 Preview: {file.name}", expanded=False):
            st.text(content[:1500] + ("..." if len(content) > 1500 else ""))

        documents.append(Document(page_content=content, metadata=metadata))

    st.subheader("🧵 Thread Info")
    thread_name = st.text_input("Enter a thread name for these emails (required):")

    if st.button("📌 Index Files"):
        if not thread_name.strip():
            st.error("Please enter a thread name before indexing.")
        else:
            index_email_uploaded(uploaded_files,thread_name)
            # vectorstore.add_documents(documents)
            # vectorstore.persist()
            st.success(f"✅ Indexed {len(documents)} document(s) successfully!")
