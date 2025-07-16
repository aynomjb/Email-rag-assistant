import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
print("📂 Project root added to path:", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from helpers.query_by_thread import ask_email_agent3

from helpers.credits import init_credits, show_credit_sidebar, use_credit


init_credits()
show_credit_sidebar()
st.set_page_config(page_title="🤖 Query Assistant", layout="wide")


st.title("🤖 Email Query Assistant")
query = st.text_input("Ask a question:", placeholder="e.g., Who was invited to the kickoff meeting?")
top_k = st.slider("Number of documents to retrieve:", 1, 20, 5)

if st.button("Run Query") and query:
    with st.spinner("Processing..."):
        response, docs = ask_email_agent3(query, "emails4", top_k=top_k)

        st.subheader("🤖 Response")
        st.markdown(response)

        with st.expander("📄 Retrieved Context"):
            for i, doc in enumerate(docs):
                st.markdown(f"**Document {i+1}:**\n\n{doc.page_content[:800]}...")
