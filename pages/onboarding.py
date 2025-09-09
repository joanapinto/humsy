import streamlit as st
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path to find the data module
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from data.storage import save_user_profile, load_user_profile, reset_user_profile
from auth import require_beta_access, get_user_email

def safe_index(value, options, default=0):
    """Safely get the index of a value in a list, with fallback to default"""
    try:
        return options.index(value)
    except ValueError:
        return default

st.set_page_config(page_title="Humsy - Onboarding", page_icon="🧠")

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

# Custom navigation sidebar
with st.sidebar:
    st.subheader("🧭 Navigation")
    
    # Main pages
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/profile.py")
    
    if st.button("📝 Daily Check-in", use_container_width=True):
        st.switch_page("pages/daily_checkin.py")
    
    if st.button("🌱 Weekly Reflection", use_container_width=True):
        st.switch_page("pages/reflection.py")
    
    if st.button("📊 Insights", use_container_width=True):
        st.switch_page("pages/history.py")
    
    st.write("---")
    
    # Admin insights access
    user_email = get_user_email()
    if user_email == "joanapnpinto@gmail.com":
        st.subheader("🔓 Admin Tools")
        if st.button("📊 Database Insights", use_container_width=True):
            st.switch_page("pages/insights.py")
    
    st.write("---")
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        from auth import logout
        logout()

# Require beta access
require_beta_access()

st.title("🧠 Welcome to Your Humsy")

# Beta tester welcome message
st.success("🎉 **Welcome to Humsy Beta!**")
st.info("💡 **Pro Tip:** Take your time with these questions - they help the AI provide personalized insights!")

# Load existing profile if available
existing_profile = load_user_profile()
is_returning_user = bool(existing_profile)

# Prefill or fallback values
goal = existing_profile.get("goal", "")
joy_sources = existing_profile.get("joy_sources", [])
joy_other = existing_profile.get("joy_other", "")
energy_drainers = existing_profile.get("energy_drainers", [])
energy_drainer_other = existing_profile.get("energy_drainer_other", "")
therapy_coaching = existing_profile.get("therapy_coaching", "No")

# Handle availability value conversion for backward compatibility
old_availability = existing_profile.get("availability", "1–2 hours")
availability_options = ["< 1 hour", "1–2 hours", "2–4 hours", "4+ hours"]
if old_availability == "2-4 hours":  # Convert old format to new format
    availability = "2–4 hours"
elif old_availability in availability_options:
    availability = old_availability
else:
    availability = "1–2 hours"

energy = existing_profile.get("energy", "Okay")
emotional_patterns = existing_profile.get("emotional_patterns", "Not sure yet")
small_habit = existing_profile.get("small_habit", "")
reminders = existing_profile.get("reminders", "Yes")
tone = existing_profile.get("tone", "Gentle & Supportive")
situation = existing_profile.get("situation", "Freelancer")
situation_other = existing_profile.get("situation_other", "")

if is_returning_user:
    st.success("👋 Welcome back! You can update your profile or reset it below.")
else:
    st.info("👋 First time here? Let's get to know you better!")

st.subheader("🎯 Let's understand your needs")

# Question 1: Main area of support
goal = st.text_area(
    "🎯 What's one area of your life you'd like more support with right now?",
    value=goal,
    placeholder="e.g., staying focused, managing emotions, building routines…",
    help="This helps us tailor your experience"
)

st.subheader("❤️ Understanding what energizes you")

# Question 2: Joy sources
joy_options = ["Friends", "Movement", "Creating", "Helping others", "Nature", "Rest", "Learning", "Other"]
joy_sources = st.multiselect(
    "❤️ What brings you joy or gives you energy lately?",
    options=joy_options,
    default=joy_sources
)

# Conditional "Other" specification for joy sources
if "Other" in joy_sources:
    st.info("💬 Tell us more about what brings you joy!")
    joy_other = st.text_area(
        "Do you want to specify what?",
        value=joy_other,
        placeholder="Write what brings you joy…"
    )

st.subheader("🌧️ Understanding what drains you")

# Question 3: Energy drainers
drainer_options = ["Overwhelm", "Lack of sleep", "Isolation", "Criticism", "Deadlines", "Other"]
energy_drainers = st.multiselect(
    "🌧️ What tends to bring you down or drain your energy?",
    options=drainer_options,
    default=energy_drainers
)

# Conditional "Other" specification for energy drainers
if "Other" in energy_drainers:
    st.info("💬 Tell us more about what drains your energy!")
    energy_drainer_other = st.text_area(
        "Do you want to specify what?",
        value=energy_drainer_other,
        placeholder="Write what brings you down or drains your energy…"
    )

st.subheader("💬 Professional support")

# Question 4: Therapy/coaching
therapy_coaching = st.selectbox(
    "💬 Are you currently working with a therapist, coach, or mentor?",
    options=["No", "Yes", "I'd like to find one"],
    index=safe_index(therapy_coaching, ["No", "Yes", "I'd like to find one"])
)

