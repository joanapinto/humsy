"""
Shared sidebar navigation for all pages
"""
import streamlit as st
from auth import get_user_email, logout, get_admin_email

def show_standard_sidebar():
    """Display the standard navigation sidebar on all pages"""
    
    # Check if we're on a page that needs additional sidebar content
    current_page = st.session_state.get('current_page', '')
    
    with st.sidebar:
        st.subheader("🧭 Navigation")
        
        # Main pages
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/profile.py")
        
        if st.button("🗺️ Plan", use_container_width=True):
            st.switch_page("pages/plan.py")
        
        if st.button("📝 Daily Check-in", use_container_width=True):
            st.switch_page("pages/daily_checkin.py")
        
        if st.button("😊 Mood Tracker", use_container_width=True):
            st.switch_page("pages/mood_tracker.py")
        
        if st.button("🌱 Weekly Reflection", use_container_width=True):
            st.switch_page("pages/reflection.py")
        
        if st.button("📊 Insights", use_container_width=True):
            st.switch_page("pages/history.py")
        
        st.write("---")
        
        # Feedback section
        st.subheader("💬 Feedback")
        if st.button("📝 Give Feedback", use_container_width=True):
            st.markdown("**[Open Feedback Form](https://tally.so/r/mBr11Q)**")
            st.info("Your feedback helps us make Humsy better for everyone! 🚀")
        
        if st.button("💡 Suggest Feature", use_container_width=True):
            st.markdown("**[Open Feature Suggestion Form](https://tally.so/r/mROLG4)**")
            st.info("💡 **Feature Suggestion**\n\nHave an idea for a new feature? We'd love to hear it! Share your thoughts on what could make Humsy even better.")
        
        if st.button("🐛 Report Bug", use_container_width=True):
            st.markdown("**[Open Bug Report Form](https://tally.so/r/waR7Eq)**")
            st.info("🐛 **Bug Report**\n\nPlease detail step by step how to reproduce the bug. Include:\n- What you were trying to do\n- What happened instead\n- Steps to reproduce")
        
        st.write("---")
        
        # Admin insights access
        user_email = get_user_email()
        admin_email = get_admin_email()
        if user_email == admin_email:
            st.subheader("🔓 Admin Tools")
            if st.button("📊 Database Insights", use_container_width=True):
                st.switch_page("pages/insights.py")
        
        st.write("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            logout()
