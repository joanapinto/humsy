"""
Profile Page for Humsy
User profile management, goals, and feedback
"""

import streamlit as st
from auth import require_beta_access, get_user_email
from data.storage import load_user_profile, save_user_profile
from data.database import DatabaseManager
from datetime import datetime

# Require beta access
require_beta_access()

# Set page config
st.set_page_config(
    page_title="Humsy - Profile",
    page_icon="👤",
    layout="wide"
)

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

def main():
    st.title("👤 Your Profile")
    
    # Get user email and profile
    user_email = get_user_email()
    user_profile = load_user_profile()
    
    # Also check if user has an active goal (new onboarding system)
    db = DatabaseManager()
    active_goal = db.get_active_goal(user_email)
    
    if not user_profile and not active_goal:
        st.warning("No profile found. Please complete onboarding first.")
        if st.button("🚀 Go to Onboarding"):
            st.switch_page("pages/onboarding.py")
        return
    
    # Profile Overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Profile Information")
        st.write(f"**Email:** {user_email}")
        
        # Use active_goal data if available, otherwise fall back to user_profile
        profile_data = active_goal if active_goal else user_profile
        
        # Member since date
        member_since = profile_data.get('created_at', profile_data.get('member_since')) if profile_data else None
        if member_since:
            try:
                # Try to parse the date if it's a string
                if isinstance(member_since, str):
                    from datetime import datetime
                    parsed_date = datetime.fromisoformat(member_since.replace('Z', '+00:00'))
                    formatted_date = parsed_date.strftime("%B %d, %Y")
                else:
                    formatted_date = str(member_since)
                st.write(f"**Member since:** {formatted_date}")
            except:
                st.write(f"**Member since:** {member_since}")
        else:
            st.write("**Member since:** Unknown")
        
        # Current goal
        st.write("---")
        st.subheader("🎯 Current Goal")
        goal = profile_data.get('title', profile_data.get('goal', 'Not specified')) if profile_data else 'Not specified'
        st.write(f"**Goal:** {goal}")
        
        # Why it matters
        why_matters = profile_data.get('why_matters', 'Not specified') if profile_data else 'Not specified'
        if why_matters and why_matters != 'Not specified':
            st.write(f"**Why this matters:** {why_matters}")
        
        # Starting point
        starting_point = profile_data.get('starting_point', 'Not specified') if profile_data else 'Not specified'
        if starting_point and starting_point != 'Not specified':
            st.write(f"**Starting Point:** {starting_point}")
        
        # Joy sources
        joy_sources = profile_data.get('joy_sources', [])
        if joy_sources:
            st.write(f"**What brings you joy:** {', '.join(joy_sources) if isinstance(joy_sources, list) else joy_sources}")
        
        # Energy drainers
        energy_drainers = profile_data.get('energy_drainers', [])
        if energy_drainers:
            st.write(f"**What drains your energy:** {', '.join(energy_drainers) if isinstance(energy_drainers, list) else energy_drainers}")
        
        # Therapy/coaching
        therapy_coaching = profile_data.get('therapy_coaching', 'Not specified')
        if therapy_coaching and therapy_coaching != 'Not specified':
            st.write(f"**Professional Support:** {therapy_coaching}")
        
        # Obstacles
        obstacles = profile_data.get('obstacles', 'Not specified')
        if obstacles and obstacles != 'Not specified':
            st.write(f"**Potential Obstacles:** {obstacles}")
        
        # Resources
        resources = profile_data.get('resources', 'Not specified')
        if resources and resources != 'Not specified':
            st.write(f"**Available Resources:** {resources}")
        
        # Reminders
        reminders = profile_data.get('reminders', 'Not specified')
        if reminders and reminders != 'Not specified':
            st.write(f"**Reminder Preferences:** {reminders}")
    
    with col2:
        st.subheader("📊 Quick Stats")
        # Add some quick stats here if available
        st.info("Profile statistics coming soon!")
    
    # Editable Goal Section
    st.write("---")
    st.subheader("🎯 Your Goal Details")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        current_goal = profile_data.get('title', profile_data.get('goal', 'Not set')) if profile_data else 'Not set'
        st.write(f"**Current Goal:** {current_goal}")
        
        # Show additional goal details if available
        if profile_data:
            deadline = profile_data.get('deadline', 'Not specified')
            if deadline and deadline != 'Not specified':
                st.write(f"**Target Date:** {deadline}")
            
            weekly_time = profile_data.get('weekly_time', 'Not specified')
            if weekly_time and weekly_time != 'Not specified':
                st.write(f"**Weekly Time Commitment:** {weekly_time}")
            
            energy_time = profile_data.get('energy_time', 'Not specified')
            if energy_time and energy_time != 'Not specified':
                st.write(f"**Peak Energy Time:** {energy_time}")
            
            free_days = profile_data.get('free_days', 'Not specified')
            if free_days and free_days != 'Not specified':
                st.write(f"**Preferred Free Days:** {free_days}")
            
            intensity = profile_data.get('intensity', 'Not specified')
            if intensity and intensity != 'Not specified':
                st.write(f"**Intensity Preference:** {intensity}")
    
    with col2:
        if st.button("✏️ Edit Goal", use_container_width=True):
            st.session_state.editing_goal = True
    
    # Goal editing form
    if st.session_state.get('editing_goal', False):
        with st.form("goal_edit_form"):
            new_goal = st.text_area(
                "What's your main goal?",
                value=current_goal if current_goal != 'Not set' else "",
                placeholder="e.g., Improve focus and productivity, Better work-life balance, Reduce stress...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Goal", use_container_width=True):
                    if new_goal.strip():
                        user_profile['goal'] = new_goal.strip()
                        save_user_profile(user_profile)
                        st.success("✅ Goal updated successfully!")
                        st.session_state.editing_goal = False
                        st.rerun()
                    else:
                        st.error("Please enter a goal")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.editing_goal = False
                    st.rerun()
    
    # Onboarding Answers (Editable)
    st.write("---")
    st.subheader("📝 Your Onboarding Answers")
    
    # Use profile_data (active_goal or user_profile) for all onboarding answers
    if profile_data:
        # Energy drainers
        st.write("**What drains your energy?**")
        energy_drainers = profile_data.get('energy_drainers', [])
        energy_drainer_other = profile_data.get('energy_drainer_other', '')
        
        if energy_drainers:
            for drainer in energy_drainers:
                st.write(f"• {drainer}")
            if energy_drainer_other:
                st.write(f"• {energy_drainer_other}")
        else:
            st.info("No energy drainers specified")
        
        # Energy boosters (joy sources)
        st.write("**What gives you energy?**")
        joy_sources = profile_data.get('joy_sources', [])
        joy_other = profile_data.get('joy_other', '')
        
        if joy_sources:
            for source in joy_sources:
                st.write(f"• {source}")
            if joy_other:
                st.write(f"• {joy_other}")
        else:
            st.info("No energy sources specified")
        
        # Stress triggers (using energy drainers as stress indicators)
        st.write("**What stresses you out?**")
        if energy_drainers:
            for drainer in energy_drainers:
                st.write(f"• {drainer}")
            if energy_drainer_other:
                st.write(f"• {energy_drainer_other}")
        else:
            st.info("No stress triggers specified")
        
        # Additional onboarding answers
        st.write("**Professional Support:**")
        therapy_coaching = profile_data.get('therapy_coaching', 'Not specified')
        st.write(f"• {therapy_coaching}")
        
        st.write("**Potential Obstacles:**")
        obstacles = profile_data.get('obstacles', 'Not specified')
        st.write(f"• {obstacles}")
        
        st.write("**Available Resources:**")
        resources = profile_data.get('resources', 'Not specified')
        st.write(f"• {resources}")
        
        st.write("**Reminder Preferences:**")
        reminders = profile_data.get('reminders', 'Not specified')
        st.write(f"• {reminders}")
        
        st.write("**Intensity Preference:**")
        intensity = profile_data.get('intensity', 'Not specified')
        st.write(f"• {intensity}")
        
    else:
        st.info("No onboarding data available. Please complete onboarding first.")
    
    # Edit onboarding answers button
    if st.button("✏️ Edit Onboarding Answers", use_container_width=True):
        st.switch_page("pages/onboarding.py")
    
    # Feedback Section
    st.write("---")
    st.subheader("💬 Help Us Improve Humsy")
    st.write("Your feedback is invaluable for making Humsy better! 🚀")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Give Feedback", use_container_width=True):
            st.markdown("""
            ### 📝 We'd love your feedback!
            
            Please take a moment to share your thoughts about Humsy:
            
            **[📋 Open Feedback Form](https://tally.so/r/mBr11Q)**
            
            Your feedback helps us make the app better for everyone! 🚀
            """)
    
    with col2:
        if st.button("🐛 Report Bug", use_container_width=True):
            st.markdown("**[🐛 Open Bug Report Form](https://tally.so/r/waR7Eq)**")
            st.info("🐛 **Bug Report**\n\nPlease detail step by step how to reproduce the bug. Include:\n- What you were trying to do\n- What happened instead\n- Steps to reproduce")
    
    with col3:
        if st.button("💡 Suggest Feature", use_container_width=True):
            st.markdown("**[💡 Open Feature Suggestion Form](https://tally.so/r/mROLG4)**")
            st.info("💡 **Feature Suggestion**\n\nHave an idea for a new feature? We'd love to hear it! Share your thoughts on what could make Humsy even better.")
    
    # Beta Tester Guide
    st.write("---")
    st.subheader("📋 Beta Tester Guide")
    if st.button("📋 View Beta Guide", use_container_width=True):
        st.markdown("""
        ### 🚀 **Beta Tester Guide**
        
        **🎯 Quick Start:**
        1. **Complete your onboarding** - Set your goals and preferences first!
        2. **Start with a time-aware check-in** - Morning, afternoon, or evening based on current time
        3. **Track your mood** - Build patterns and insights
        4. **Try the AI features** - Personalized analysis and tips
        5. **Explore weekly reflections** - Learn from your patterns
        
        **💡 Pro Tips:**
        - **Be consistent** - Daily check-ins build the most valuable insights
        - **Use the AI features** - They get smarter with your data
        - **Don't worry about perfection** - Just log how you're feeling
        - **Try different times** - Morning, afternoon, and evening check-ins
        
        **🤖 AI Features:**
        - **Personalized greetings** - AI that knows your patterns
        - **Smart task planning** - Based on your energy and goals
        - **Usage limits** - 20 AI calls per day, 400 per month
        - **Graceful fallback** - Works perfectly even without AI
        
        **⚠️ Beta Expectations:**
        - This is a **beta version** - some things might change
        - **AI features** have usage limits to control costs
        - **Data is saved locally** - your privacy is protected
        - **Updates** will add new features based on your feedback
        
        **🎁 Beta Perks:**
        - **Early access** to new features
        - **Direct influence** on development
        - **Priority support** for issues
        - **Exclusive insights** into the development process
        """)

    # Reset Profile Section
    st.markdown("---")
    st.subheader("⚠️ Reset Your Profile")
    st.warning("⚠️ **Warning:** This will permanently delete all your saved profile data, goals, and plans. This action cannot be undone.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("**What gets deleted:**")
        st.write("• Your onboarding answers")
        st.write("• Your active goal and plan")
        st.write("• All milestones and action steps")
        st.write("• Your mood tracking data")
        st.write("• All progress history")
    
    with col2:
        confirm_reset = st.checkbox("I understand this will delete all my data permanently.")
        
        if confirm_reset:
            if st.button("❌ Reset My Profile", type="secondary"):
                # Import the reset function
                from data.storage import reset_user_profile
                reset_user_profile()
                st.success("✅ Profile reset successfully. Redirecting...")
                st.rerun()
        else:
            st.info("Check the box to enable the reset button.")

if __name__ == "__main__":
    main()
