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
from data.database import DatabaseManager
from assistant.ai_service import AIService
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

# Standard navigation sidebar
from shared_sidebar import show_standard_sidebar
show_standard_sidebar()

# Require beta access
require_beta_access()

st.title("🧠 Welcome to Your Humsy")

# Beta tester welcome message
st.success("🎉 **Welcome to Humsy Beta!**")
st.info("💡 **Pro Tip:** Take your time with these questions - they help the AI provide personalized insights!")

# Load existing profile if available
existing_profile = load_user_profile()

# Also check if user has an active goal (new onboarding system)
db = DatabaseManager()
user_email = get_user_email() or "me@example.com"
active_goal = db.get_active_goal(user_email)

# Use active_goal data if available, otherwise fall back to existing_profile
profile_data = active_goal if active_goal else existing_profile
is_returning_user = bool(profile_data)

# Prefill or fallback values
goal = profile_data.get("title", profile_data.get("goal", "")) if profile_data else ""
joy_sources = profile_data.get("joy_sources", []) if profile_data else []
joy_other = profile_data.get("joy_other", "") if profile_data else ""
energy_drainers = profile_data.get("energy_drainers", []) if profile_data else []
energy_drainer_other = profile_data.get("energy_drainer_other", "") if profile_data else ""
therapy_coaching = profile_data.get("therapy_coaching", "No") if profile_data else "No"

# Handle availability value conversion for backward compatibility
old_availability = profile_data.get("weekly_time", "1–2 hours") if profile_data else "1–2 hours"
availability_options = ["< 1 hour", "1–2 hours", "2–4 hours", "4+ hours"]
if old_availability == "2-4 hours":  # Convert old format to new format
    availability = "2–4 hours"
elif old_availability in availability_options:
    availability = old_availability
else:
    availability = "1–2 hours"

energy = profile_data.get("energy_time", "Okay") if profile_data else "Okay"
emotional_patterns = profile_data.get("emotional_patterns", "Not sure yet") if profile_data else "Not sure yet"
small_habit = profile_data.get("small_habit", "") if profile_data else ""
reminders = profile_data.get("reminder_preference", "Yes") if profile_data else "Yes"
tone = profile_data.get("tone", "Gentle & Supportive") if profile_data else "Gentle & Supportive"
situation = profile_data.get("situation", "Freelancer") if profile_data else "Freelancer"
situation_other = profile_data.get("situation_other", "") if profile_data else ""

if is_returning_user:
    st.success("👋 Welcome back! You can update your profile or reset it below.")
else:
    st.info("👋 First time here? Let's get to know you better!")

st.subheader("🎯 Let's create your personalized plan")

# Question 1: Main goal (mandatory)
st.markdown("**1. What's your main goal?***")
goal_title = st.text_input(
    "What do you want to achieve?",
    value=goal,
    placeholder="e.g., Learn Python programming, Run a marathon, Start a business",
    help="Be specific about what you want to accomplish"
)

# Question 2: Why it matters (optional)
st.markdown("**2. Why does this matter to you?**")
why_matters = st.text_area(
    "What's driving you to pursue this goal?",
    value=profile_data.get("why_matters", "") if profile_data else "",
    placeholder="e.g., Career advancement, personal growth, helping others...",
    help="Understanding your motivation helps create a more meaningful plan"
)

# Question 3: Target date (mandatory)
st.markdown("**3. Do you have a target date?***")
has_deadline = st.radio("Do you have a deadline?", ["Yes", "No"], horizontal=True)
goal_deadline = None
if has_deadline == "Yes":
    goal_deadline = st.date_input("When is your target date?")

# Question 4: Success metric (mandatory)
st.markdown("**4. How will we know you've succeeded?***")
success_metric = st.text_input(
    "What does success look like?",
    value=profile_data.get("success_metric", "") if profile_data else "",
    placeholder="e.g., Complete 3 projects, Finish marathon under 4 hours, Launch MVP",
    help="Be specific about how you'll measure success"
)

# Question 5: Starting point (mandatory)
st.markdown("**5. What's your starting point right now?***")
starting_point = st.text_area(
    "Where are you starting from?",
    value=profile_data.get("starting_point", "") if profile_data else "",
    placeholder="e.g., Complete beginner, Some experience, Already started but stuck...",
    help="This helps us create realistic first steps"
)

# Question 6: Weekly time (mandatory)
st.markdown("**6. Realistically, how much time can you give this each week?***")
weekly_time = st.select_slider(
    "Weekly time commitment",
    options=["< 1 hour", "1–2 hours", "2–4 hours", "4–6 hours", "6+ hours"],
    value=availability
)

