"""
Fallback System for Focus Companion
Provides intelligent responses when AI features are not available
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class FallbackAssistant:
    """Fallback assistant that provides intelligent responses without AI"""
    
    def __init__(self, user_profile: Dict = None, mood_data: List[Dict] = None, checkin_data: List[Dict] = None):
        self.user_profile = user_profile or {}
        self.mood_data = mood_data or []
        self.checkin_data = checkin_data or []
        self.user_goal = self.user_profile.get('goal', 'Improve focus and productivity')
        self.user_tone = self.user_profile.get('tone', 'Gentle & Supportive')
        self.joy_sources = self.user_profile.get('joy_sources', [])
        self.energy_drainers = self.user_profile.get('energy_drainers', [])
        self.therapy_coaching = self.user_profile.get('therapy_coaching', 'No')
        self.availability = self.user_profile.get('availability', '1–2 hours')
        self.energy = self.user_profile.get('energy', 'Okay')
        self.emotional_patterns = self.user_profile.get('emotional_patterns', 'Not sure yet')
        self.small_habit = self.user_profile.get('small_habit', '')
        self.reminders = self.user_profile.get('reminders', 'Yes')
        self.situation = self.user_profile.get('situation', 'Freelancer')
        
        # AI service will be imported locally when needed
    
    def get_daily_encouragement(self) -> str:
        """Get a daily encouragement message"""
        # Get user email from session state if available
        user_email = None
        try:
            import streamlit as st
            user_email = st.session_state.get('user_email')
        except:
            pass
        
        # Try AI first
        try:
            from .ai_service import AIService
            ai_service = AIService()
            ai_encouragement = ai_service.generate_daily_encouragement(
                self.user_profile, self.mood_data, self.checkin_data, user_email
            )
        except Exception:
            ai_encouragement = None
        
        if ai_encouragement:
            return ai_encouragement
        
        # Fallback to rule-based encouragement
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            messages = [
                f"🌅 Good morning! Ready to tackle your goal: {self.user_goal}",
                f"🌅 Rise and shine! Today is a new opportunity to work on: {self.user_goal}",
                f"🌅 Morning! Let's start the day focused on: {self.user_goal}"
            ]
        elif 12 <= current_hour < 18:
            messages = [
                f"☀️ Good afternoon! How's your progress on: {self.user_goal}",
                f"☀️ Afternoon check-in! Still working toward: {self.user_goal}",
                f"☀️ Midday reminder: You're making progress on: {self.user_goal}"
            ]
        else:
            messages = [
                f"🌆 Good evening! Reflect on your work toward: {self.user_goal}",
                f"🌆 Evening! How did you do today with: {self.user_goal}",
                f"🌆 Night check-in! Remember your focus on: {self.user_goal}"
            ]
        
        return random.choice(messages)
    
    def get_mood_insight(self) -> str:
        """Get a mood insight based on recent data"""
        # Try AI first
        try:
            from .ai_service import AIService
            ai_service = AIService()
            ai_insight = ai_service.generate_mood_analysis(self.mood_data, self.user_goal)
        except Exception:
            ai_insight = None
        
        if ai_insight:
            return ai_insight
        
        # Fallback to rule-based insight
        if not self.mood_data:
            return "💡 Start tracking your mood to discover patterns and insights!"
        
        recent_moods = [m for m in self.mood_data 
                       if datetime.fromisoformat(m['timestamp']) > datetime.now() - timedelta(days=7)]
        
        if not recent_moods:
            return "💡 Log your mood regularly to see how it affects your focus and productivity!"
        
        # Calculate average mood intensity
        # Handle both old format (with intensity) and new format (without intensity)
        intensities = []
        for m in recent_moods:
            if 'intensity' in m:
                intensities.append(m['intensity'])
            else:
                # For new format without intensity, use a default value
                intensities.append(5)  # Default neutral mood intensity
        
        avg_intensity = sum(intensities) / len(intensities) if intensities else 5
        
        if avg_intensity >= 7:
            return "🎉 Your mood has been positive recently! This is great for maintaining focus and productivity."
        elif avg_intensity >= 5:
            return "😊 Your mood has been stable. Consider what activities boost your energy and mood."
        else:
            return "💙 Your mood has been lower than usual. Remember to be kind to yourself and reach out for support if needed."
    
    def get_productivity_tip(self) -> str:
        """Get a random productivity tip"""
        # Get user email from session state if available
        user_email = None
        try:
            import streamlit as st
            user_email = st.session_state.get('user_email')
        except:
            pass
        
        # Try AI first
        try:
            from .ai_service import AIService
            ai_service = AIService()
            ai_tip = ai_service.generate_productivity_tip(
                self.user_profile, self.mood_data, self.checkin_data, user_email
            )
            
            if ai_tip and len(ai_tip.strip()) > 10:  # Ensure we have a meaningful tip
                return ai_tip
        except Exception as e:
            # If AI fails, fall back to rule-based tips
            pass
        
        # Fallback to rule-based tips
        tips = [
            "💡 Try the Pomodoro Technique: 25 minutes of focused work, then a 5-minute break",
            "💡 Eliminate distractions by putting your phone in another room",
            "💡 Start with your most important task when your energy is highest",
            "💡 Take regular breaks to maintain focus and prevent burnout",
            "💡 Create a dedicated workspace to signal your brain it's time to focus",
            "💡 Use time-blocking to schedule specific tasks for specific times",
            "💡 Practice the 2-minute rule: if it takes less than 2 minutes, do it now",
            "💡 Batch similar tasks together to reduce context switching",
            "💡 Set clear, specific goals for each work session",
            "💡 Review and plan your day the night before"
        ]
        
        return random.choice(tips)
    
    def get_wellness_reminder(self) -> str:
        """Get a wellness reminder"""
        reminders = [
            "💧 Remember to stay hydrated throughout the day",
            "🌱 Take a moment to stretch and move your body",
            "😌 Practice deep breathing when you feel overwhelmed",
            "☀️ Get some natural light and fresh air",
            "🍎 Fuel your body with nutritious food",
            "😴 Prioritize good sleep for better focus tomorrow",
            "🎵 Listen to music that helps you focus",
            "🧘 Try a quick meditation or mindfulness exercise",
            "👥 Connect with someone who supports your goals",
            "🎯 Celebrate small wins and progress"
        ]
        
        return random.choice(reminders)
    
    def get_goal_reminder(self) -> str:
        """Get a personalized goal reminder"""
        goal_reminders = [
            f"🎯 Remember your goal: {self.user_goal}",
            f"🎯 Every small step brings you closer to: {self.user_goal}",
            f"🎯 Stay focused on what matters: {self.user_goal}",
            f"🎯 Your progress toward {self.user_goal} is worth celebrating",
            f"🎯 Keep moving forward with: {self.user_goal}"
        ]
        
        return random.choice(goal_reminders)
    
    def get_weekly_motivation(self) -> str:
        """Get weekly motivation message"""
        motivations = [
            "🚀 New week, new opportunities to make progress!",
            "🌟 You've got this! Every day is a chance to improve",
            "💪 Consistency beats perfection - keep showing up",
            "🎯 Small actions compound into big results",
            "🌈 Progress, not perfection, is the goal",
            "🔥 Your future self will thank you for today's efforts",
            "⭐ You're building habits that will serve you well",
            "🎊 Celebrate your commitment to growth and improvement"
        ]
        
        return random.choice(motivations)
    
    def get_personalized_greeting(self) -> str:
        """Get a personalized greeting based on user preferences"""
        # Get user email from session state if available
        user_email = None
        try:
            import streamlit as st
            user_email = st.session_state.get('user_email')
        except:
            pass
        
        # Try AI first
        try:
            from .ai_service import AIService
            ai_service = AIService()
            ai_greeting = ai_service.generate_personalized_greeting(
                self.user_profile, self.mood_data, self.checkin_data, user_email
            )
        except Exception:
            ai_greeting = None
        
        if ai_greeting:
            return ai_greeting
        
        # Fallback to rule-based greeting
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            time_greeting = "Good morning"
        elif 12 <= current_hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        # Add personal touch based on tone preference
        if self.user_tone == "Gentle & supportive":
            tone_phrase = "I'm here to support you"
        elif self.user_tone == "Direct & motivating":
            tone_phrase = "Let's make today productive"
        else:
            tone_phrase = "Ready to help you focus"
        
        return f"{time_greeting}! {tone_phrase} on your goal: {self.user_goal}"
    
    def get_personalized_joy_suggestions(self) -> List[str]:
        """Get personalized suggestions based on user's joy sources"""
        suggestions = []
        
        for joy_source in self.joy_sources:
            if joy_source == "Friends":
                suggestions.append("👥 Connect with a friend or family member")
            elif joy_source == "Movement":
                suggestions.append("🏃‍♂️ Do some light exercise or stretching")
            elif joy_source == "Creating":
                suggestions.append("🎨 Spend time on a creative project")
            elif joy_source == "Helping others":
                suggestions.append("🤝 Do something kind for someone else")
            elif joy_source == "Nature":
                suggestions.append("🌿 Spend time outdoors or with plants")
            elif joy_source == "Rest":
                suggestions.append("😌 Take a moment to rest and recharge")
            elif joy_source == "Learning":
                suggestions.append("📚 Read or learn something new")
        
        return suggestions
    
    def get_energy_drainer_avoidance_tips(self) -> List[str]:
        """Get tips to avoid or manage energy drainers"""
        tips = []
        
        for drainer in self.energy_drainers:
            if drainer == "Overwhelm":
                tips.append("📝 Break tasks into smaller, manageable steps")
            elif drainer == "Lack of sleep":
                tips.append("😴 Prioritize getting 7-9 hours of sleep")
            elif drainer == "Isolation":
                tips.append("👥 Reach out to someone for connection")
            elif drainer == "Criticism":
                tips.append("💙 Practice self-compassion and positive self-talk")
            elif drainer == "Deadlines":
                tips.append("⏰ Start tasks early to reduce deadline pressure")
        
        return tips
    
    def get_situation_specific_advice(self) -> str:
        """Get advice specific to user's situation"""
        situation_advice = {
            "Freelancer": "💼 As a freelancer, consider setting clear work boundaries and regular breaks",
            "New parent": "👶 Parenting is demanding - remember to take care of yourself too",
            "PhD student": "🎓 Research can be isolating - try to connect with colleagues regularly",
            "Full-time job": "🏢 Balance work demands with personal time and self-care",
            "Unemployed": "💪 Use this time to build skills and maintain a positive routine"
        }
        
        return situation_advice.get(self.situation, "🌟 Focus on what you can control and celebrate small wins")
    
    def get_small_habit_reminder(self) -> str:
        """Get a reminder about the user's small habit goal"""
        if self.small_habit and self.energy in ["Low", "Very low"]:
            return f"🌱 Remember your small habit goal: {self.small_habit}. Even 5 minutes counts!"
        return ""
    
    def get_activity_suggestion(self) -> str:
        """Get a suggestion for a focus or wellness activity"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            activities = [
                "🌅 Start with a 5-minute meditation",
                "📝 Write down your top 3 priorities for today",
                "🏃 Take a short walk to boost your energy",
                "📚 Read something inspiring for 10 minutes",
                "🎯 Set a specific, achievable goal for this morning"
            ]
        elif 12 <= current_hour < 18:
            activities = [
                "☀️ Take a 10-minute break to recharge",
                "🚶 Go for a short walk outside",
                "💧 Drink a glass of water and stretch",
                "🎵 Listen to focus music for 15 minutes",
                "🧘 Do a quick breathing exercise"
            ]
        else:
            activities = [
                "🌆 Reflect on today's accomplishments",
                "📖 Read something relaxing before bed",
                "🛁 Take time to unwind and decompress",
                "📝 Plan tomorrow's priorities",
                "😴 Prepare for a good night's sleep"
            ]
        
        return random.choice(activities)
    
    def get_encouragement_for_situation(self, situation: str) -> str:
        """Get encouragement specific to user's situation"""
        situation_encouragement = {
            "New parent": [
                "👶 Being a new parent is challenging - you're doing great!",
                "💕 Your little one is lucky to have such a dedicated parent",
                "🌟 Parenthood and personal growth can happen together"
            ],
            "PhD student": [
                "🎓 Your research and dedication will pay off",
                "📚 Every study session brings you closer to your degree",
                "🔬 You're contributing valuable knowledge to your field"
            ],
            "Freelancer": [
                "💼 Your independence and flexibility are strengths",
                "🚀 Every project builds your portfolio and skills",
                "⭐ You're building your own success story"
            ],
            "Full-time job": [
                "💼 Your commitment to growth in your career is admirable",
                "🏢 Balancing work and personal development takes skill",
                "📈 You're investing in your future success"
            ],
            "Unemployed": [
                "💪 This is a temporary phase - you're building your next chapter",
                "🎯 Use this time to develop skills and clarity",
                "🌟 Your resilience during this time will serve you well"
            ]
        }
        
        if situation in situation_encouragement:
            return random.choice(situation_encouragement[situation])
        else:
            return "🌟 You're on a journey of growth and improvement - that's worth celebrating!"
    
    def generate_smart_task_plan(self, checkin_data: Dict, user_goals: str = None) -> Dict:
        """Generate intelligent task planning based on user's current state and goals"""
        current_hour = datetime.now().hour
        time_period = checkin_data.get('time_period', 'morning')
        
        # Analyze current state
        sleep_quality = checkin_data.get('sleep_quality', 'Good')
        energy_level = checkin_data.get('energy_level', 'Good')
        current_feeling = checkin_data.get('current_feeling', 'Good')
        day_progress = checkin_data.get('day_progress', 'Good')
        
        # Get user's focus goal
        focus_goal = checkin_data.get('focus_today', user_goals or self.user_goal)
        
        # Generate task plan based on time period and state
        if time_period == 'morning':
            return self._generate_morning_task_plan(sleep_quality, energy_level, focus_goal)
        elif time_period == 'afternoon':
            return self._generate_afternoon_task_plan(energy_level, day_progress, focus_goal)
        else:  # evening
            return self._generate_evening_task_plan(current_feeling, focus_goal)
    
    def _generate_morning_task_plan(self, sleep_quality: str, energy_level: str, focus_goal: str) -> Dict:
        """Generate morning task plan based on sleep and energy"""
        import random
        
        tasks = []
        recommendations = []
        
        # Adjust based on sleep quality
        if sleep_quality in ['Poor', 'Terrible']:
            gentle_tasks = [
                "🌅 Gentle morning routine (10 min)",
                "💧 Hydrate with water",
                "🧘 Light stretching or meditation",
                "☕ Enjoy a warm beverage slowly",
                "🌱 Spend 5 minutes with plants or nature",
                "📖 Read something uplifting for 10 minutes"
            ]
            tasks.extend(random.sample(gentle_tasks, 3))
            recommendations.append("Start with gentle activities to build momentum")
        elif sleep_quality in ['Excellent', 'Good']:
            productive_tasks = [
                "🎯 Tackle your most important task first",
                "📝 Review and prioritize today's goals",
                "🏃‍♂️ Consider exercise if energy is high",
                "⚡ Use your peak energy for complex work",
                "📊 Plan your day with specific time blocks",
                "🎨 Start with creative or challenging tasks"
            ]
            tasks.extend(random.sample(productive_tasks, 3))
            recommendations.append("Great sleep! You're ready for focused work")
        
        # Adjust based on energy level
        if energy_level in ['Low', 'Very low']:
            energy_boost_tasks = [
                "☕ Have a healthy breakfast",
                "🚶‍♂️ Take a short walk outside",
                "📚 Start with lighter, more enjoyable tasks",
                "🍎 Eat a nutritious snack",
                "🌞 Get some natural light exposure",
                "🎵 Listen to energizing music"
            ]
            tasks.extend(random.sample(energy_boost_tasks, 3))
            recommendations.append("Build energy gradually with nourishing activities")
        elif energy_level in ['High', 'Good']:
            high_energy_tasks = [
                "⚡ Use your high energy for complex tasks",
                "🎯 Break down your main goal into 2-3 key actions",
                "⏰ Set specific time blocks for focused work",
                "🚀 Tackle challenging projects first",
                "📈 Work on skill development",
                "🎨 Engage in creative problem-solving"
            ]
            tasks.extend(random.sample(high_energy_tasks, 3))
            recommendations.append("Perfect energy for productive deep work")
        
        # Add focus goal breakdown
        if focus_goal:
            tasks.append(f"🎯 Main focus: {focus_goal}")
            tasks.append("📋 Break this into 3 smaller steps")
        
        # Add personalized joy-based activities
        joy_suggestions = self.get_personalized_joy_suggestions()
        if joy_suggestions:
            tasks.append("💫 Energy boost: " + joy_suggestions[0])
        
        # Add small habit reminder if applicable
        habit_reminder = self.get_small_habit_reminder()
        if habit_reminder:
            recommendations.append(habit_reminder)
        
        # Add situation-specific advice
        situation_advice = self.get_situation_specific_advice()
        if situation_advice:
            recommendations.append(situation_advice)
        
        return {
            "tasks": tasks,
            "recommendations": recommendations,
            "estimated_duration": self._estimate_task_duration(energy_level, sleep_quality),
            "priority_order": "energy_based"
        }
    
    def _generate_afternoon_task_plan(self, energy_level: str, day_progress: str, focus_goal: str) -> Dict:
        """Generate afternoon task plan based on energy and progress"""
        tasks = []
        recommendations = []
        
        # Adjust based on day progress
        if day_progress in ['Challenging', 'Difficult']:
            tasks.extend([
                "🔄 Review what's working and what's not",
                "📝 Break down remaining tasks into smaller chunks",
                "☕ Take a proper break to reset"
            ])
            recommendations.append("It's okay to adjust your approach")
        elif day_progress in ['Great', 'Good']:
            tasks.extend([
                "🚀 Build on your momentum",
                "🎯 Focus on your next priority",
                "💡 Consider adding one more meaningful task"
            ])
            recommendations.append("Great progress! Keep the momentum going")
        
        # Adjust based on energy level
        if energy_level in ['Low', 'Very low']:
            tasks.extend([
                "🍎 Have a healthy snack",
                "🚶‍♂️ Take a 10-minute walk",
                "📚 Switch to lighter, administrative tasks"
            ])
            recommendations.append("Focus on energy restoration and lighter tasks")
        elif energy_level in ['High', 'Good']:
            tasks.extend([
                "⚡ Tackle your most challenging remaining task",
                "🎯 Deep work session (45-90 minutes)",
                "📊 Review and adjust your plan for the rest of the day"
            ])
            recommendations.append("Use your energy for focused, important work")
        
        # Add energy drainer avoidance tips
        drainer_tips = self.get_energy_drainer_avoidance_tips()
        if drainer_tips:
            recommendations.append("💡 Avoid energy drainers: " + drainer_tips[0])
        
        # Add joy-based activity for energy boost
        joy_suggestions = self.get_personalized_joy_suggestions()
        if joy_suggestions and energy_level in ['Low', 'Very low']:
            tasks.append("💫 Quick energy boost: " + joy_suggestions[0])
        
        return {
            "tasks": tasks,
            "recommendations": recommendations,
            "estimated_duration": self._estimate_task_duration(energy_level, "Good"),
            "priority_order": "progress_based"
        }
    
    def _generate_evening_task_plan(self, current_feeling: str, focus_goal: str) -> Dict:
        """Generate evening task plan based on current feeling"""
        tasks = []
        recommendations = []
        
        # Adjust based on current feeling
        if current_feeling in ['Tired', 'Stressed']:
            tasks.extend([
                "🧘 Gentle evening routine",
                "📖 Light reading or listening",
                "🛁 Relaxing activity (bath, tea, etc.)"
            ])
            recommendations.append("Focus on rest and recovery")
        elif current_feeling in ['Accomplished', 'Good']:
            tasks.extend([
                "📝 Reflect on today's wins",
                "🎯 Plan tomorrow's priorities",
                "🎉 Celebrate your accomplishments"
            ])
            recommendations.append("Great day! Plan for tomorrow's success")
        
        # Add preparation tasks
        tasks.extend([
            "🌙 Prepare for tomorrow",
            "📋 Review tomorrow's schedule",
            "😴 Wind down routine"
        ])
        
        return {
            "tasks": tasks,
            "recommendations": recommendations,
            "estimated_duration": "1-2 hours",
            "priority_order": "wellness_based"
        }
    
    def _estimate_task_duration(self, energy_level: str, sleep_quality: str) -> str:
        """Estimate task duration based on energy and sleep"""
        if energy_level in ['High', 'Good'] and sleep_quality in ['Excellent', 'Good']:
            return "4-6 hours of focused work"
        elif energy_level in ['Moderate']:
            return "3-4 hours of moderate work"
        else:
            return "2-3 hours of lighter tasks"

    def fallback_plan(self, goal: dict) -> dict:
        # Enhanced fallback plan using new goal structure
        import datetime
        title = goal.get("title","Your Goal")
        deadline = goal.get("deadline")
        weekly_time = goal.get("weekly_time", "2–4 hours")
        intensity = goal.get("intensity", "Balanced")
        energy_time = goal.get("energy_time", "Morning")
        free_days = goal.get("free_days", [])
        starting_point = goal.get("starting_point", "Not specified")
        
        today = datetime.date.today()
        if deadline:
            try:
                dl = datetime.date.fromisoformat(deadline)
            except Exception:
                dl = today + datetime.timedelta(days=90)
        else:
            dl = today + datetime.timedelta(days=90)
        
        # Adjust timeline based on intensity
        if intensity == "Gentle":
            total_days = (dl - today).days * 1.5  # More time
            step_count = 8
        elif intensity == "Ambitious":
            total_days = (dl - today).days * 0.7  # Less time
            step_count = 15
        else:  # Balanced
            total_days = (dl - today).days
            step_count = 12
        
        # Create milestones based on starting point
        milestones = []
        if "beginner" in starting_point.lower():
            milestones = [
                {"title": "Foundation Building", "description": f"Learn basics and set up for {title}", "target_date": str(today + datetime.timedelta(days=int(total_days*0.3)))},
                {"title": "Skill Development", "description": f"Develop core skills for {title}", "target_date": str(today + datetime.timedelta(days=int(total_days*0.6)))},
                {"title": "Mastery & Application", "description": f"Apply skills and achieve {title}", "target_date": str(dl)}
            ]
        else:
            milestones = [
                {"title": "Assessment & Planning", "description": f"Evaluate current state and plan for {title}", "target_date": str(today + datetime.timedelta(days=int(total_days*0.25)))},
                {"title": "Active Progress", "description": f"Make significant progress toward {title}", "target_date": str(today + datetime.timedelta(days=int(total_days*0.6)))},
                {"title": "Completion & Refinement", "description": f"Complete and refine {title}", "target_date": str(dl)}
            ]
        
        # Create steps based on energy time and free days
        steps = []
        available_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if free_days:
            available_days = [day for day in available_days if day not in free_days]
        
        # Suggest days based on energy time
        if energy_time == "Morning":
            suggested_days = "Mon,Tue,Wed,Thu,Fri"
        elif energy_time == "Afternoon":
            suggested_days = "Mon,Tue,Wed,Thu,Fri"
        elif energy_time == "Evening":
            suggested_days = "Mon,Tue,Wed,Thu,Fri"
        else:
            suggested_days = "Any"
        
        for i in range(1, step_count + 1):
            milestone_idx = min(i // (step_count // 3), 2)
            milestone_title = milestones[milestone_idx]["title"]
            
            # Adjust step size based on weekly time
            if weekly_time in ["< 1 hour", "1–2 hours"]:
                estimate_minutes = 15
            elif weekly_time in ["2–4 hours"]:
                estimate_minutes = 30
            else:  # 4+ hours
                estimate_minutes = 45
            
            steps.append({
                "milestone_title": milestone_title,
                "title": f"Step {i}: Action item",
                "description": f"Specific action to move toward {title}",
                "estimate_minutes": estimate_minutes,
                "suggested_day": suggested_days,
                "due_date": None
            })
        
        return {"milestones": milestones, "steps": steps}

    def fallback_alignment(self, context: dict) -> dict:
        # choose 1–3 smallest pending steps
        steps = context.get("steps_today_candidates", []) or []
        steps = sorted(steps, key=lambda s: (s.get("estimate_minutes") or 999, s.get("due_date") or "9999-12-31"))
        pick = [{"step_id": s["id"], "title": s["title"]} for s in steps[:3]]
        score = 70 if pick else 40
        why = "Picked small steps to keep momentum given recent mood and time."
        return {"alignment_score": score, "today_steps": pick, "adjustments": [], "why": why}
