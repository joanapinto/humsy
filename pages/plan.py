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
from data.supabase_manager import SupabaseManager
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

# Try Supabase REST API first, fallback to SQLite
try:
    db = SupabaseManager()
    user_email = get_user_email() or "me@example.com"
    goal = db.get_active_goal(user_email)
except Exception as e:
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
        # Handle missing seq column - use index + 1 as fallback
        seq_num = milestone.get('seq', i + 1)
        target_date = milestone.get('target_date', 'No date set')
        status = milestone.get('status', 'pending')
        
        with st.expander(f"**{seq_num}. {milestone['title']}** - Due: {target_date}", expanded=(i==0)):
            st.write(f"**Description:** {milestone.get('description', 'No description available')}")
            st.write(f"**Status:** {status.title()}")
            
            # Show steps for this milestone - handle missing milestone_id column
            milestone_steps = [s for s in steps if s.get('milestone_id') == milestone['id']]
            if milestone_steps:
                st.write("**Steps:**")
                for step in milestone_steps:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"• **{step['title']}**")
                        # Show the description in a clean, readable format
                        description = step.get('description', '')
                        if description:
                            # Clean up the description - remove any prefixes and make it readable
                            clean_description = description.replace('EXACTLY: ', '').replace(' - Break this down into specific, actionable steps.', '')
                            
                            # Display as a simple, clean instruction
                            st.write(f"📋 **How to do this:**")
                            st.write(clean_description)
                        else:
                            st.write("📋 **Instructions:** Detailed instructions will be provided when you start this activity.")
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
    st.markdown("## 📅 This Week's Schedule")
    
    # Get current week's activities (only show steps that are due this week)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    
    # Filter steps to show those due this week or with suggested days
    current_week_steps = []
    for step in steps:
        due_date_str = step.get('due_date', '')
        suggested_day = step.get('suggested_day', '')
        
        # Include if due this week
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if start_of_week <= due_date <= end_of_week:
                    current_week_steps.append(step)
                    continue
            except:
                pass
        
        # Include if has suggested day (even if no due date)
        if suggested_day and suggested_day.strip():
            current_week_steps.append(step)
            continue
        
        # If no due date or suggested day, include first few steps anyway
        if len(current_week_steps) < 5:  # Show up to 5 steps even without dates
            current_week_steps.append(step)
    
    # Group current week steps by day
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
                # Find steps for this day
                day_steps = [s for s in current_week_steps if s.get('suggested_day', '').strip() == day]
                
                # If no steps assigned to this day, assign some unassigned steps
                if not day_steps and current_week_steps:
                    unassigned_steps = [s for s in current_week_steps if not s.get('suggested_day', '').strip()]
                    if unassigned_steps and i < len(unassigned_steps):
                        day_steps = [unassigned_steps[i]]
                
                if day_steps:
                    for step in day_steps:
                        st.write(f"• **{step['title']}**")
                        estimate = step.get('estimate_minutes', 0)
                        if estimate > 0:
                            st.write(f"  ⏱️ {estimate} min")
                        st.write("---")
                else:
                    st.write("*No activities scheduled*")
    
    # Show detailed activity explanations below
    st.markdown("---")
    st.markdown("## 📋 This Week's Activity Guide")
    st.info("💡 **Below are detailed explanations of each activity scheduled for this week.**")
    
    # Group current week steps and show their detailed explanations
    current_week_activities = {}
    for step in current_week_steps:
        activity_name = step['title']
        if activity_name not in current_week_activities:
            current_week_activities[activity_name] = {
                'description': step.get('description', ''),
                'estimated_time': step['estimate_minutes'],
                'days': []
            }
        current_week_activities[activity_name]['days'].append(step['suggested_day'])
    
    if current_week_activities:
        for activity_name, details in current_week_activities.items():
            with st.expander(f"📌 {activity_name} ({details['estimated_time']} min)"):
                # Show which days this activity is scheduled this week
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
    else:
        st.info("No activities scheduled for this week. Check your plan timeline or regenerate your plan.")
    
    # Show all steps in a summary table
    st.markdown("## 📋 All Action Steps")
    if steps:
        # Create DataFrame with available columns only
        df_steps = pd.DataFrame(steps)
        available_columns = []
        required_columns = ["title", "milestone_id", "estimate_minutes", "suggested_day", "due_date", "status"]
        
        for col in required_columns:
            if col in df_steps.columns:
                available_columns.append(col)
        
        if available_columns:
            dfs = df_steps[available_columns]
        else:
            dfs = df_steps[["title"]]  # Fallback to just title
        
        # Map milestone_id to milestone title for better readability (if milestone_id exists)
        if "milestone_id" in df_steps.columns:
            milestone_map = {m['id']: m['title'] for m in milestones}
            dfs['milestone_title'] = dfs['milestone_id'].map(milestone_map)
            # Reorder columns to include milestone_title
            display_columns = ["title", "milestone_title"]
            for col in ["estimate_minutes", "suggested_day", "due_date", "status"]:
                if col in dfs.columns:
                    display_columns.append(col)
            dfs = dfs[display_columns]
            dfs.columns = ["Step", "Milestone"] + [col.replace("_", " ").title() for col in display_columns[2:]]
        else:
            # No milestone_id, just show available columns
            column_names = ["Step"] + [col.replace("_", " ").title() for col in available_columns[1:]]
            dfs.columns = column_names
        
        st.dataframe(dfs, hide_index=True, use_container_width=True)
else:
    st.info("No steps yet. Complete onboarding to generate your personalized plan.")

st.markdown("### Recent Adaptations")
# Handle both SQLite and Supabase databases
if hasattr(db, 'db_path') and db.db_path != "supabase://remote":
    # SQLite database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT checkin_timestamp, alignment_score, reason, change_summary FROM plan_adaptations WHERE goal_id=? ORDER BY id DESC LIMIT 10", (goal["id"],))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
else:
    # Supabase database - for now, show empty state
    # TODO: Implement plan_adaptations table in Supabase if needed
    rows = []

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
