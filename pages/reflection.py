import streamlit as st
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path to find the data module
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from data.storage import save_user_profile, load_user_profile
from data.database import DatabaseManager
from auth import require_beta_access, get_user_email

st.set_page_config(page_title="Humsy - Reflection", page_icon="🤔")

# Hide Streamlit's default navigation
hide_streamlit_navigation = """
<style>
    /* Hide the automatic pages navigation */
    .stSidebar > div:first-child > div:first-child > div:nth-child(2) {
        display: none;
    }
    
    /* Hide the default page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Hide any remaining automatic navigation */
    .css-1544g2n {
        display: none;
    }
</style>
"""
st.markdown(hide_streamlit_navigation, unsafe_allow_html=True)

# Standard navigation sidebar
from shared_sidebar import show_standard_sidebar
show_standard_sidebar()

# Require beta access
require_beta_access()

st.title("🤔 Weekly Reflection")

# Load user profile
user_profile = load_user_profile()

# Also check if user has an active goal (new onboarding system)
# Initialize database with Supabase-first fallback
try:
    from data.supabase_manager import SupabaseManager
    db = SupabaseManager()
except Exception:
    from data.database import DatabaseManager
    db = DatabaseManager()

user_email = get_user_email() or "me@example.com"
active_goal = db.get_active_goal(user_email)

if not user_profile and not active_goal:
    st.warning("Please complete onboarding first!")
    if st.button("🚀 Go to Onboarding", use_container_width=True):
        st.switch_page("pages/onboarding.py")
else:
    st.write("Take some time to reflect on your week and progress toward your goals.")
    
    with st.form("reflection_form"):
        wins = st.text_area("🏆 What were your biggest wins this week?")
        
        challenges = st.text_area("🚧 What challenges did you face?")
        
        lessons = st.text_area("📚 What did you learn?")
        
        next_week = st.text_area("🎯 What do you want to focus on next week?")
        
        submitted = st.form_submit_button("💾 Save Reflection")
        
        if submitted:
            # Save reflection to database
            try:
                from datetime import datetime, timedelta
                
                # Get current week dates
                today = datetime.now()
                monday = today - timedelta(days=today.weekday())
                sunday = monday + timedelta(days=6)
                
                # Create reflection summary
                reflection_summary = f"""Weekly Reflection - {monday.strftime('%B %d')} to {sunday.strftime('%B %d, %Y')}

🏆 Wins: {wins}

🚧 Challenges: {challenges}

📚 Lessons: {lessons}

🎯 Next Week Focus: {next_week}"""
                
                # Save to database
                db.save_weekly_reflection(
                    user_email=user_email,
                    week_start_date=monday.strftime('%Y-%m-%d'),
                    week_end_date=sunday.strftime('%Y-%m-%d'),
                    summary_text=reflection_summary,
                    insights={
                        "wins": wins,
                        "challenges": challenges,
                        "lessons": lessons,
                        "next_week_focus": next_week
                    },
                    patterns={},
                    recommendations={},
                    data_summary={
                        "reflection_type": "manual",
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                st.success("✅ Reflection saved successfully to your personal archive!")
                
            except Exception as e:
                st.error(f"❌ Error saving reflection: {str(e)}")
                st.write(f"🔍 Error type: {type(e).__name__}")
                import traceback
                st.write(f"🔍 Full traceback: {traceback.format_exc()}")