# Question 7: Energy time (optional)
st.markdown("**7. When do you usually have more energy?**")
energy_time = st.selectbox(
    "Your peak energy time",
    options=["Morning", "Afternoon", "Evening", "Varies", "Not sure"],
    index=safe_index(energy, ["Morning", "Afternoon", "Evening", "Varies", "Not sure"]),
    help="This helps us schedule your most important tasks"
)

# Question 8: Free days (optional)
st.markdown("**8. Any days you prefer to keep free?**")
# Handle free_days data safely
free_days_data = profile_data.get("free_days", []) if profile_data else []
if isinstance(free_days_data, str):
    # If it's a string, try to parse it as a list
    try:
        import ast
        free_days_data = ast.literal_eval(free_days_data)
    except:
        free_days_data = []
elif not isinstance(free_days_data, list):
    free_days_data = []

free_days = st.multiselect(
    "Days to avoid",
    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=free_days_data,
    help="Select days you'd prefer not to work on this goal"
)

# Question 9: Intensity (optional)
st.markdown("**9. How intense should we start?**")
intensity = st.selectbox(
    "Starting intensity",
    options=["Gentle", "Balanced", "Ambitious"],
    index=safe_index(profile_data.get("intensity", "Balanced") if profile_data else "Balanced", ["Gentle", "Balanced", "Ambitious"]),
    help="Gentle = small steps, Balanced = moderate pace, Ambitious = aggressive timeline"
)

# Question 10: Joy sources (optional)
st.markdown("**10. What brings you joy or gives you energy lately?**")
joy_options = ["Friends", "Movement", "Creating", "Helping others", "Nature", "Rest", "Learning", "Music", "Other"]

# Handle joy_sources data safely
joy_sources_data = profile_data.get("joy_sources", []) if profile_data else []
if isinstance(joy_sources_data, str):
    # If it's a string, try to parse it as a list
    try:
        import ast
        joy_sources_data = ast.literal_eval(joy_sources_data)
    except:
        joy_sources_data = []
elif not isinstance(joy_sources_data, list):
    joy_sources_data = []

joy_sources = st.multiselect(
    "What energizes you?",
    options=joy_options,
    default=joy_sources_data,
    help="We'll incorporate these into your plan to keep you motivated"
)

# Conditional "Other" specification for joy sources
if "Other" in joy_sources:
    st.info("💬 Tell us more about what brings you joy!")
    joy_other = st.text_area(
        "What else brings you joy?",
        value=profile_data.get("joy_other", "") if profile_data else "",
        placeholder="Write what brings you joy…",
        help="Specify what other things energize you"
    )
else:
    joy_other = ""

# Question 11: Energy drainers (optional)
st.markdown("**11. What tends to bring you down or drain your energy?**")
drainer_options = ["Overwhelm", "Lack of sleep", "Isolation", "Criticism", "Deadlines", "Perfectionism", "Other"]

# Handle energy_drainers data safely
energy_drainers_data = profile_data.get("energy_drainers", []) if profile_data else []
if isinstance(energy_drainers_data, str):
    # If it's a string, try to parse it as a list
    try:
        import ast
        energy_drainers_data = ast.literal_eval(energy_drainers_data)
    except:
        energy_drainers_data = []
elif not isinstance(energy_drainers_data, list):
    energy_drainers_data = []

energy_drainers = st.multiselect(
    "What drains your energy?",
    options=drainer_options,
    default=energy_drainers_data,
    help="We'll help you avoid or manage these"
)

# Conditional "Other" specification for energy drainers
if "Other" in energy_drainers:
    st.info("💬 Tell us more about what drains your energy!")
    energy_drainer_other = st.text_area(
        "What else drains your energy?",
        value=profile_data.get("energy_drainer_other", "") if profile_data else "",
        placeholder="Write what brings you down or drains your energy…",
        help="Specify what other things drain your energy"
    )
else:
    energy_drainer_other = ""

# Question 12: Therapy/coaching (optional)
st.markdown("**12. Are you currently with a therapist, coach or mentor?**")
therapy_coaching = st.selectbox(
    "Professional support",
    options=["No", "Yes", "I'd like to find one"],
    index=safe_index(profile_data.get("therapy_coaching", "No") if profile_data else "No", ["No", "Yes", "I'd like to find one"]),
    help="This helps us tailor our approach" 
)

# Question 13: Obstacles (optional)
st.markdown("**13. What might get in the way?**")
obstacles = st.text_area(
    "Potential challenges",
    value=profile_data.get("obstacles", "") if profile_data else "",
    placeholder="e.g., Time constraints, lack of confidence, competing priorities...",
    help="Identifying obstacles helps us plan around them"
)

