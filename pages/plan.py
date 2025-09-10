import streamlit as st
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add the parent directory to the Python path to find the data module
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from data.database import DatabaseManager
from auth import require_beta_access, get_user_email

st.set_page_config(page_title="Plan", page_icon="🗺️")

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

st.title("🗺️ Your Plan")

db = DatabaseManager()
user_email = get_user_email() or "me@example.com"
goal = db.get_active_goal(user_email)

if not goal:
    st.info("No active goal yet. Go to Onboarding to create one.")
    st.stop()

st.subheader(f"🎯 {goal['title']}")

# Plan management buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 Regenerate Plan", use_container_width=True):
        # Regenerate the plan with the new prompt
        from assistant.ai_service import AIService
        
        st.info("🔄 Regenerating your plan with ultra-explicit instructions...")
        
        # Prepare goal data for plan generation
        plan_data = {
            "title": goal.get("title", ""),
            "why_matters": goal.get("why_matters", ""),
            "deadline": goal.get("deadline"),
            "success_metric": goal.get("success_metric", ""),
            "starting_point": goal.get("starting_point", ""),
            "weekly_time": goal.get("weekly_time", ""),
            "energy_time": goal.get("energy_time", ""),
            "free_days": goal.get("free_days", ""),
            "intensity": goal.get("intensity", ""),
            "joy_sources": goal.get("joy_sources", []),
            "energy_drainers": goal.get("energy_drainers", []),
            "obstacles": goal.get("obstacles", ""),
            "resources": goal.get("resources", "")
        }
        
        # Show what we're working with
        st.write(f"**Your goal:** {plan_data['title']}")
        st.write(f"**Weekly time:** {plan_data['weekly_time']}")
        
        # Generate new plan
        ai = AIService()
        with st.spinner("🤖 Generating ultra-explicit plan..."):
            new_plan = ai.generate_goal_plan(plan_data, user_email)
        
        # Show what was generated
        st.write("**Generated plan preview:**")
        st.write(f"Milestones: {len(new_plan.get('milestones', []))}")
        st.write(f"Steps: {len(new_plan.get('steps', []))}")
        
        # Clear old plan and save new one
        db.clear_plan(goal["id"])
        db.save_milestones(goal["id"], new_plan.get("milestones", []))
        db.save_steps(goal["id"], new_plan.get("steps", []))
        
        st.success("✅ Plan regenerated with ultra-explicit instructions!")
        st.rerun()
with col2:
    if st.button("✏️ Edit Goal", use_container_width=True):
        st.switch_page("pages/profile.py")
with col3:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/history.py")

st.write("---")

