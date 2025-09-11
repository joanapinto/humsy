import streamlit as st
import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to the Python path to find the data module
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from data.storage import save_user_profile, load_user_profile, save_checkin_data, load_checkin_data, load_mood_data
from data.database import DatabaseManager
from assistant.fallback import FallbackAssistant
from assistant.ai_service import AIService
from auth import require_beta_access, get_user_email

st.set_page_config(page_title="Humsy - Daily Check-in", page_icon="📝")

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

def generate_checkin_analysis(user_profile, checkin_data, mood_data, time_period, active_goal=None):
    """Generate AI-powered analysis of the check-in against user's goal and patterns"""
    try:
        # Initialize AI service
        ai_service = AIService()
        user_email = get_user_email()
        
        # Get recent patterns (last 7 days)
        recent_checkins = [c for c in checkin_data if (datetime.now() - datetime.fromisoformat(c['timestamp'])).days <= 7]
        recent_moods = [m for m in mood_data if (datetime.now() - datetime.fromisoformat(m['timestamp'])).days <= 7]
        
        # Use active_goal if available, otherwise fall back to user_profile
        if active_goal:
            user_goal = active_goal.get('title', 'Not specified')
            user_tone = 'Gentle & Supportive'  # Default tone for new system
            user_situation = active_goal.get('why_matters', 'Not specified')
            
            # Get weekly progress context
            # Use the same database connection as the main page
            try:
                from data.supabase_manager import SupabaseManager
                db = SupabaseManager()
            except Exception:
                from data.database import DatabaseManager
                db = DatabaseManager()
            milestones, steps = db.list_plan(active_goal['id'])
            
            # Calculate current week's progress
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            current_week_steps = []
            for step in steps:
                try:
                    due_date = datetime.fromisoformat(step['due_date']).date()
                    if week_start <= due_date <= week_end:
                        current_week_steps.append(step)
                except:
                    current_week_steps.append(step)
            
            completed_this_week = [s for s in current_week_steps if s.get('status') == 'completed']
            weekly_progress = (len(completed_this_week) / len(current_week_steps)) * 100 if current_week_steps else 0
            
            weekly_context = {
                "total_weekly_steps": len(current_week_steps),
                "completed_steps": len(completed_this_week),
                "progress_percentage": weekly_progress,
                "today_steps": [s for s in current_week_steps if s.get('suggested_day') == datetime.now().strftime('%A')]
            }
        else:
            user_goal = user_profile.get('goal', 'Not specified')
            user_tone = user_profile.get('tone', 'Gentle & Supportive')
            user_situation = user_profile.get('situation', 'Not specified')
            weekly_context = {}
        
        # Prepare context for AI analysis
        context = {
            "user_goal": user_goal,
            "user_tone": user_tone,
            "user_situation": user_situation,
            "time_period": time_period,
            "current_checkin": checkin_data[-1] if checkin_data else {},
            "weekly_progress": weekly_context,
            "recent_patterns": {
                "checkins_count": len(recent_checkins),
                "moods_count": len(recent_moods),
                "energy_levels": [c.get('energy_level', 'Unknown') for c in recent_checkins if 'energy_level' in c],
                "focus_areas": [c.get('focus_today', '') for c in recent_checkins if 'focus_today' in c],
                "accomplishments": [c.get('accomplishments', '') for c in recent_checkins if 'accomplishments' in c]
            }
        }
        
        # Create the analysis prompt
        weekly_progress_text = ""
        if context['weekly_progress']:
            wp = context['weekly_progress']
            weekly_progress_text = f"""
WEEKLY PROGRESS CONTEXT:
- Total steps this week: {wp['total_weekly_steps']}
- Completed steps: {wp['completed_steps']}
- Progress percentage: {wp['progress_percentage']:.0f}%
- Steps scheduled for today: {len(wp['today_steps'])}
"""

        prompt = f"""
You are a compassionate productivity coach analyzing a user's daily check-in. Your role is to provide emotional support while offering deep insights that help them align with their goals.

USER CONTEXT:
- Main Goal: {context['user_goal']}
- Communication Style: {context['user_tone']}
- Situation: {context['user_situation']}
- Check-in Time: {context['time_period']}
{weekly_progress_text}
CURRENT CHECK-IN:
{context['current_checkin']}

RECENT PATTERNS (Last 7 days):
- Check-ins: {context['recent_patterns']['checkins_count']} entries
- Moods tracked: {context['recent_patterns']['moods_count']} entries
- Energy levels: {', '.join(context['recent_patterns']['energy_levels'][:3])}
- Focus areas: {', '.join(context['recent_patterns']['focus_areas'][:3])}
- Accomplishments: {', '.join(context['recent_patterns']['accomplishments'][:3])}

ANALYSIS REQUEST:
Provide a personalized analysis that:
1. Acknowledges their current state with empathy
2. Connects their check-in to their main goal and weekly progress
3. Identifies patterns and opportunities for improvement
4. Offers specific, actionable suggestions based on their weekly plan
5. Maintains their preferred communication tone
6. Celebrates progress or offers encouragement based on weekly completion rate

Be warm, understanding, and deeply insightful. Focus on productivity and goal alignment while being emotionally supportive. Reference their weekly progress when relevant.
"""
        
        # Generate the analysis
        analysis = ai_service.generate_response(prompt, user_email)
        return analysis
        
    except Exception as e:
        # Fallback to a simple analysis if AI fails
        goal_text = active_goal.get('title', 'improve your focus and productivity') if active_goal else user_profile.get('goal', 'improve your focus and productivity')
        return f"Thank you for your {time_period} check-in! Your goal is to {goal_text}. Keep tracking your progress - every check-in brings you closer to your goals! 💪"

st.title("📝 Daily Check-in")

# Load user profile
user_profile = load_user_profile()

# Also check if user has an active goal (new onboarding system)
# Try Supabase REST API first, fallback to SQLite
try:
    from data.supabase_manager import SupabaseManager
    db = SupabaseManager()
    user_email = get_user_email() or "me@example.com"
    active_goal = db.get_active_goal(user_email)
except Exception as e:
    from data.database import DatabaseManager
    db = DatabaseManager()
    user_email = get_user_email() or "me@example.com"
    active_goal = db.get_active_goal(user_email)

if not user_profile and not active_goal:
    st.warning("Please complete onboarding first!")
    if st.button("🚀 Go to Onboarding", use_container_width=True):
        st.switch_page("pages/onboarding.py")