# Question 14: Resources (optional)
st.markdown("**14. What resources do you already have?**")
resources = st.text_area(
    "Available resources",
    value=profile_data.get("resources", "") if profile_data else "",
    placeholder="e.g., Books, courses, tools, connections, budget...",
    help="This helps us leverage what you already have"
)

# Question 15: Reminders (optional)
st.markdown("**15. How do you want reminders?**")
reminder_preference = st.selectbox(
    "Reminder frequency",
    options=["Daily", "Weekdays", "Custom", "None"],
    index=safe_index(profile_data.get("reminder_preference", "Daily") if profile_data else "Daily", ["Daily", "Weekdays", "Custom", "None"]),
    help="How often would you like check-in reminders?"
)

# Generate Plan Button
st.markdown("---")
st.write(f"🔍 Debug: Button condition check - goal_title: {bool(goal_title)}, success_metric: {bool(success_metric)}, starting_point: {bool(starting_point)}, weekly_time: {bool(weekly_time)}")

if goal_title and success_metric and starting_point and weekly_time:
    st.write("🔍 Debug: All conditions met, showing form")
    st.write(f"🔍 Debug: goal_title='{goal_title}', success_metric='{success_metric}', starting_point='{starting_point}', weekly_time='{weekly_time}'")
    
    # Use a form instead of direct button - more reliable on Streamlit Cloud
    with st.form("generate_plan_form"):
        st.write("🔍 Debug: Inside form context")
        st.write("### 🚀 Ready to Generate Your Plan?")
        st.write("All required fields are filled. Click below to generate your personalized plan.")
        
        submitted = st.form_submit_button("🚀 Generate Plan", type="primary", use_container_width=True)
        
        st.write(f"🔍 Debug: Form submitted = {submitted}")
        
        if submitted:
            st.write("🔍 Debug: Form submitted! Starting plan generation...")
            
            # Test secrets availability
            try:
                api_key = st.secrets.get("openai_api_key", "")
                st.write(f"🔍 Debug: API key available = {bool(api_key)}")
                st.write(f"🔍 Debug: API key length = {len(api_key) if api_key else 0}")
            except Exception as secrets_error:
                st.write(f"🔍 Debug: Secrets error: {str(secrets_error)}")
            
            user_email = get_user_email() or "me@example.com"
            st.write(f"🔍 Debug: User email: {user_email}")
            
            try:
                db = DatabaseManager()
                st.write("🔍 Debug: Database manager created")
                
                goal_id = db.create_goal(user_email, {
                    "title": goal_title,
                    "why_matters": why_matters,
                    "deadline": str(goal_deadline) if goal_deadline else None,
                    "success_metric": success_metric,
                    "starting_point": starting_point,
                    "weekly_time": weekly_time,
                    "energy_time": energy_time,
                    "free_days": ",".join(free_days) if free_days else "",
                    "intensity": intensity,
                    "joy_sources": joy_sources,
                    "energy_drainers": energy_drainers,
                    "therapy_coaching": therapy_coaching,
                    "obstacles": obstacles,
                    "resources": resources,
                    "reminder_preference": reminder_preference,
                    "auto_adapt": True
                })
                st.write(f"🔍 Debug: Goal created with ID: {goal_id}")
                
                # Generate plan
                try:
                    ai = AIService()
                    st.write("🔍 Debug: AI service created successfully")
                    st.write(f"🔍 Debug: AI service client = {ai.client is not None}")
                except Exception as ai_error:
                    st.error(f"❌ Error creating AI service: {str(ai_error)}")
                    st.write(f"🔍 Debug: AI service error details: {type(ai_error).__name__}: {str(ai_error)}")
                    return
                plan_data = {
                    "title": goal_title,
                    "why_matters": why_matters,
                    "deadline": str(goal_deadline) if goal_deadline else None,
                    "success_metric": success_metric,
                    "starting_point": starting_point,
                    "weekly_time": weekly_time,
                    "energy_time": energy_time,
                    "free_days": free_days,
                    "intensity": intensity,
                    "joy_sources": joy_sources,
                    "energy_drainers": energy_drainers,
                    "obstacles": obstacles,
                    "resources": resources
                }
                
                with st.spinner("🤖 Generating your personalized plan..."):
                    try:
                        plan = ai.generate_goal_plan(plan_data, user_email)
                        st.write("🔍 Debug: Plan generation completed")
                        st.write(f"🔍 Debug: Plan keys: {list(plan.keys()) if plan else 'None'}")
                        st.write(f"🔍 Debug: Milestones count: {len(plan.get('milestones', [])) if plan else 0}")
                        st.write(f"🔍 Debug: Steps count: {len(plan.get('steps', [])) if plan else 0}")
                        
                        if not plan or not plan.get("milestones"):
                            st.error("❌ Failed to generate plan. Please check your API key and try again.")
                            st.write(f"🔍 Debug: Plan is None or has no milestones")
                        else:
                            db.save_milestones(goal_id, plan.get("milestones", []))
                            db.save_steps(goal_id, plan.get("steps", []))
                            
                            # Store in session state to persist across reruns
                            st.session_state.plan_generated = True
                            st.session_state.generated_plan = plan
                            st.session_state.goal_id = goal_id
                            
                            st.write("🔍 Debug: Session state set")
                            st.write(f"🔍 Debug: plan_generated = {st.session_state.get('plan_generated')}")
                            st.write(f"🔍 Debug: goal_id = {st.session_state.get('goal_id')}")
                            
                            st.success("🎉 Plan generated successfully!")
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error generating plan: {str(e)}")
                        st.write(f"🔍 Debug: Exception details: {type(e).__name__}: {str(e)}")
                        
            except Exception as e:
                st.error(f"❌ Error in plan generation process: {str(e)}")
                st.write(f"🔍 Debug: Exception details: {type(e).__name__}: {str(e)}")