# Goal overview in expandable sections
with st.expander("📋 Goal Details", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Why this matters:**")
        st.write(goal.get("why_matters") or "Not specified")
        
        st.markdown("**Success looks like:**")
        st.write(goal.get("success_metric") or "Not specified")
        
        st.markdown("**Starting point:**")
        st.write(goal.get("starting_point") or "Not specified")
        
        st.markdown("**Weekly time commitment:**")
        st.write(goal.get("weekly_time") or "Not specified")
    
    with col2:
        st.markdown("**Target date:**")
        st.write(goal.get("deadline") or "No deadline set")
        
        st.markdown("**Peak energy time:**")
        st.write(goal.get("energy_time") or "Not specified")
        
        st.markdown("**Free days:**")
        st.write(goal.get("free_days") or "None")
        
        st.markdown("**Starting intensity:**")
        st.write(goal.get("intensity") or "Balanced")

with st.expander("🎨 Personal Context"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**What energizes you:**")
        joy_sources = goal.get("joy_sources", [])
        if joy_sources:
            for source in joy_sources:
                st.write(f"• {source}")
        else:
            st.write("Not specified")
        
        st.markdown("**Resources available:**")
        st.write(goal.get("resources") or "Not specified")
    
    with col2:
        st.markdown("**What drains your energy:**")
        energy_drainers = goal.get("energy_drainers", [])
        if energy_drainers:
            for drainer in energy_drainers:
                st.write(f"• {drainer}")
        else:
            st.write("Not specified")
        
        st.markdown("**Potential obstacles:**")
        st.write(goal.get("obstacles") or "None identified")

with st.expander("⚙️ Settings"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Professional support:**")
        st.write(goal.get("therapy_coaching") or "Not specified")
        
        st.markdown("**Reminder preference:**")
        st.write(goal.get("reminder_preference") or "Not specified")
    
    with col2:
        st.markdown("**Auto-adaptation:**")
        auto_adapt = goal.get("auto_adapt", True)
        st.write("✅ Enabled" if auto_adapt else "❌ Disabled")

milestones, steps = db.list_plan(goal["id"])

# Show how the plan respects user preferences
if steps:
    st.markdown("## ⚡ Plan Optimization")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Energy Time:**")
        energy_time = goal.get("energy_time", "Not specified")
        st.write(f"📅 {energy_time}")
        if energy_time != "Not specified":
            st.write("✅ Activities scheduled during your peak energy")
    
    with col2:
        st.markdown("**Free Days:**")
        free_days = goal.get("free_days", "None")
        if free_days:
            st.write(f"🆓 {free_days}")
            st.write("✅ No activities scheduled on your free days")
        else:
            st.write("📅 No free days specified")
    
    with col3:
        st.markdown("**Weekly Time:**")
        weekly_time = goal.get("weekly_time", "Not specified")
        st.write(f"⏰ {weekly_time}")
        total_minutes = sum(step['estimate_minutes'] for step in steps)
        st.write(f"📊 Total plan: {total_minutes} min/week")
    
    st.write("---")

# Display milestones in a more organized way
st.markdown("## 🎯 Your Personalized Plan")
if milestones:
    for i, milestone in enumerate(milestones):
        with st.expander(f"**{milestone['seq']}. {milestone['title']}** - Due: {milestone['target_date']}", expanded=(i==0)):
            st.write(f"**Description:** {milestone.get('description', 'No description available')}")
            st.write(f"**Status:** {milestone['status'].title()}")
            
            # Show steps for this milestone
            milestone_steps = [s for s in steps if s['milestone_id'] == milestone['id']]
            if milestone_steps:
                st.write("**Steps:**")
                for step in milestone_steps:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"• **{step['title']}**")
                        # Show the ultra-explicit description in a clean format
                        description = step.get('description', '')
                        if description:
                            # Remove "EXACTLY:" prefix and format nicely
                            clean_description = description.replace('EXACTLY: ', '').replace(' - Break this down into specific, actionable steps.', '')
                            
                            # Split into sections for better readability
                            sections = clean_description.split('. ')
                            if len(sections) > 1:
                                # First section is the main instruction
                                main_instruction = sections[0]
                                st.write(f"📋 **What to do:** {main_instruction}")
                                
                                # Parse other sections
                                for section in sections[1:]:
                                    if 'TOTAL TIME:' in section:
                                        time_info = section.replace('TOTAL TIME:', '⏱️ **Duration:**')
                                        st.write(time_info)
                                    elif 'EFFORT LEVEL:' in section:
                                        effort_info = section.replace('EFFORT LEVEL:', '💪 **Effort:**')
                                        st.write(effort_info)
                                    elif 'SAFETY:' in section:
                                        safety_info = section.replace('SAFETY:', '⚠️ **Safety:**')
                                        st.write(safety_info)
                                    elif 'EQUIPMENT:' in section:
                                        equipment_info = section.replace('EQUIPMENT:', '🛠️ **Equipment:**')
                                        st.write(equipment_info)
                                    elif 'HYDRATION:' in section:
                                        hydration_info = section.replace('HYDRATION:', '💧 **Hydration:**')
                                        st.write(hydration_info)
                                    elif 'SUCCESS CRITERIA:' in section:
                                        success_info = section.replace('SUCCESS CRITERIA:', '✅ **Success looks like:**')
                                        st.write(success_info)
                                    elif 'WHAT TO EXPECT:' in section:
                                        expect_info = section.replace('WHAT TO EXPECT:', '🎯 **What to expect:**')
                                        st.write(expect_info)
                                    elif 'PROGRESSION:' in section:
                                        progress_info = section.replace('PROGRESSION:', '📈 **How this helps:**')
                                        st.write(progress_info)
                            else:
                                st.write(clean_description)
                    with col2:
                        st.write(f"{step['estimate_minutes']} min")
                    with col3:
                        st.write(f"{step['suggested_day']}")
            else:
                st.write("No steps assigned yet.")
else:
    st.info("No milestones yet. Complete onboarding to generate your personalized plan.")

# Show weekly schedule view
if steps:
    st.markdown("## 📅 Your Weekly Schedule")
    
    # Group steps by day
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    free_days = goal.get("free_days", "").split(",") if goal.get("free_days") else []
    free_days = [day.strip() for day in free_days if day.strip()]
    
    # Create columns for each day
    cols = st.columns(7)
    
    for i, day in enumerate(days_of_week):
        with cols[i]:
            if day in free_days:
                st.markdown(f"**{day}** 🆓")
                st.write("*Your free day*")
            else:
                st.markdown(f"**{day}**")
                day_steps = [s for s in steps if s['suggested_day'] == day]
                if day_steps:
                    for step in day_steps:
                        st.write(f"• **{step['title']}**")
                        st.write(f"  ⏱️ {step['estimate_minutes']} min")
                        st.write("---")
                else:
                    st.write("*No activities scheduled*")
    
    # Show detailed activity explanations below
    st.markdown("---")
    st.markdown("## 📋 Activity Guide")
    st.info("💡 **Below are detailed explanations of each activity with practical steps you can take.**")
    
    # Group all steps and show their detailed explanations
    all_activities = {}
    for step in steps:
        activity_name = step['title']
        if activity_name not in all_activities:
            all_activities[activity_name] = {
                'description': step.get('description', ''),
                'estimated_time': step['estimate_minutes'],
                'days': []
            }
        all_activities[activity_name]['days'].append(step['suggested_day'])
    
    for activity_name, details in all_activities.items():
        with st.expander(f"📌 {activity_name} ({details['estimated_time']} min)"):
            # Show which days this activity is scheduled
            days_str = ", ".join(details['days'])
            st.write(f"**📅 Scheduled on:** {days_str}")
            st.write(f"**⏱️ Time needed:** {details['estimated_time']} minutes")
            
            # Show the detailed description
            description = details['description']
            if description:
                # Clean up the description
                clean_description = description.replace('EXACTLY: ', '').replace(' - Break this down into specific, actionable steps.', '')
                st.write("**📋 How to do this:**")
                st.write(clean_description)
            else:
                st.write("**📋 How to do this:**")
                st.write("Detailed instructions will be provided when you start this activity.")
    
    # Show all steps in a summary table
    st.markdown("## 📋 All Action Steps")
    dfs = pd.DataFrame(steps)[["title","milestone_id","estimate_minutes","suggested_day","due_date","status"]]
    # Map milestone_id to milestone title for better readability
    milestone_map = {m['id']: m['title'] for m in milestones}
    dfs['milestone_title'] = dfs['milestone_id'].map(milestone_map)
    dfs = dfs[["title","milestone_title","estimate_minutes","suggested_day","due_date","status"]]
    dfs.columns = ["Step", "Milestone", "Duration", "Day", "Due Date", "Status"]
    st.dataframe(dfs, hide_index=True, use_container_width=True)
else:
    st.info("No steps yet. Complete onboarding to generate your personalized plan.")

st.markdown("### Recent Adaptations")
conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT checkin_timestamp, alignment_score, reason, change_summary FROM plan_adaptations WHERE goal_id=? ORDER BY id DESC LIMIT 10", (goal["id"],))
rows = [dict(r) for r in cur.fetchall()]
conn.close()

if rows:
    # Create a prettier DataFrame with formatted columns
    df_adaptations = pd.DataFrame(rows)
    
    # Format the timestamp column
    df_adaptations['checkin_timestamp'] = pd.to_datetime(df_adaptations['checkin_timestamp']).dt.strftime('%B %d, %Y at %I:%M %p')
    
    # Rename columns to be more user-friendly
    df_adaptations = df_adaptations.rename(columns={
        'checkin_timestamp': 'Check-in Date',
        'alignment_score': 'Alignment Score',
        'reason': 'Reason',
        'change_summary': 'Changes Made'
    })
    
    # Reorder columns for better readability
    df_adaptations = df_adaptations[['Check-in Date', 'Alignment Score', 'Reason', 'Changes Made']]
    
    st.dataframe(df_adaptations, hide_index=True, use_container_width=True)
else:
    st.info("No adaptations yet. Your plan will adapt based on your check-ins and progress.")