else:
    # Load user data for context
    user_email = get_user_email() or "me@example.com"
    mood_data = load_mood_data(user_email)
    checkin_data = load_checkin_data(user_email)
    
    # Initialize assistant for personalized insights (cached to avoid repeated AI calls)
    if 'fallback_assistant' not in st.session_state:
        assistant = FallbackAssistant(user_profile, mood_data, checkin_data)
        st.session_state.fallback_assistant = assistant
    else:
        assistant = st.session_state.fallback_assistant
    
    # Initialize AI service for task planning (cached to avoid repeated initialization)
    if 'ai_service' not in st.session_state:
        try:
            from assistant.ai_service import AIService
            ai_service = AIService()
            from auth import get_user_email
            user_email = get_user_email()
            st.session_state.ai_service = ai_service
            st.session_state.ai_service_available = True
            st.session_state.ai_user_email = user_email
        except Exception as e:
            st.warning(f"🤖 AI service initialization failed: {str(e)}")
            st.session_state.ai_service = None
            st.session_state.ai_service_available = False
            st.session_state.ai_user_email = None
    
    ai_service = st.session_state.get('ai_service')
    ai_service_available = st.session_state.get('ai_service_available', False)
    user_email = st.session_state.get('ai_user_email')
    
    # Determine time of day with more granular awareness
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    day_of_week = current_time.strftime("%A")
    
    # Enhanced time period detection
    if 5 <= current_hour < 12:
        time_period = "🕕 Morning"
        time_emoji = "🌅"
        time_context = "Start your day with intention"
    elif 12 <= current_hour < 18:
        time_period = "🕒 Afternoon"
        time_emoji = "☀️"
        time_context = "Midday energy and focus check"
    else:
        time_period = "🌙 Evening"
        time_emoji = "🌆"
        time_context = "Reflect on your day's progress"
    
    # Check if user has already checked in today
    today_checkins = [
        checkin for checkin in checkin_data 
        if datetime.fromisoformat(checkin['timestamp']).date() == current_time.date()
    ]
    
    # Get previous check-in context
    previous_checkin = None
    if today_checkins:
        today_checkins.sort(key=lambda x: x['timestamp'], reverse=True)
        previous_checkin = today_checkins[0]
    
    # Display enhanced header with context
    st.write(f"{time_emoji} **{time_period} Check-in**")
    st.write(f"**{day_of_week}** • {current_time.strftime('%B %d, %Y')} • {current_time.strftime('%I:%M %p')}")
    st.write(f"*{time_context}*")
    
    # Show goal reminder
    goal_text = active_goal.get('title', 'Improve focus and productivity') if active_goal else user_profile.get('goal', 'Improve focus and productivity')
    st.write(f"🎯 **Your goal:** {goal_text}")
    
    # Show today's focus steps prominently at the top
    if active_goal:
        milestones, steps = db.list_plan(active_goal['id'])
        if steps:
            # Get today's steps based on suggested_day (not due_date)
            today_name = current_time.strftime('%A')
            today_steps = [s for s in steps if s.get('suggested_day') == today_name]
            
            # Also get current week's steps for the weekly view
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            current_week_steps = []
            for step in steps:
                try:
                    due_date = datetime.fromisoformat(step['due_date']).date()
                    if week_start <= due_date <= week_end:
                        current_week_steps.append(step)
                except:
                    # If no due_date or invalid date, include step if it's scheduled for this week
                    if step.get('suggested_day') in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                        current_week_steps.append(step)
            
            if today_steps:
                st.markdown("### 🎯 Today's Focus Steps")
                st.write(f"**You have {len(today_steps)} step(s) scheduled for today:**")
                
                completed_today = []
                total_minutes = 0
                
                for i, step in enumerate(today_steps):
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        # Status indicator
                        if step.get('status') == 'completed':
                            st.write("✅")
                        else:
                            if st.checkbox("Complete", key=f"complete_{step['id']}", value=False, label_visibility="collapsed"):
                                completed_today.append(step['id'])
                    
                    with col2:
                        # Step details
                        milestone_title = next((m['title'] for m in milestones if m['id'] == step['milestone_id']), 'Unknown')
                        st.write(f"**{step['title']}**")
                        st.write(f"*{milestone_title}* • {step['estimate_minutes']} min")
                        
                        # Show clean description
                        description = step.get('description', '')
                        if description:
                            clean_description = description.replace('EXACTLY: ', '').replace(' - Break this down into specific, actionable steps.', '')
                            main_instruction = clean_description.split('. ')[0]
                            st.write(f"📋 {main_instruction}")
                    
                    with col3:
                        # Time estimate
                        st.write(f"⏱️ {step['estimate_minutes']}m")
                        total_minutes += step['estimate_minutes']
                    
                    st.write("---")
                
                # Progress summary
                completed_count = len([s for s in today_steps if s.get('status') == 'completed'])
                progress_percentage = (completed_count / len(today_steps)) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Steps Today", f"{completed_count}/{len(today_steps)}")
                with col2:
                    st.metric("Progress", f"{progress_percentage:.0f}%")
                with col3:
                    st.metric("Time Needed", f"{total_minutes} min")
                
                # Progress bar
                st.progress(progress_percentage / 100)
                
                # Completion button
                if completed_today:
                    if st.button("🎉 Mark Selected as Complete", type="primary", use_container_width=True):
                        for step_id in completed_today:
                            db.mark_step_status(step_id, "completed")
                        st.success(f"🎉 Great job! Marked {len(completed_today)} step(s) as complete!")
                        st.rerun()
                
                # Daily motivation based on progress
                if progress_percentage == 100:
                    st.success("🌟 **Perfect day!** You've completed all your planned steps!")
                elif progress_percentage >= 75:
                    st.success("🔥 **Almost there!** You're doing great today!")
                elif progress_percentage >= 50:
                    st.info("💪 **Good progress!** Keep the momentum going!")
                elif progress_percentage >= 25:
                    st.warning("📈 **Getting started!** Every step counts toward your goal!")
                else:
                    st.info("🚀 **Ready to tackle today's challenges!** You've got this!")
                    
                st.write("---")
            else:
                st.info("📅 **No specific steps scheduled for today.**")
                st.write("This might be a rest day or you can choose to work on any step from your weekly plan!")
                st.write("---")
    
    # Show current week's steps and progress
    if active_goal:
        milestones, steps = db.list_plan(active_goal['id'])
        if steps:
            # Get current week's steps (steps due this week)
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            current_week_steps = []
            for step in steps:
                try:
                    due_date = datetime.fromisoformat(step['due_date']).date()
                    if week_start <= due_date <= week_end:
                        current_week_steps.append(step)
                except:
                    # If date parsing fails, include the step anyway
                    current_week_steps.append(step)
            
            if current_week_steps:
                st.markdown("### 📅 This Week's Action Steps")
                
                # Group steps by day
                steps_by_day = {}
                for step in current_week_steps:
                    day = step.get('suggested_day', 'Monday')
                    if day not in steps_by_day:
                        steps_by_day[day] = []
                    steps_by_day[day].append(step)
                
                # Show steps for each day
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                    if day in steps_by_day:
                        day_steps = steps_by_day[day]
                        with st.expander(f"📅 **{day}** ({len(day_steps)} steps)", expanded=(day == current_time.strftime('%A'))):
                            for step in day_steps:
                                # Check if step is completed
                                status_icon = "✅" if step.get('status') == 'completed' else "⏳"
                                st.write(f"{status_icon} **{step['title']}** ({step['estimate_minutes']} min)")
                                
                                # Show clean description
                                description = step.get('description', '')
                                if description:
                                    # Clean up the description
                                    clean_description = description.replace('EXACTLY: ', '').replace(' - Break this down into specific, actionable steps.', '')
                                    main_instruction = clean_description.split('. ')[0]
                                    st.write(f"   📋 {main_instruction}")
                                
                                # Show milestone context
                                milestone_title = next((m['title'] for m in milestones if m['id'] == step['milestone_id']), 'Unknown')
                                st.write(f"   🎯 *{milestone_title}*")
                                st.write("---")
                
                # Show weekly progress summary
                completed_steps = [s for s in current_week_steps if s.get('status') == 'completed']
                progress_percentage = (len(completed_steps) / len(current_week_steps)) * 100 if current_week_steps else 0
                
                st.markdown("### 📊 Weekly Progress")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Steps Completed", f"{len(completed_steps)}/{len(current_week_steps)}")
                with col2:
                    st.metric("Progress", f"{progress_percentage:.0f}%")
                with col3:
                    total_minutes = sum(s['estimate_minutes'] for s in completed_steps)
                    st.metric("Time Invested", f"{total_minutes} min")
                
                # Progress bar
                st.progress(progress_percentage / 100)
                
                if progress_percentage == 100:
                    st.success("🎉 Amazing! You've completed all your weekly steps!")
                elif progress_percentage >= 75:
                    st.success("🔥 Great progress! You're almost there!")
                elif progress_percentage >= 50:
                    st.info("💪 Good progress! Keep going!")
                elif progress_percentage >= 25:
                    st.warning("📈 You're getting started! Every step counts.")
                else:
                    st.info("🚀 Ready to tackle this week's challenges!")
                
    
    # Show previous check-in context if available
    if previous_checkin:
        time_period = previous_checkin.get('time_period', 'Unknown')
        if time_period and time_period != 'unknown':
            time_period_display = time_period.title()
        else:
            time_period_display = "Previous"
        st.info(f"📝 **Previous check-in today:** {time_period_display} at {datetime.fromisoformat(previous_checkin['timestamp']).strftime('%I:%M %p')}")
    
    # Time-aware encouragement (cached to avoid repeated AI calls)
    today = datetime.now().strftime('%Y-%m-%d')
    if ('daily_encouragement' not in st.session_state or 
        st.session_state.get('encouragement_date') != today):
        encouragement = assistant.get_daily_encouragement()
        st.session_state.daily_encouragement = encouragement
        st.session_state.encouragement_date = today
    else:
        encouragement = st.session_state.daily_encouragement
    st.success(encouragement)
    
    # Simple form without progress tracking
    

    
    with st.form("daily_checkin_form"):
        # Set default mode to always provide task planning help
        checkin_mode = "🎯 Get help planning my day"
        
        # Morning flow (5 AM - 12 PM)
        if 5 <= current_hour < 12:
            # Get yesterday's evening check-in for context
            yesterday_evening = None
            if checkin_data:
                yesterday = current_time.date() - timedelta(days=1)
                yesterday_checkins = [
                    checkin for checkin in checkin_data
                    if datetime.fromisoformat(checkin['timestamp']).date() == yesterday
                    and checkin.get('time_period') == 'evening'
                ]
                if yesterday_checkins:
                    yesterday_evening = yesterday_checkins[0]
            
            # Show yesterday's context if available
            if yesterday_evening:
                st.info(f"📝 **Yesterday's evening:** You felt {yesterday_evening.get('current_feeling', 'N/A')} and accomplished: {yesterday_evening.get('accomplishments', 'N/A')[:50]}...")
            
            # Step 1: Goals & Energy
            st.subheader("🎯 Step 1: Goals & Energy")
            
            # Time-aware sleep question
            if current_hour < 8:
                sleep_context = "How did you sleep last night?"
            else:
                sleep_context = "How did you sleep?"
            
            sleep_quality = st.selectbox(
                f"😴 {sleep_context}",
                ["Excellent", "Good", "Okay", "Poor", "Terrible"]
            )
            
                    # User answered sleep question
            
            # Suggest focus based on previous patterns
            focus_suggestion = ""
            if previous_checkin and previous_checkin.get('focus_today'):
                focus_suggestion = f"Previous focus: {previous_checkin['focus_today']}"
            
            focus_today = st.text_area(
                "🎯 What do you want to focus on today?",
                placeholder="e.g., Complete project proposal, Exercise for 30 minutes, Read 20 pages",
                help=focus_suggestion if focus_suggestion else "Be specific about what you want to accomplish"
            )
            
            # Time-aware energy question
            if current_hour < 7:
                energy_context = "How's your morning energy?"
            elif current_hour < 10:
                energy_context = "How's your energy now?"
            else:
                energy_context = "What's your energy like?"
            
            energy_level = st.selectbox(
                f"🔋 {energy_context}",
                ["High", "Good", "Moderate", "Low", "Very low"]
            )
            
                    # User answered energy question
            
            # Morning wellness reminder
            if energy_level in ["Low", "Very low"]:
                st.warning("💡 **Tip:** Consider a short walk, stretching, or a healthy breakfast to boost your energy!")
            
            # Step 2: Additional Context
            st.subheader("💭 Step 2: Additional Context")
            
            # Current feeling
            current_feeling = st.selectbox(
                "😊 How are you feeling right now?",
                ["Excited", "Good", "Okay", "Tired", "Stressed", "Focused"]
            )
            
            # Optional notes field
            additional_notes = st.text_area(
                "📝 Any additional thoughts? (Optional)",
                placeholder="e.g., Feeling excited about today, Need to remember to call mom, Weather is affecting my mood",
                help="Share any context that might help with your check-in"
            )
            
            submitted = st.form_submit_button("💾 Save Morning Check-in")
            
            if submitted:
                checkin_data = {
                    "timestamp": datetime.now().isoformat(),
                    "time_period": "morning",
                    "sleep_quality": sleep_quality,
                    "focus_today": focus_today,
                    "energy_level": energy_level,
                    "current_feeling": current_feeling,
                    "additional_notes": additional_notes,
                    "day_of_week": day_of_week,
                    "checkin_hour": current_hour
                }
                # Save the check-in data to persistent storage
                user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)
                st.success("✅ Morning check-in saved successfully!")
                
                # After saving today's check-in, compute plan alignment:
                db = DatabaseManager()
                user_email = get_user_email() or "me@example.com"
                goal = db.get_active_goal(user_email)
                if goal:
                    st.subheader("📌 Today's Plan (Goal Alignment)")
                    ai = ai_service
                    today_str = datetime.now().date().isoformat()
                    candidates = db.get_today_candidates(user_email, today_str)
                    # build context (extend with your mood history if available)
                    context = {
                        "goal": goal,
                        "steps_today_candidates": candidates,
                        "checkin": {
                            "timestamp": datetime.now().isoformat(),
                            # include any mood/energy fields you capture already:
                            "energy_level": energy_level,
                            "focus_today": focus_today,
                            "current_feeling": current_feeling,
                        }
                    }
                    choice = ai.choose_today_steps(context, user_email) or {}
                    alignment = int(choice.get("alignment_score", 60))
                    selected = choice.get("today_steps", [])
                    adjustments = choice.get("adjustments", [])
                    why = choice.get("why","Keeping it small to maintain momentum.")

                    colA, colB = st.columns([2,1])
                    with colA:
                        st.write("**Suggested steps for today:**")
                        checked = []
                        for s in selected:
                            if st.checkbox(s["title"], key=f"step_{s['step_id']}"):
                                checked.append(s["step_id"])
                        if checked:
                            # Store completed steps in session state for processing outside form
                            st.session_state['pending_completions'] = checked
                            st.info(f"✅ {len(checked)} step(s) selected for completion")
                    with colB:
                        hue = "🟢" if alignment >= 70 else ("🟡" if alignment >= 40 else "🔴")
                        st.metric("Alignment", f"{hue} {alignment}%")
                        with st.expander("Why this today?"):
                            st.write(why)
                            if adjustments:
                                st.caption("Adjustments: " + "; ".join(adjustments))

                    # Skip reasons + Adaptation loop
                    skipped = [s for s in selected if not st.session_state.get(f"step_{s['step_id']}")]
                    if skipped:
                        st.divider()
                        st.caption("Skipped a step? Tell us why (helps adapt your plan):")
                        reason = st.selectbox("Reason", ["Low energy","No time","Confusing next step","Fear/avoidance","External interruption","Other"])
                        # Store skip data in session state for processing outside form
                        st.session_state['pending_skips'] = {
                            'skipped': skipped,
                            'reason': reason,
                            'candidates': candidates
                        }
                else:
                    st.info("Define a main goal in Onboarding to get aligned daily steps.")
                
                # Completion celebration
                st.success("🎉 **Check-in Complete!** You've successfully completed your morning check-in!")
                
                # Show completion summary
                st.write("---")
                st.subheader("📋 Check-in Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Time Period:** {time_period}")
                    st.write(f"**Sleep Quality:** {sleep_quality}")
                    st.write(f"**Energy Level:** {energy_level}")
                with col2:
                    st.write(f"**Focus Today:** {focus_today[:50]}{'...' if len(focus_today) > 50 else ''}")
                    if additional_notes:
                        st.write(f"**Notes:** {additional_notes[:50]}{'...' if len(additional_notes) > 50 else ''}")
                
                # AI Analysis
                st.write("---")
                st.subheader("🤖 Personalized Insights")
                with st.spinner("🧠 Analyzing your check-in against your goals and patterns..."):
                    analysis = generate_checkin_analysis(user_profile, checkin_data, mood_data, "morning", active_goal)
                    st.write(analysis)
                
                # Feedback prompt after successful check-in
                st.write("---")
                st.info("💬 **How was this check-in experience?**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.radio("How was this check-in?", ["👍 Great!", "🤔 Could be better", "📝 Share detailed feedback"], key="feedback_morning", horizontal=True):
                        st.session_state['morning_feedback'] = st.session_state['feedback_morning']
                with col2:
                    st.write("")  # Empty space
                with col3:
                    st.write("")  # Empty space
                
                # Generate smart task plan if user requested help
                if checkin_mode == "🎯 Get help planning my day":
                    st.subheader("🎯 Your Smart Task Plan")
                    
                    # Prepare current check-in data for AI
                    current_checkin_data = {
                        'time_period': 'morning',
                        'sleep_quality': sleep_quality,
                        'energy_level': energy_level,
                        'focus_today': focus_today,
                        'current_feeling': current_feeling,
                        'day_progress': 'Not applicable for morning'
                    }
                    
                    # Generate AI-powered task plan
                    if ai_service_available and ai_service:
                        task_plan = ai_service.generate_ai_task_plan(user_profile, current_checkin_data, mood_data, user_email)
                        
                        # Fallback to rule-based plan if AI fails
                        if not task_plan:
                            st.info("🤖 AI task planning unavailable, using smart fallback system...")
                            task_plan = assistant.generate_smart_task_plan(checkin_data, focus_today)
                        else:
                            st.success("🤖 AI-powered personalized plan generated!")
                    else:
                        st.info("🤖 AI service not available, using smart fallback system...")
                        task_plan = assistant.generate_smart_task_plan(checkin_data, focus_today)
                    
                    # Display tasks
                    st.write("**📋 Recommended Tasks:**")
                    for i, task in enumerate(task_plan['tasks'], 1):
                        st.write(f"{i}. {task}")
                    
                    # Display recommendations
                    if task_plan['recommendations']:
                        st.write("**💡 Smart Recommendations:**")
                        for rec in task_plan['recommendations']:
                            st.info(rec)
                    
                    # Display estimated duration
                    st.write(f"**⏰ Estimated Duration:** {task_plan['estimated_duration']}")
                    
                    # Add task completion tracking
                    st.write("**✅ Task Completion:**")
                    task_completion = {}
                    for task in task_plan['tasks']:
                        task_completion[task] = st.checkbox(f"Complete: {task}")
                    
                    # Save task plan to user data
                    checkin_data['task_plan'] = task_plan
                    checkin_data['task_completion'] = task_completion
                    user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)
        
        # Afternoon flow (12 PM - 6 PM)
        elif 12 <= current_hour < 18:
            # Get morning check-in for context
            morning_checkin = None
            if today_checkins:
                morning_checkins = [
                    checkin for checkin in today_checkins
                    if checkin.get('time_period') == 'morning'
                ]
                if morning_checkins:
                    morning_checkin = morning_checkins[0]
            
            # Show morning context if available
            if morning_checkin:
                st.info(f"📝 **This morning:** You planned to focus on: {morning_checkin.get('focus_today', 'N/A')} and your energy was {morning_checkin.get('energy_level', 'N/A')}")
            
            # Step 1: Goals & Energy
            st.subheader("🎯 Step 1: Goals & Energy")
            
            # Energy level for afternoon
            energy_level = st.selectbox(
                "🔋 How's your energy now?",
                ["High", "Good", "Moderate", "Low", "Very low"]
            )
            
            # Focus today (what they're focusing on)
            focus_today = st.text_area(
                "🎯 What are you focusing on today?",
                placeholder="e.g., Work project, Exercise, Reading, Social activities",
                help="What's your main focus or priority today?"
            )
            
            # Current feeling
            current_feeling = st.selectbox(
                "😊 How are you feeling right now?",
                ["Motivated", "Good", "Okay", "Tired", "Stressed"]
            )
            
            # Time-aware progress question
            if current_hour < 14:
                progress_context = "How's your morning progress?"
            elif current_hour < 16:
                progress_context = "How's the day going so far?"
            else:
                progress_context = "How's your afternoon going?"
            
            day_progress = st.selectbox(
                f"📊 {progress_context}",
                ["Great", "Good", "Okay", "Challenging", "Difficult"]
            )
            
                    # User answered progress question
            
            # Suggest plan adjustments based on progress
            if day_progress in ["Challenging", "Difficult"]:
                st.warning("💡 **Tip:** Consider breaking down your tasks into smaller, more manageable steps!")
            
            adjust_plan = st.text_area(
                "🔄 Want to adjust your plan? (Optional)",
                placeholder="e.g., Move difficult tasks to tomorrow, Take a longer break, Focus on one priority",
                help="What would help you feel more productive?"
            )
            
            # Time-aware break suggestion
            if current_hour >= 15:
                break_context = "☕ Take a break? (It's getting late in the day)"
            else:
                break_context = "☕ Take a break?"
            
            take_break = st.radio(
                break_context,
                ["Yes, I need a break", "No, I'm in the zone", "Maybe later"]
            )
            
            # User answered break question
            
            # Break encouragement
            if take_break == "Yes, I need a break":
                st.info("💡 **Great choice!** Taking breaks helps maintain focus and prevents burnout.")
            elif take_break == "No, I'm in the zone":
                st.success("🚀 **Flow state!** Enjoy your productive momentum!")
            
            # Step 2: Additional Context
            st.subheader("💭 Step 2: Additional Context")
            
            # Optional notes field
            additional_notes = st.text_area(
                "📝 Any additional thoughts? (Optional)",
                placeholder="e.g., Need to adjust my schedule, Feeling more focused now, Should take a walk",
                help="Share any context that might help with your check-in"
            )
            
            submitted = st.form_submit_button("💾 Save Afternoon Check-in")
            
            if submitted:
                checkin_data = {
                    "timestamp": datetime.now().isoformat(),
                    "time_period": "afternoon",
                    "energy_level": energy_level,
                    "focus_today": focus_today,
                    "current_feeling": current_feeling,
                    "day_progress": day_progress,
                    "adjust_plan": adjust_plan,
                    "take_break": take_break,
                    "additional_notes": additional_notes,
                    "day_of_week": day_of_week,
                    "checkin_hour": current_hour
                }
                # Save the check-in data to persistent storage
                user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)
                st.success("✅ Afternoon check-in saved successfully!")
                
                # After saving today's check-in, compute plan alignment:
                db = DatabaseManager()
                user_email = get_user_email() or "me@example.com"
                goal = db.get_active_goal(user_email)
                if goal:
                    st.subheader("📌 Today's Plan (Goal Alignment)")
                    ai = ai_service
                    today_str = datetime.now().date().isoformat()
                    candidates = db.get_today_candidates(user_email, today_str)
                    # build context (extend with your mood history if available)
                    context = {
                        "goal": goal,
                        "steps_today_candidates": candidates,
                        "checkin": {
                            "timestamp": datetime.now().isoformat(),
                            # include any mood/energy fields you capture already:
                            "energy_level": energy_level,
                            "focus_today": focus_today,
                            "current_feeling": current_feeling,
                        }
                    }
                    choice = ai.choose_today_steps(context, user_email) or {}
                    alignment = int(choice.get("alignment_score", 60))
                    selected = choice.get("today_steps", [])
                    adjustments = choice.get("adjustments", [])
                    why = choice.get("why","Keeping it small to maintain momentum.")

                    colA, colB = st.columns([2,1])
                    with colA:
                        st.write("**Suggested steps for today:**")
                        checked = []
                        for s in selected:
                            if st.checkbox(s["title"], key=f"step_{s['step_id']}"):
                                checked.append(s["step_id"])
                        if checked:
                            # Store completed steps in session state for processing outside form
                            st.session_state['pending_completions'] = checked
                            st.info(f"✅ {len(checked)} step(s) selected for completion")
                    with colB:
                        hue = "🟢" if alignment >= 70 else ("🟡" if alignment >= 40 else "🔴")
                        st.metric("Alignment", f"{hue} {alignment}%")
                        with st.expander("Why this today?"):
                            st.write(why)
                            if adjustments:
                                st.caption("Adjustments: " + "; ".join(adjustments))

                    # Skip reasons + Adaptation loop
                    skipped = [s for s in selected if not st.session_state.get(f"step_{s['step_id']}")]
                    if skipped:
                        st.divider()
                        st.caption("Skipped a step? Tell us why (helps adapt your plan):")
                        reason = st.selectbox("Reason", ["Low energy","No time","Confusing next step","Fear/avoidance","External interruption","Other"])
                        # Store skip data in session state for processing outside form
                        st.session_state['pending_skips'] = {
                            'skipped': skipped,
                            'reason': reason,
                            'candidates': candidates
                        }
                else:
                    st.info("Define a main goal in Onboarding to get aligned daily steps.")
                
                # Completion celebration
                st.success("🎉 **Check-in Complete!** You've successfully completed your afternoon check-in!")
                
                # Show completion summary
                st.write("---")
                st.subheader("📋 Check-in Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Time Period:** {time_period}")
                    st.write(f"**Day Progress:** {day_progress}")
                    st.write(f"**Break Decision:** {take_break}")
                with col2:
                    if adjust_plan:
                        st.write(f"**Plan Adjustment:** {adjust_plan[:50]}{'...' if len(adjust_plan) > 50 else ''}")
                    if additional_notes:
                        st.write(f"**Notes:** {additional_notes[:50]}{'...' if len(additional_notes) > 50 else ''}")
                
                # AI Analysis
                st.write("---")
                st.subheader("🤖 Personalized Insights")
                with st.spinner("🧠 Analyzing your progress against your goals and patterns..."):
                    analysis = generate_checkin_analysis(user_profile, checkin_data, mood_data, "afternoon", active_goal)
                    st.write(analysis)
                
                # Generate smart task plan if user requested help
                if checkin_mode == "🎯 Get help planning my day":
                    st.subheader("🎯 Your Smart Afternoon Plan")
                    
                    # Prepare current check-in data for AI
                    current_checkin_data = {
                        'time_period': 'afternoon',
                        'sleep_quality': 'Not applicable for afternoon',
                        'energy_level': energy_level,
                        'focus_today': focus_today,
                        'current_feeling': current_feeling,
                        'day_progress': day_progress
                    }
                    
                    # Generate AI-powered task plan
                    if ai_service_available and ai_service:
                        task_plan = ai_service.generate_ai_task_plan(user_profile, current_checkin_data, mood_data, user_email)
                        
                        # Fallback to rule-based plan if AI fails
                        if not task_plan:
                            st.info("🤖 AI task planning unavailable, using smart fallback system...")
                            task_plan = assistant.generate_smart_task_plan(checkin_data)
                        else:
                            st.success("🤖 AI-powered personalized plan generated!")
                    else:
                        st.info("🤖 AI service not available, using smart fallback system...")
                        task_plan = assistant.generate_smart_task_plan(checkin_data)
                    
                    # Display tasks
                    st.write("**📋 Recommended Tasks:**")
                    for i, task in enumerate(task_plan['tasks'], 1):
                        st.write(f"{i}. {task}")
                    
                    # Display recommendations
                    if task_plan['recommendations']:
                        st.write("**💡 Smart Recommendations:**")
                        for rec in task_plan['recommendations']:
                            st.info(rec)
                    
                    # Display estimated duration
                    st.write(f"**⏰ Estimated Duration:** {task_plan['estimated_duration']}")
                    
                    # Add task completion tracking
                    st.write("**✅ Task Completion:**")
                    task_completion = {}
                    for task in task_plan['tasks']:
                        task_completion[task] = st.checkbox(f"Complete: {task}")
                    
                    # Save task plan to user data
                    checkin_data['task_plan'] = task_plan
                    checkin_data['task_completion'] = task_completion
                    user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)
        
        # Evening flow (6 PM - 5 AM)
        else:
            # Get today's previous check-ins for context
            morning_checkin = None
            afternoon_checkin = None
            
            if today_checkins:
                for checkin in today_checkins:
                    if checkin.get('time_period') == 'morning':
                        morning_checkin = checkin
                    elif checkin.get('time_period') == 'afternoon':
                        afternoon_checkin = checkin
            
            # Show today's journey
            if morning_checkin or afternoon_checkin:
                journey_summary = "📝 **Today's journey:** "
                if morning_checkin:
                    journey_summary += f"Started with focus on '{morning_checkin.get('focus_today', 'N/A')}' "
                if afternoon_checkin:
                    journey_summary += f"• Afternoon was {afternoon_checkin.get('day_progress', 'N/A')}"
                st.info(journey_summary)
            
            # Step 1: Goals & Energy
            st.subheader("🎯 Step 1: Goals & Energy")
            
            # Energy level for evening
            energy_level = st.selectbox(
                "🔋 How's your energy now?",
                ["High", "Good", "Moderate", "Low", "Very low"]
            )
            
            # Focus today (what they focused on)
            focus_today = st.text_area(
                "🎯 What did you focus on today?",
                placeholder="e.g., Work project, Exercise, Reading, Social activities",
                help="What was your main focus or priority today?"
            )
            
            # Time-aware accomplishment question
            if current_hour < 20:
                accomplishment_context = "What did you accomplish today?"
            else:
                accomplishment_context = "What did you accomplish today? (It's getting late)"
            
            accomplishments = st.text_area(
                f"🏆 {accomplishment_context}",
                placeholder="e.g., Completed project proposal, Exercised for 30 minutes, Read 20 pages",
                help="Celebrate your wins, no matter how small!"
            )
            
            # User entered accomplishments
            
            challenges = st.text_area(
                "🚧 Any challenges? (Optional)",
                placeholder="e.g., Had trouble focusing, Felt overwhelmed, Technical difficulties",
                help="Understanding challenges helps improve future days"
            )
            
            # Time-aware feeling question
            if current_hour < 22:
                feeling_context = "How do you feel now?"
            else:
                feeling_context = "How do you feel now? (Getting ready for bed)"
            
            current_feeling = st.selectbox(
                f"😊 {feeling_context}",
                ["Accomplished", "Good", "Okay", "Tired", "Stressed"]
            )
            
            # User answered feeling question
            
            # Evening wellness tips
            if current_feeling in ["Tired", "Stressed"]:
                st.warning("💡 **Evening tip:** Consider a relaxing activity like reading, meditation, or gentle stretching to wind down.")
            elif current_feeling == "Accomplished":
                st.success("🎉 **Great job today!** You should be proud of your accomplishments!")
            
            # Step 2: Additional Context
            st.subheader("💭 Step 2: Additional Context")
            
            # Tomorrow preparation
            if current_hour < 22:
                tomorrow_focus = st.text_area(
                    "🌙 What would you like to focus on tomorrow? (Optional)",
                    placeholder="e.g., Continue with the project, Exercise in the morning, Call a friend",
                    help="Planning ahead can help you start tomorrow with intention"
                )
            else:
                tomorrow_focus = st.text_area(
                    "🌙 Any thoughts for tomorrow? (Optional)",
                    placeholder="e.g., Need to remember to..., Looking forward to..., Should prepare for...",
                    help="Capture any thoughts before bed"
                )
            
            submitted = st.form_submit_button("💾 Save Evening Check-in")
            
            if submitted:
                checkin_data = {
                    "timestamp": datetime.now().isoformat(),
                    "time_period": "evening",
                    "energy_level": energy_level,
                    "focus_today": focus_today,
                    "accomplishments": accomplishments,
                    "challenges": challenges,
                    "current_feeling": current_feeling,
                    "tomorrow_focus": tomorrow_focus,
                    "day_of_week": day_of_week,
                    "checkin_hour": current_hour
                }
                # Save the check-in data to persistent storage
                user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)
                st.success("✅ Evening check-in saved successfully!")
                
                # After saving today's check-in, compute plan alignment:
                db = DatabaseManager()
                user_email = get_user_email() or "me@example.com"
                goal = db.get_active_goal(user_email)
                if goal:
                    st.subheader("📌 Today's Plan (Goal Alignment)")
                    ai = ai_service
                    today_str = datetime.now().date().isoformat()
                    candidates = db.get_today_candidates(user_email, today_str)
                    # build context (extend with your mood history if available)
                    context = {
                        "goal": goal,
                        "steps_today_candidates": candidates,
                        "checkin": {
                            "timestamp": datetime.now().isoformat(),
                            # include any mood/energy fields you capture already:
                            "energy_level": energy_level,
                            "focus_today": focus_today,
                            "current_feeling": current_feeling,
                        }
                    }
                    choice = ai.choose_today_steps(context, user_email) or {}
                    alignment = int(choice.get("alignment_score", 60))
                    selected = choice.get("today_steps", [])
                    adjustments = choice.get("adjustments", [])
                    why = choice.get("why","Keeping it small to maintain momentum.")

                    colA, colB = st.columns([2,1])
                    with colA:
                        st.write("**Suggested steps for today:**")
                        checked = []
                        for s in selected:
                            if st.checkbox(s["title"], key=f"step_{s['step_id']}"):
                                checked.append(s["step_id"])
                        if checked:
                            # Store completed steps in session state for processing outside form
                            st.session_state['pending_completions'] = checked
                            st.info(f"✅ {len(checked)} step(s) selected for completion")
                    with colB:
                        hue = "🟢" if alignment >= 70 else ("🟡" if alignment >= 40 else "🔴")
                        st.metric("Alignment", f"{hue} {alignment}%")
                        with st.expander("Why this today?"):
                            st.write(why)
                            if adjustments:
                                st.caption("Adjustments: " + "; ".join(adjustments))

                    # Skip reasons + Adaptation loop
                    skipped = [s for s in selected if not st.session_state.get(f"step_{s['step_id']}")]
                    if skipped:
                        st.divider()
                        st.caption("Skipped a step? Tell us why (helps adapt your plan):")
                        reason = st.selectbox("Reason", ["Low energy","No time","Confusing next step","Fear/avoidance","External interruption","Other"])
                        # Store skip data in session state for processing outside form
                        st.session_state['pending_skips'] = {
                            'skipped': skipped,
                            'reason': reason,
                            'candidates': candidates
                        }
                else:
                    st.info("Define a main goal in Onboarding to get aligned daily steps.")
                
                # Completion celebration
                st.success("🎉 **Check-in Complete!** You've successfully completed your evening check-in!")
                
                # Show completion summary
                st.write("---")
                st.subheader("📋 Check-in Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Time Period:** {time_period}")
                    st.write(f"**Current Feeling:** {current_feeling}")
                    st.write(f"**Accomplishments:** {accomplishments[:50]}{'...' if len(accomplishments) > 50 else ''}")
                with col2:
                    if challenges:
                        st.write(f"**Challenges:** {challenges[:50]}{'...' if len(challenges) > 50 else ''}")
                    if tomorrow_focus:
                        st.write(f"**Tomorrow's Focus:** {tomorrow_focus[:50]}{'...' if len(tomorrow_focus) > 50 else ''}")
                
                # AI Analysis
                st.write("---")
                st.subheader("🤖 Personalized Insights")
                with st.spinner("🧠 Analyzing your day against your goals and patterns..."):
                    analysis = generate_checkin_analysis(user_profile, checkin_data, mood_data, "evening", active_goal)
                    st.write(analysis)
                
                # Generate smart task plan if user requested help
                if checkin_mode == "🎯 Get help planning my day":
                    st.subheader("🌙 Your Smart Evening Plan")
                    
                    # Prepare current check-in data for AI
                    current_checkin_data = {
                        'time_period': 'evening',
                        'sleep_quality': 'Not applicable for evening',
                        'energy_level': energy_level,
                        'focus_today': focus_today,
                        'current_feeling': current_feeling,
                        'day_progress': 'Not applicable for evening'
                    }
                    
                    # Generate AI-powered task plan
                    if ai_service_available and ai_service:
                        task_plan = ai_service.generate_ai_task_plan(user_profile, current_checkin_data, mood_data, user_email)
                        
                        # Fallback to rule-based plan if AI fails
                        if not task_plan:
                            st.info("🤖 AI task planning unavailable, using smart fallback system...")
                            task_plan = assistant.generate_smart_task_plan(checkin_data)
                        else:
                            st.success("🤖 AI-powered personalized plan generated!")
                    else:
                        st.info("🤖 AI service not available, using smart fallback system...")
                        task_plan = assistant.generate_smart_task_plan(checkin_data)
                    
                    # Display tasks
                    st.write("**📋 Recommended Tasks:**")
                    for i, task in enumerate(task_plan['tasks'], 1):
                        st.write(f"{i}. {task}")
                    
                    # Display recommendations
                    if task_plan['recommendations']:
                        st.write("**💡 Smart Recommendations:**")
                        for rec in task_plan['recommendations']:
                            st.info(rec)
                    
                    # Display estimated duration
                    st.write(f"**⏰ Estimated Duration:** {task_plan['estimated_duration']}")
                    
                    # Add task completion tracking
                    st.write("**✅ Task Completion:**")
                    task_completion = {}
                    for task in task_plan['tasks']:
                        task_completion[task] = st.checkbox(f"Complete: {task}")
                    
                    # Save task plan to user data
                    checkin_data['task_plan'] = task_plan
                    checkin_data['task_completion'] = task_completion
                    user_email = get_user_email() or "me@example.com"
                save_checkin_data(checkin_data, user_email)

