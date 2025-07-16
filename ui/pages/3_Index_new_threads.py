import streamlit as st
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from helpers.credits import init_credits, show_credit_sidebar, use_credit


init_credits()
show_credit_sidebar()
st.set_page_config(page_title="📥 Index New Emails", layout="wide")
st.title("📥 Index New Email Text Files")

# Setup embedding + Chroma
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Adjust path if needed (make sure it's project-root-relative)
chroma_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../chroma_email_db_3"))
vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embedding_model)

# File uploader
uploaded_files = st.file_uploader("Upload one or more .txt files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    documents = []
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        metadata = {"source": file.name}

        # Preview file
        with st.expander(f"📄 Preview: {file.name}", expanded=False):
            st.text(content[:1500] + ("..." if len(content) > 1500 else ""))

        documents.append(Document(page_content=content, metadata=metadata))

    if st.button("📌 Index Files"):
        vectorstore.add_documents(documents)
        vectorstore.persist()
        st.success(f"✅ Indexed {len(documents)} document(s) successfully!")
