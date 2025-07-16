import streamlit as st

import os
from helpers.credits import init_credits, show_credit_sidebar, use_credit


init_credits()
show_credit_sidebar()
st.write("Working directory:", os.getcwd())

st.set_page_config(page_title="📬 Email RAG System", layout="wide")

st.title("📬 Email Query System")
st.markdown("Navigate using the sidebar or click below:")

# Custom CSS for clickable cards
st.markdown("""
<style>
.option-box {
    border: 2px solid #d3d3d3;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: box-shadow 0.3s ease-in-out;
    background-color: #f9f9f9;
}
.option-box:hover {
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.15);
}
a {
    text-decoration: none;
    color: inherit;
}
</style>
""", unsafe_allow_html=True)

# Three columns for layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="option-box">'
        '💬<br><a href="/Query_assistant" target="_self"><b>Query Assistant</b></a>'
        '</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<div class="option-box">'
        '📁<br><a href="/Indexed_threads" target="_self"><b>Indexed Documents</b></a>'
        '</div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        '<div class="option-box">'
        '🗂️<br><a href="/Index_new_threads" target="_self"><b>Index New Emails</b></a>'
        '</div>',
        unsafe_allow_html=True
    )