# Handle pending skips (outside of forms)
if 'pending_skips' in st.session_state:
    pending = st.session_state['pending_skips']
    st.markdown("---")
    st.markdown("### 📝 Record Skipped Steps")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"**Skipped {len(pending['skipped'])} step(s):**")
        for s in pending['skipped']:
            st.write(f"• {s['title']}")
        st.write(f"**Reason:** {pending['reason']}")
    
    with col2:
        if st.button("Record Skip & Adapt Plan", type="primary"):
            # Process the skips
            for s in pending['skipped']:
                db.mark_step_status(s["step_id"], "skipped")
            
            # Adapt the plan
            adapt_ctx = {
                "goal": active_goal,
                "skipped": pending['skipped'],
                "reason": pending['reason'],
                "recent_candidates": pending['candidates'],
            }
            
            try:
                if ai_service:
                    change = ai_service.adapt_plan(adapt_ctx, user_email) or {"change_summary": "No change", "diff": []}
                    try:
                        diff_json = json.dumps(change.get("diff", []))
                    except Exception:
                        diff_json = "[]"
                    db.record_adaptation(active_goal["id"], datetime.now().isoformat(), 0, pending['reason'], change.get("change_summary",""), diff_json)
                    st.success("✅ Plan adapted! Check your plan page for updates.")
                else:
                    st.info("📝 Skipped step recorded. Plan will adapt over time.")
            except Exception as e:
                st.error(f"Error adapting plan: {e}")
                st.info("📝 Skipped step recorded. Plan will adapt over time.")
            
            # Clear the pending skips
            del st.session_state['pending_skips']
            st.rerun()