st.subheader("⏱️ Time and energy assessment")

# Question 5: Time availability
availability = st.selectbox(
    "⏱️ On most weekdays, how much time do you feel you can dedicate to yourself or your goals?",
    options=["< 1 hour", "1–2 hours", "2–4 hours", "4+ hours"],
    index=safe_index(availability, ["< 1 hour", "1–2 hours", "2–4 hours", "4+ hours"])
)

# Question 6: Current energy levels
energy = st.selectbox(
    "🔋 How would you describe your current energy levels?",
    options=["Very low", "Low", "Okay", "Good", "High"],
    index=safe_index(energy, ["Very low", "Low", "Okay", "Good", "High"])
)

# Conditional questions for low energy
if energy in ["Low", "Very low"]:
    st.info("💡 Since your energy is low, let's see how we can help!")
    
    # Question 6.1: Emotional patterns help
    emotional_patterns = st.selectbox(
        "🧠 Do you want help understanding emotional patterns over time?",
        options=["Yes", "No", "Not sure yet"],
        index=safe_index(emotional_patterns, ["Yes", "No", "Not sure yet"])
    )
    
    # Question 6.2: Small habit building
    small_habit = st.text_area(
        "🌱 What's one small habit you'd love to build right now?",
        value=small_habit,
        placeholder="e.g., journaling, moving more, taking breaks…"
    )

st.subheader("🔔 Assistant preferences")

# Question 7: Reminders
reminders = st.selectbox(
    "🔔 Would you like gentle reminders or check-in nudges from your assistant?",
    options=["Yes", "No"],
    index=safe_index(reminders, ["Yes", "No"])
)

# Question 8: Communication tone
tone = st.selectbox(
    "🗣️ How would you like your assistant to speak to you?",
    options=["Direct & Motivating", "Gentle & Supportive", "Neutral & Balanced"],
    index=safe_index(tone, ["Direct & Motivating", "Gentle & Supportive", "Neutral & Balanced"])
)

st.subheader("💼 Your situation")

# Question 9: Current situation
situation = st.selectbox(
    "💼 Which of these best describes your current situation?",
    options=["Freelancer", "New parent", "PhD student", "Full-time job", "Unemployed", "Other"],
    index=safe_index(situation, ["Freelancer", "New parent", "PhD student", "Full-time job", "Unemployed", "Other"])
)

# Conditional "Other" specification for situation
if situation == "Other":
    st.info("💬 Tell us more about your situation!")
    situation_other = st.text_area(
        "Do you want to specify what?",
        value=situation_other,
        placeholder="Describe your current situation in a few words…"
    )

# Save button
submitted = st.button("💾 Save & Continue", type="primary", use_container_width=True)

# Helpful tip before submission
st.info("💡 **What's next?** After saving, you'll be guided to start your first check-in and explore the app!")

if submitted:
    user_profile = {
        "goal": goal,
        "joy_sources": joy_sources,
        "joy_other": joy_other if "Other" in joy_sources else "",
        "energy_drainers": energy_drainers,
        "energy_drainer_other": energy_drainer_other if "Other" in energy_drainers else "",
        "therapy_coaching": therapy_coaching,
        "availability": availability,
        "energy": energy,
        "emotional_patterns": emotional_patterns if energy in ["Low", "Very low"] else "Not applicable",
        "small_habit": small_habit if energy in ["Low", "Very low"] else "",
        "reminders": reminders,
        "tone": tone,
        "situation": situation,
        "situation_other": situation_other if situation == "Other" else ""
    }

    save_user_profile(user_profile)
    st.success("✅ Profile saved successfully!")
        
    # Feedback prompt after onboarding completion
    st.write("---")
    st.subheader("🎉 Welcome to Humsy!")
    st.write("You're all set up! How was the onboarding experience?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👍 Smooth & easy!", key="onboarding_good"):
            st.success("Great! We're glad it was easy for you! 🙏")
            st.switch_page("pages/daily_checkin.py")
    with col2:
        if st.button("🤔 Could be clearer", key="onboarding_ok"):
            st.info("We'd love to improve it! [📝 Feedback Form](https://tally.so/r/mBr11Q)")
            st.switch_page("pages/daily_checkin.py")
    with col3:
        if st.button("📝 Share detailed feedback", key="onboarding_detailed"):
            st.markdown("**[📋 Open Feedback Form](https://tally.so/r/mBr11Q)**")
            st.switch_page("pages/daily_checkin.py")

# 🚨 Reset Button with Confirmation
st.markdown("---")
st.subheader("⚠️ Reset your profile")

confirm_reset = st.checkbox("I understand this will delete all my saved profile data.")

if confirm_reset:
    if st.button("❌ Reset My Profile"):
        reset_user_profile()
        st.success("✅ Profile reset successfully. Redirecting...")
        st.rerun()
else:
    st.warning("Tick the box above to enable the reset button.")
