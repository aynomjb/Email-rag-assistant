import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from helpers.query_by_thread import ask_email_agent3

st.set_page_config(page_title="🤖 Query Assistant", layout="wide")


st.title("🤖 Email Query Assistant")
# Load vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="chroma_email_db_3", embedding_function=embedding_model)

# Load all docs just for thread list (won't affect retrieval later)
all_docs = vectorstore.similarity_search(" ", k=1000)
all_threads = sorted(list(set(doc.metadata.get("thread", "Unknown") for doc in all_docs)))
if not all_threads:
    st.info("No mail threads indexed yet")
    st.markdown(
    """
    <a href="/Index_new_threads" target="_self">
        <button style='padding:10px 20px; background-color:#4CAF50; color:white; border:none; border-radius:8px; font-size:16px; cursor:pointer;'>
            📂 Index New Mails
        </button>
    </a>
    """,
    unsafe_allow_html=True
)
    st.stop()

st.subheader("📂 Query Scope")
thread_options = ["All Threads"] + all_threads
selected_thread = st.selectbox("🔍 Select thread to query", options=thread_options)
query = st.text_input("Ask a question:", placeholder="e.g., Who was invited to the kickoff meeting?")
top_k = st.slider("Number of documents to retrieve:", 1, 20, 5)

if st.button("Run Query") and query:
    with st.spinner("Processing..."):
        print(selected_thread)
        response, docs = ask_email_agent3(query, selected_thread, top_k=top_k)

        st.subheader("🤖 Response")
        st.markdown(response)

        with st.expander("📄 Retrieved Context"):
            for i, doc in enumerate(docs):
                st.markdown(f"**Document {i+1}:**\n\n{doc.page_content[:800]}...")