# Handle pending completions (outside of forms)
if 'pending_completions' in st.session_state:
    pending = st.session_state['pending_completions']
    st.markdown("---")
    st.markdown("### ✅ Complete Selected Steps")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"**{len(pending)} step(s) ready to mark as complete:**")
        # Get step details for display
        if active_goal:
            milestones, steps = db.list_plan(active_goal['id'])
            for step_id in pending:
                step = next((s for s in steps if s['id'] == step_id), None)
                if step:
                    st.write(f"• {step['title']}")
    
    with col2:
        if st.button("🎉 Mark as Complete", type="primary"):
            # Process the completions
            for step_id in pending:
                db.mark_step_status(step_id, "completed")
            
            st.success(f"🎉 Great job! Marked {len(pending)} step(s) as complete!")
            
            # Clear the pending completions
            del st.session_state['pending_completions']
            st.rerun()

# Handle feedback (outside of forms)
if 'morning_feedback' in st.session_state:
    feedback = st.session_state['morning_feedback']
    st.markdown("---")
    st.markdown("### 💬 Feedback Response")
    
    if feedback == "👍 Great!":
        st.success("Thanks! We're glad it's working well for you! 🙏")
    elif feedback == "🤔 Could be better":
        st.info("We'd love to hear your suggestions! [📝 Feedback Form](https://tally.so/r/mBr11Q)")
    elif feedback == "📝 Share detailed feedback":
        st.markdown("**[📋 Open Feedback Form](https://tally.so/r/mBr11Q)**")
    
    if st.button("Clear Feedback", key="clear_feedback"):
        del st.session_state['morning_feedback']
        st.rerun()