else:
    st.write("🔍 Debug: Button condition not met - button not shown")

# Show plan if it was generated
st.write(f"🔍 Debug: Checking session state - plan_generated = {st.session_state.get('plan_generated', False)}")

if st.session_state.get("plan_generated", False):
    plan = st.session_state.get("generated_plan", {})
    goal_id = st.session_state.get("goal_id")
    
    st.write("🔍 Debug: Plan display section reached")
    st.write(f"🔍 Debug: Plan data: {list(plan.keys()) if plan else 'None'}")
    
    # Display the generated plan
    st.subheader("📋 Your Generated Plan")
    
    # Display milestones
    if plan.get("milestones"):
        st.markdown("### 🎯 Milestones")
        for i, milestone in enumerate(plan["milestones"], 1):
            with st.expander(f"Milestone {i}: {milestone.get('title', 'Untitled')}"):
                st.write(f"**Description:** {milestone.get('description', 'No description')}")
                st.write(f"**Target Date:** {milestone.get('target_date', 'Not set')}")
    
    # Display steps
    if plan.get("steps"):
        st.markdown("### 📝 Action Steps")
        for i, step in enumerate(plan["steps"], 1):
            with st.expander(f"Step {i}: {step.get('title', 'Untitled')}"):
                st.write(f"**Description:** {step.get('description', 'No description')}")
                st.write(f"**Due Date:** {step.get('due_date', 'Not set')}")
                st.write(f"**Suggested Day:** {step.get('suggested_day', 'Not set')}")
                st.write(f"**Estimated Time:** {step.get('estimated_time', 'Not set')}")
    
    st.markdown("---")
    
    # Post-generation questions
    st.subheader("📋 Plan Review")
    
    col1, col2 = st.columns(2)
    with col1:
        edit_plan = st.radio("Would you like to edit the plan before saving?", ["Yes", "No"], horizontal=True)
    with col2:
        auto_adapt = st.radio("Do you want the plan to auto-adapt when you skip tasks?", ["Yes", "No"], horizontal=True)
    
    # Save Plan button
    if st.button("💾 Save Plan", type="primary", use_container_width=True):
        try:
            db = DatabaseManager()
            
            # Check if update_goal method exists
            if hasattr(db, 'update_goal'):
                # Update goal with user preferences
                db.update_goal(goal_id, {
                    "auto_adapt": auto_adapt == "Yes"
                })
            else:
                # Fallback: direct SQL update
                import sqlite3
                conn = sqlite3.connect(db.db_path)
                cur = conn.cursor()
                cur.execute("UPDATE goals SET auto_adapt = ? WHERE id = ?", (auto_adapt == "Yes", goal_id))
                conn.commit()
                conn.close()
            
            st.success("🎉 Your personalized plan has been saved!")
            st.balloons()
            
            # Clear session state
            st.session_state.plan_generated = False
            st.session_state.generated_plan = None
            st.session_state.goal_id = None
            
            # Redirect to plan page
            st.switch_page("pages/plan.py")
            
        except Exception as e:
            st.error(f"❌ Error saving plan: {str(e)}")
            st.info("💡 Your plan was generated successfully, but there was an issue saving your preferences. You can still view your plan on the Plan page.")
            
            # Clear session state and redirect anyway
            st.session_state.plan_generated = False
            st.session_state.generated_plan = None
            st.session_state.goal_id = None
            
            if st.button("📋 Go to Plan Page", use_container_width=True):
                st.switch_page("pages/plan.py")
            
else:
    st.info("👆 Please fill in all mandatory fields (marked with *) to generate your personalized plan.")

# Additional profile information is now integrated into the main onboarding flow above
# No need for duplicate questions

