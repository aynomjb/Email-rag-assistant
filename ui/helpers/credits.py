import streamlit as st

DEFAULT_CREDITS = 10

def init_credits():
    if "credits" not in st.session_state:
        st.session_state.credits = DEFAULT_CREDITS

def show_credit_sidebar():
    st.sidebar.title("💳 Credit Wallet")
    st.sidebar.metric("Credits Left", st.session_state.credits)

    if st.sidebar.button("➕ Add 5 Credits"):
        st.session_state.credits += 5

    with st.sidebar.expander("📜 Credit Info"):
        st.markdown("- 1 query = 1 credit")
        st.markdown(f"- Session starts with {DEFAULT_CREDITS} credits")

def use_credit(amount=1):
    if st.session_state.credits >= amount:
        st.session_state.credits -= amount
        return True
    else:
        st.error("🚫 Not enough credits. Please top up.")
        return False