# Daily Goal Reflection (outside of forms)
if active_goal:
    st.markdown("---")
    st.markdown("### 🎯 Daily Goal Reflection")
    
    # Show goal reminder
    goal_title = active_goal.get('title', 'Your goal')
    goal_why = active_goal.get('why_matters', 'Not specified')
    
    st.write(f"**Your Goal:** {goal_title}")
    st.write(f"**Why this matters:** {goal_why}")
    
    # Daily reflection questions
    with st.expander("💭 Reflect on Today's Progress", expanded=False):
        st.write("**How did today's actions move you closer to your goal?**")
        
        # Get today's completed steps
        milestones, steps = db.list_plan(active_goal['id'])
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        current_week_steps = []
        for step in steps:
            try:
                due_date = datetime.fromisoformat(step['due_date']).date()
                if week_start <= due_date <= week_end:
                    current_week_steps.append(step)
            except:
                current_week_steps.append(step)
        
        today_steps = [s for s in current_week_steps if s.get('suggested_day') == current_time.strftime('%A')]
        completed_today = [s for s in today_steps if s.get('status') == 'completed']
        
        if completed_today:
            st.write("**✅ Steps you completed today:**")
            for step in completed_today:
                milestone_title = next((m['title'] for m in milestones if m['id'] == step['milestone_id']), 'Unknown')
                st.write(f"• {step['title']} - *{milestone_title}*")
            
            st.write("**🤔 Reflection questions:**")
            st.write("• How do these completed steps connect to your bigger goal?")
            st.write("• What did you learn or discover today?")
            st.write("• What would you do differently tomorrow?")
        else:
            st.write("**📝 No specific steps completed today.**")
            st.write("**🤔 Reflection questions:**")
            st.write("• What did you do today that might help your goal?")
            st.write("• What obstacles did you face?")
            st.write("• How can you make tomorrow more productive?")

# Step completion section (outside of forms)
if active_goal:
    milestones, steps = db.list_plan(active_goal['id'])
    if steps:
        # Get current week's steps
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        current_week_steps = []
        for step in steps:
            try:
                due_date = datetime.fromisoformat(step['due_date']).date()
                if week_start <= due_date <= week_end:
                    current_week_steps.append(step)
            except:
                current_week_steps.append(step)
        
        if current_week_steps:
            st.markdown("---")
