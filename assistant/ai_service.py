"""
AI Service for Focus Companion
Handles OpenAI API calls for personalized responses
"""

import os
import openai
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from .prompts import PromptTemplates
from .usage_limiter import UsageLimiter
from .ai_cache import ai_cache, PromptOptimizer
import json

# Load environment variables
load_dotenv()

class AIService:
    """Service for handling AI-powered responses"""
    
    def __init__(self):
        # Initialize OpenAI client
        # Try Streamlit secrets first (for Streamlit Cloud), then environment variables
        api_key = None
        
        try:
            api_key = st.secrets.get("openai_api_key", "")
        except:
            pass
        
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            st.warning("⚠️ OpenAI API key not found. AI features will be disabled.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
        # Initialize usage limiter
        self.usage_limiter = UsageLimiter()
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def can_use_feature(self, feature: str, user_email: str = None) -> tuple[bool, str]:
        """
        Check if a feature can be used based on limits
        Returns (allowed, reason)
        """
        # Admin user bypass - unlimited access for testing
        from auth import get_admin_email
        admin_email = get_admin_email()
        if user_email == admin_email:
            return True, "Admin user - unlimited access"
        
        if not self.is_available():
            return False, "AI service not available"
        
        # Check if feature is enabled
        if not self.usage_limiter.is_feature_enabled(feature, user_email):
            return False, f"Feature '{feature}' is disabled for beta testing"
        
        # Check usage limits
        return self.usage_limiter.can_make_api_call(user_email)
    
    def generate_personalized_greeting(self, user_profile: Dict, mood_data: List[Dict], 
                                     checkin_data: List[Dict], user_email: str = None) -> str:
        """Generate a personalized AI greeting"""
        # Check if we can use this feature
        can_use, reason = self.can_use_feature("greeting", user_email)
        if not can_use:
            st.warning(f"🤖 AI greeting limited: {reason}")
            return None
        
        # Prepare context for the AI
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Determine time of day
        if 5 <= current_hour < 12:
            time_context = "morning"
        elif 12 <= current_hour < 18:
            time_context = "afternoon"
        else:
            time_context = "evening"
        
        # Get recent mood data (last 3 entries)
        recent_moods = mood_data[-3:] if mood_data else []
        mood_summary = ""
        if recent_moods:
            # Handle both old format (with intensity) and new format (without intensity)
            intensities = []
            for m in recent_moods:
                if 'intensity' in m:
                    intensities.append(m['intensity'])
                else:
                    # For new format without intensity, use a default value
                    intensities.append(5)  # Default neutral mood intensity
            
            if intensities:
                avg_mood = sum(intensities) / len(intensities)
                if avg_mood >= 7:
                    mood_summary = "You've been in a positive mood recently"
                elif avg_mood >= 5:
                    mood_summary = "Your mood has been stable"
                else:
                    mood_summary = "You've been experiencing some challenges"
        
        # Get recent check-in patterns
        recent_checkins = checkin_data[-2:] if checkin_data else []
        checkin_summary = ""
        if recent_checkins:
            energy_levels = [c.get('energy_level', 'Unknown') for c in recent_checkins if 'energy_level' in c]
            if energy_levels:
                most_common_energy = max(set(energy_levels), key=energy_levels.count)
                checkin_summary = f"Your energy has been {most_common_energy.lower()}"
        
        # Use the existing prompt template for daily recommendations
        recent_data = {
            'time_context': time_context,
            'mood_summary': mood_summary,
            'checkin_summary': checkin_summary,
            'recent_moods': recent_moods,
            'recent_checkins': recent_checkins
        }
        
        # Check cache first
        if user_email:
            cached_response = ai_cache.get_cached_response("greeting", user_email, recent_data)
            if cached_response:
                return cached_response

        # Use optimized prompt
        prompt = PromptOptimizer.optimize_greeting_prompt(user_profile, recent_data)
        
        try:
            # Show enhanced loading feedback
            with st.spinner("🤖 AI is crafting your personalized greeting..."):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a supportive, encouraging assistant focused on helping users achieve their goals."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
            
            result = response.choices[0].message.content.strip()
            
            # Cache the response
            if user_email:
                ai_cache.cache_response("greeting", user_email, recent_data, result)
            
            # Record the API call with detailed information
            tokens_used = response.usage.total_tokens if response.usage else None
            cost_usd = (tokens_used * 0.000002) if tokens_used else None  # GPT-3.5-turbo pricing
            
            self.usage_limiter.record_api_call(
                user_email=user_email,
                feature="greeting",
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error generating AI greeting: {str(e)}")
            return None
    
    def generate_daily_encouragement(self, user_profile: Dict, mood_data: List[Dict], 
                                   checkin_data: List[Dict], user_email: str = None) -> str:
        """Generate personalized daily encouragement"""
        # Check if we can use this feature
        can_use, reason = self.can_use_feature("encouragement", user_email)
        if not can_use:
            st.warning(f"🤖 AI encouragement limited: {reason}")
            return None
        
        # Prepare recent data for analysis
        recent_data = {
            'mood_data': mood_data[-3:] if mood_data else [],
            'checkin_data': checkin_data[-3:] if checkin_data else [],
            'goal': user_profile.get('goal', 'Improve focus and productivity'),
            'tone': user_profile.get('tone', 'Gentle & Supportive')
        }
        
        # Use the existing prompt template for goal progress analysis
        progress_data = {
            'recent_moods': recent_data['mood_data'],
            'recent_checkins': recent_data['checkin_data'],
            'energy_trend': self._analyze_energy_trend(checkin_data),
            'mood_trend': self._analyze_mood_trend(mood_data)
        }
        
        prompt = PromptTemplates.goal_progress_prompt(user_profile.get('goal', 'Improve focus and productivity'), progress_data)
        
        # Add specific encouragement instructions
        prompt += "\n\nPlease provide an encouraging message (1-2 sentences) that acknowledges their progress and motivates them to continue. Keep it concise and personal."
        
        try:
            # Show enhanced loading feedback
            with st.spinner("🤖 AI is crafting your daily encouragement..."):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an encouraging, supportive assistant helping users stay motivated."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=80,
                    temperature=0.7
                )
            
            result = response.choices[0].message.content.strip()
            
            # Record the API call with detailed information
            tokens_used = response.usage.total_tokens if response.usage else None
            cost_usd = (tokens_used * 0.000002) if tokens_used else None  # GPT-3.5-turbo pricing
            
            self.usage_limiter.record_api_call(
                user_email=user_email,
                feature="encouragement",
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error generating AI encouragement: {str(e)}")
            return None
    
    def generate_productivity_tip(self, user_profile: Dict, mood_data: List[Dict], 
                                checkin_data: List[Dict], user_email: str = None) -> str:
        """Generate a personalized productivity tip"""
        # Check if we can use this feature
        can_use, reason = self.can_use_feature("productivity_tip", user_email)
        if not can_use:
            st.warning(f"🤖 AI productivity tip limited: {reason}")
            return None
        
        # Prepare all data for comprehensive analysis
        all_data = {
            'user_profile': user_profile,
            'mood_data': mood_data[-7:] if mood_data else [],  # Last week
            'checkin_data': checkin_data[-7:] if checkin_data else [],  # Last week
            'energy_drainers': user_profile.get('energy_drainers', []),
            'situation': user_profile.get('situation', 'Not specified'),
            'availability': user_profile.get('availability', '1–2 hours')
        }
        
        # Use the existing prompt template for productivity insights
        prompt = PromptTemplates.productivity_insights_prompt(all_data)
        
        # Add specific tip instructions
        prompt += "\n\nPlease provide ONE specific, actionable productivity tip that considers their current situation and energy drainers. Keep it practical, implementable, and concise (2-3 sentences max)."
        
        try:
            # Show enhanced loading feedback
            with st.spinner("🤖 AI is crafting your personalized productivity tip..."):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a productivity expert providing practical, personalized advice. Keep responses concise and actionable."},
                        {"role": "user", "content": prompt}
                ],
                    max_tokens=150,
                    temperature=0.7
                )
            
            result = response.choices[0].message.content.strip()
            
            # Record the API call with detailed information
            tokens_used = response.usage.total_tokens if response.usage else None
            cost_usd = (tokens_used * 0.000002) if tokens_used else None  # GPT-3.5-turbo pricing
            
            self.usage_limiter.record_api_call(
                user_email=user_email,
                feature="productivity_tip",
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error generating AI productivity tip: {str(e)}")
            return None
    
    def _analyze_energy_trend(self, checkin_data: List[Dict]) -> str:
        """Analyze energy trend from check-in data"""
        if not checkin_data:
            return "No recent data"
        
        recent_checkins = checkin_data[-3:]
        energy_levels = [c.get('energy_level', 'Unknown') for c in recent_checkins if 'energy_level' in c]
        
        if not energy_levels:
            return "No energy data available"
        
        if len(set(energy_levels)) == 1:
            return f"Consistently {energy_levels[0].lower()}"
        else:
            return "Varying energy levels"
    
    def _analyze_mood_trend(self, mood_data: List[Dict]) -> str:
        """Analyze mood trend from mood data"""
        if not mood_data:
            return "No recent data"
        
        recent_moods = mood_data[-3:]
        avg_mood = sum(m.get('intensity', 5) for m in recent_moods) / len(recent_moods)
        
        if avg_mood >= 7:
            return "Positive mood trend"
        elif avg_mood >= 5:
            return "Stable mood"
        else:
            return "Lower mood trend"
    
    def generate_mood_analysis(self, mood_data: List[Dict], user_goal: str) -> str:
        """Generate comprehensive mood analysis using existing prompt template"""
        if not self.is_available():
            return None
        
        prompt = PromptTemplates.mood_analysis_prompt(mood_data, user_goal)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive wellness assistant analyzing mood patterns to help users achieve their goals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating mood analysis: {str(e)}")
            return None
    
    def generate_focus_optimization(self, checkin_data: List[Dict], mood_data: List[Dict]) -> str:
        """Generate focus optimization advice using existing prompt template"""
        if not self.is_available():
            return None
        
        prompt = PromptTemplates.focus_optimization_prompt(checkin_data, mood_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a productivity expert providing focus optimization advice based on user patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating focus optimization: {str(e)}")
            return None
    
    def generate_stress_management(self, mood_data: List[Dict], checkin_data: List[Dict]) -> str:
        """Generate stress management advice using existing prompt template"""
        if not self.is_available():
            return None
        
        prompt = PromptTemplates.stress_management_prompt(mood_data, checkin_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a wellness expert providing stress management advice based on user patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating stress management advice: {str(e)}")
            return None

    def generate_weekly_summary(self, user_profile: Dict, week_analysis: Dict, user_email: str = None) -> str:
        """Generate personalized weekly summary"""
        # Check if we can use this feature
        can_use, reason = self.can_use_feature("weekly_summary", user_email)
        if not can_use:
            st.warning(f"🤖 Weekly summary limited: {reason}")
            return None

        # Prepare comprehensive context for the AI
        total_checkins = week_analysis['total_checkins']
        total_moods = week_analysis['total_mood_entries']
        
        # Find most active day
        day_counts = {}
        for day in week_analysis['checkin_days']:
            day_counts[day] = day_counts.get(day, 0) + 1
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        
        # Find highest energy day
        highest_energy_day = None
        highest_energy = 0
        for day, energies in week_analysis['energy_patterns'].items():
            energy_scores = []
            for energy in energies:
                if energy == 'High': energy_scores.append(5)
                elif energy == 'Good': energy_scores.append(4)
                elif energy == 'Moderate': energy_scores.append(3)
                elif energy == 'Low': energy_scores.append(2)
                elif energy == 'Very low': energy_scores.append(1)
            
            if energy_scores:
                avg_energy = sum(energy_scores) / len(energy_scores)
                if avg_energy > highest_energy:
                    highest_energy = avg_energy
                    highest_energy_day = day
        
        # Find most common mood
        all_moods = []
        for day_data in week_analysis['mood_patterns'].values():
            all_moods.extend(day_data['moods'])
        most_common_mood = max(set(all_moods), key=all_moods.count) if all_moods else None
        
        # Calculate average mood intensity
        all_intensities = []
        for day_data in week_analysis['mood_patterns'].values():
            all_intensities.extend(day_data['intensities'])
        avg_mood_intensity = sum(all_intensities) / len(all_intensities) if all_intensities else 5
        
        # Check cache first
        if user_email:
            cached_response = ai_cache.get_cached_response("weekly_summary", user_email, week_analysis)
            if cached_response:
                return cached_response

        # Use optimized prompt
        prompt = PromptOptimizer.optimize_weekly_summary_prompt(user_profile, week_analysis)

        try:
            # Show enhanced loading feedback
            with st.spinner("🤖 AI is analyzing your weekly patterns and crafting personalized insights..."):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a supportive wellness coach who celebrates progress and provides encouraging insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.8
                )
            result = response.choices[0].message.content.strip()
            
            # Cache the response
            if user_email:
                ai_cache.cache_response("weekly_summary", user_email, week_analysis, result)
            
            # Record the API call with detailed information
            tokens_used = response.usage.total_tokens if response.usage else None
            cost_usd = (tokens_used * 0.000002) if tokens_used else None  # GPT-3.5-turbo pricing
            
            self.usage_limiter.record_api_call(
                user_email=user_email,
                feature="weekly_summary",
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error generating weekly summary: {str(e)}")
            return None

    def generate_ai_task_plan(self, user_profile: Dict, checkin_data: Dict, mood_data: List[Dict], user_email: str = None) -> Dict:
        """Generate AI-powered personalized task plan"""
        # Check if we can use this feature
        can_use, reason = self.can_use_feature("task_planning", user_email)
        if not can_use:
            st.warning(f"🤖 AI task planning limited: {reason}")
            return None

        # Prepare comprehensive context for the AI
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Determine time period
        if 5 <= current_hour < 12:
            time_period = "morning"
        elif 12 <= current_hour < 18:
            time_period = "afternoon"
        else:
            time_period = "evening"
        
        # Get recent context
        recent_moods = mood_data[-3:] if mood_data else []
        
        # Handle checkin_data - it could be a list of all checkins or a single checkin dict
        if isinstance(checkin_data, list):
            recent_checkins = checkin_data[-2:] if checkin_data else []
        else:
            # If it's a single checkin dict, we don't have recent checkins for context
            recent_checkins = []
        
        # Build comprehensive context
        context = {
            'time_period': time_period,
            'current_hour': current_hour,
            'user_goal': user_profile.get('goal', 'Improve focus and productivity'),
            'user_tone': user_profile.get('tone', 'Friendly'),
            'availability': user_profile.get('availability', '2-4 hours'),
            'energy_drainers': user_profile.get('energy_drainers', []),
            'joy_sources': user_profile.get('joy_sources', []),
            'situation': user_profile.get('situation', 'Not specified'),
            'small_habit': user_profile.get('small_habit', ''),
            'current_checkin': checkin_data,
            'recent_moods': recent_moods,
            'recent_checkins': recent_checkins,
            'all_checkins': checkin_data if isinstance(checkin_data, list) else [],
            'focus_today': checkin_data.get('focus_today', 'Not specified'),
            'energy_level': checkin_data.get('energy_level', 'Not specified'),
            'current_feeling': checkin_data.get('current_feeling', 'Not specified'),
            'sleep_quality': checkin_data.get('sleep_quality', 'Not specified'),
            'day_progress': checkin_data.get('day_progress', 'Not specified')
        }

        # Check cache first
        if user_email:
            cached_response = ai_cache.get_cached_response("task_planning", user_email, context)
            if cached_response:
                try:
                    import json
                    return json.loads(cached_response)
                except:
                    pass

        # Generate AI prompt for task planning
        prompt = f"""
You are an expert productivity coach and life strategist who creates deeply personalized, thoughtful daily plans. Your goal is to help users feel empowered, not overwhelmed, while making meaningful progress toward their goals.

USER CONTEXT:
- Primary Goal: {context['user_goal']}
- Communication Style: {context['user_tone']}
- Available Time: {context['availability']}
- Current Time: {context['time_period']} ({current_hour}:00)
- Life Situation: {context['situation']}

CURRENT STATE ANALYSIS:
- Sleep Quality: {checkin_data.get('sleep_quality', 'Not specified')}
- Energy Level: {checkin_data.get('energy_level', 'Not specified')}
- Emotional State: {checkin_data.get('current_feeling', 'Not specified')}
- Day Progress: {checkin_data.get('day_progress', 'Not specified')}
- Main Focus: {checkin_data.get('focus_today', 'Not specified')}

PERSONAL PREFERENCES & PATTERNS:
- Energy Drainers (Avoid): {context['energy_drainers']}
- Joy Sources (Incorporate): {context['joy_sources']}
- Small Habit: {context['small_habit']}
- Recent Mood Pattern: {[', '.join(m.get('moods', [m.get('mood', 'Unknown')])) for m in recent_moods]}
- Recent Energy Pattern: {[c.get('energy_level', 'Unknown') for c in recent_checkins]}

DEEP PLANNING APPROACH:
1. **Energy-Aware Task Design**: Match task complexity to their current energy level
2. **Emotional Intelligence**: Consider their emotional state and provide appropriate support
3. **Goal Alignment**: Break down their main focus into manageable, meaningful steps
4. **Joy Integration**: Weave in their joy sources naturally to boost motivation
5. **Overwhelm Prevention**: Structure tasks to feel achievable, not daunting
6. **Progress Momentum**: Design tasks that build on each other and create a sense of accomplishment
7. **Flexibility**: Account for their availability and life situation

TASK BREAKDOWN STRATEGY:
- **High Energy + Good Sleep**: Focus on complex, creative, or challenging tasks
- **Moderate Energy**: Mix of focused work and lighter activities
- **Low Energy**: Gentle, restorative activities that still move them forward
- **Poor Sleep**: Extra gentle approach with lots of self-care
- **Stressed/Overwhelmed**: Focus on calming, grounding activities first
- **Motivated/Accomplished**: Build on momentum with next-level tasks

CREATE A PERSONALIZED {context['time_period'].upper()} PLAN THAT:
1. **Deeply reflects their specific focus** - Break down their main goal into 3-5 thoughtful, actionable steps
2. **Matches their energy perfectly** - Tasks should feel right for their current state
3. **Incorporates their joy sources naturally** - Use what energizes them to boost motivation
4. **Avoids their energy drainers** - Steer clear of what depletes them
5. **Prevents overwhelm** - Structure tasks to feel achievable and satisfying
6. **Builds momentum** - Each task should naturally lead to the next
7. **Provides emotional support** - Consider their feelings and offer appropriate encouragement

FORMAT: Return a JSON object with:
{{
    "tasks": [
        "Specific, actionable task that directly relates to their focus",
        "Next logical step that builds on the first",
        "Task that incorporates their joy sources",
        "Task that moves them toward their goal",
        "Optional: Small habit or self-care task"
    ],
    "recommendations": [
        "Specific advice for their current energy/emotional state",
        "Strategy to avoid their energy drainers",
        "Encouragement that matches their tone preference"
    ],
    "estimated_duration": "Realistic time estimate based on their availability",
    "priority_order": "energy_based or goal_based",
    "personalized_note": "Thoughtful, encouraging message that acknowledges their specific situation and feelings"
}}

IMPORTANT: Make each task specific to their stated focus. If they want to "work on project X," don't give generic tasks - break down what "working on project X" actually means for them right now. Consider their energy level, emotional state, and make the plan feel like it was crafted specifically for them in this moment.
"""

        try:
            # Show enhanced loading feedback
            with st.spinner(f"🤖 AI is crafting your personalized {context['time_period']} plan..."):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert productivity coach and life strategist with deep empathy and understanding of human psychology. You specialize in creating thoughtful, personalized daily plans that help people feel empowered and make meaningful progress without feeling overwhelmed. You understand that productivity is deeply personal and varies greatly based on energy, emotions, life circumstances, and individual preferences. Your goal is to craft plans that feel like they were made specifically for this person in this moment."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                
                # Parse JSON response
                try:
                    import json
                    task_plan = json.loads(result)
                    
                    # Cache the response
                    if user_email:
                        ai_cache.cache_response("task_planning", user_email, context, result)
                    
                    # Record the API call
                    tokens_used = response.usage.total_tokens if response.usage else None
                    cost_usd = (tokens_used * 0.000002) if tokens_used else None
                    
                    self.usage_limiter.record_api_call(
                        user_email=user_email,
                        feature="task_planning",
                        tokens_used=tokens_used,
                        cost_usd=cost_usd
                    )
                    
                    return task_plan
                    
                except json.JSONDecodeError:
                    st.error("Error parsing AI task plan response")
                    return None
                
        except Exception as e:
            st.error(f"Error generating AI task plan: {str(e)}")
            return None

    # ---- internal JSON chat helper ----
    def _chat_json(self, prompt: str) -> dict:
        """
        Calls your chat model and parses JSON safely. 
        If your project already has a 'chat' method, use it here.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,  # Increased for comprehensive plans
                temperature=0.3,
                timeout=30  # Add timeout
            )
            txt = response.choices[0].message.content.strip().strip("`")
            # try to extract JSON if model wrapped in code fences
            if txt.startswith("{") and txt.endswith("}"):
                return json.loads(txt)
            # fallback: find first JSON block
            start = txt.find("{")
            end = txt.rfind("}")
            if start != -1 and end != -1:
                return json.loads(txt[start:end+1])
        except Exception as e:
            st.error(f"❌ AI API Error: {str(e)}")
        return {}

    # ---- Feature flags/limits already exist; reuse your can_use_feature if present ----
    def generate_goal_plan(self, goal: dict, user_email: str = None) -> dict:
        try:
            can_use, reason = self.can_use_feature("plan_generation", user_email)
        except Exception:
            can_use = True
        if not can_use:
            from .fallback import FallbackAssistant
            fallback = FallbackAssistant()
            return fallback.fallback_plan(goal)
        prompt = PromptTemplates.goal_plan_prompt(goal)
        out = self._chat_json(prompt)
        if not out:
            from .fallback import FallbackAssistant
            fallback = FallbackAssistant()
            return fallback.fallback_plan(goal)
        
        # Validate and fix the plan
        out = self._validate_and_fix_plan(out, goal)
        return out
    
    def _validate_and_fix_plan(self, plan: dict, goal: dict) -> dict:
        """Validate and fix plan to ensure it follows constraints"""
        from datetime import datetime, timedelta
        
        # Parse weekly time constraint
        weekly_time = goal.get('weekly_time', 'Not specified')
        weekly_hours = 0
        if '1-2' in weekly_time.lower():
            weekly_hours = 1.5
        elif '2-3' in weekly_time.lower():
            weekly_hours = 2.5
        elif '3-4' in weekly_time.lower():
            weekly_hours = 3.5
        elif '4-5' in weekly_time.lower():
            weekly_hours = 4.5
        elif '5+' in weekly_time.lower() or 'more' in weekly_time.lower():
            weekly_hours = 6
        else:
            weekly_hours = 3
        
        max_weekly_minutes = int(weekly_hours * 60)
        
        # Fix dates to start from today and be realistic
        today = datetime.now().date()
        current_year = today.year
        
        # Calculate realistic timeline based on weekly hours
        if weekly_hours <= 2:
            # Low commitment: 6-12 months
            max_timeline_months = 12
        elif weekly_hours <= 4:
            # Medium commitment: 3-6 months  
            max_timeline_months = 6
        else:
            # High commitment: 1-3 months
            max_timeline_months = 3
        
        # Fix milestone dates to be realistic and start from today
        for i, milestone in enumerate(plan.get('milestones', [])):
            if milestone.get('target_date'):
                try:
                    date_obj = datetime.fromisoformat(milestone['target_date']).date()
                    # Calculate realistic milestone date based on timeline
                    months_from_start = (i + 1) * (max_timeline_months / len(plan.get('milestones', [])))
                    new_date = today + timedelta(days=int(months_from_start * 30))
                    milestone['target_date'] = new_date.strftime('%Y-%m-%d')
                except: 
                    # Fallback: set milestone dates progressively
                    months_from_start = (i + 1) * (max_timeline_months / len(plan.get('milestones', [])))
                    new_date = today + timedelta(days=int(months_from_start * 30))
                    milestone['target_date'] = new_date.strftime('%Y-%m-%d')
        
        # Fix step dates to be realistic and start from today
        for i, step in enumerate(plan.get('steps', [])):
            # Always set a due date, even if the AI didn't provide one
            if not step.get('due_date') or step.get('due_date') == 'None':
                # Calculate realistic step date (spread over the timeline)
                days_from_start = (i + 1) * (max_timeline_months * 30 / len(plan.get('steps', [])))
                new_date = today + timedelta(days=int(days_from_start))
                step['due_date'] = new_date.strftime('%Y-%m-%d')
            else:
                try:
                    date_obj = datetime.fromisoformat(step['due_date']).date()
                    # Calculate realistic step date (spread over the timeline)
                    days_from_start = (i + 1) * (max_timeline_months * 30 / len(plan.get('steps', [])))
                    new_date = today + timedelta(days=int(days_from_start))
                    step['due_date'] = new_date.strftime('%Y-%m-%d')
                except:
                    # Fallback: set step dates progressively
                    days_from_start = (i + 1) * (max_timeline_months * 30 / len(plan.get('steps', [])))
                    new_date = today + timedelta(days=int(days_from_start))
                    step['due_date'] = new_date.strftime('%Y-%m-%d')
            
            # Also fix suggested_day if it's missing or generic
            if (not step.get('suggested_day') or 
                step.get('suggested_day') in ['Any', 'None', 'Mon,Tue,Wed,Thu,Fri', 'Monday,Tuesday,Wednesday,Thursday,Friday'] or
                ',' in str(step.get('suggested_day', ''))):
                # Assign days based on weekly time commitment
                days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                if weekly_hours <= 2:
                    # Low commitment: 2 days per week (Monday, Wednesday)
                    step['suggested_day'] = days_of_week[i % 2 * 2]  # Monday, Wednesday
                elif weekly_hours <= 4:
                    # Medium commitment: 3 days per week (Monday, Wednesday, Friday)
                    step['suggested_day'] = days_of_week[i % 3 * 2]  # Monday, Wednesday, Friday
                else:
                    # High commitment: 4 days per week (Monday, Tuesday, Thursday, Friday)
                    step['suggested_day'] = days_of_week[i % 4]  # Monday, Tuesday, Thursday, Friday
        
        # Limit to 2-3 sessions per week for low time commitments
        if weekly_hours <= 2.5:
            # Group steps by suggested_day and limit to 2-3 days
            days_used = set()
            steps_to_keep = []
            
            for step in plan.get('steps', []):
                day = step.get('suggested_day', 'Monday')
                if len(days_used) < 3 or day in days_used:
                    steps_to_keep.append(step)
                    days_used.add(day)
            
            plan['steps'] = steps_to_keep
        
        # Ensure total weekly minutes doesn't exceed constraint
        total_minutes = sum(step.get('estimate_minutes', 0) for step in plan.get('steps', []))
        if total_minutes > max_weekly_minutes:
            # Scale down all step durations proportionally
            scale_factor = max_weekly_minutes / total_minutes
            for step in plan.get('steps', []):
                current_minutes = step.get('estimate_minutes', 0)
                step['estimate_minutes'] = max(15, int(current_minutes * scale_factor))
        
        # Validate step descriptions are specific and actionable
        for step in plan.get('steps', []):
            title = step.get('title', '')
            description = step.get('description', '')
            minutes = step.get('estimate_minutes', 30)
            goal_title = goal.get('title', 'your goal')
            
            # Check if description is generic and needs improvement
            generic_phrases = [
                "Specific action to move toward",
                "Take steps to achieve",
                "Work on",
                "Practice",
                "Research",
                "Plan",
                "Break this down into specific, actionable steps",
                "Set up your workspace",
                "Follow a clear sequence"
            ]
            
            is_generic = any(phrase in description for phrase in generic_phrases)
            
            if is_generic or len(description.strip()) < 50:
                # Generate a specific, actionable description based on the step title and goal
                step['description'] = self._generate_specific_description(title, goal_title, minutes)
        
        return plan

    def _generate_specific_description(self, title: str, goal: str, minutes: int) -> str:
        """Generate a specific, actionable description for a step"""
        
        # Business-related descriptions
        if any(word in title.lower() for word in ['business', 'start', 'company', 'entrepreneur', 'market', 'research', 'plan']):
            if 'research' in title.lower():
                return f"Research your business idea using Google. Search for '{goal}' + 'problems' and '{goal}' + 'solutions'. Read 5 articles about common challenges in this field. Visit competitor websites and note their pricing. Check Reddit and Facebook groups for customer complaints. Create a simple list of: 1) Top 3 problems people face, 2) How competitors solve them, 3) Pricing ranges. You'll understand the market and find opportunities."
            elif 'plan' in title.lower():
                return f"Create a simple business plan using Google Docs. Write: 1) What problem you solve (1 paragraph), 2) Who your customers are (age, location, interests), 3) How you'll solve it (your product/service), 4) How you'll make money (pricing), 5) What you need to start (tools, skills, money). Use free templates from SCORE.org. You'll have a clear roadmap for your business."
            elif 'validate' in title.lower():
                return f"Validate your business idea using Google Forms. Create a free survey asking: 1) 'What's your biggest problem with {goal.lower()}?', 2) 'How much would you pay to solve this?', 3) 'Would you buy a product that solves this?'. Share on Facebook groups, Reddit, and LinkedIn. Aim for 50 responses. Analyze results to see if people actually want your solution. You'll know if your idea has market demand."
            else:
                return f"Research 5 direct competitors on Google. For each competitor: 1) Visit their website, 2) Note their pricing, 3) Read 10 customer reviews on Google/Yelp, 4) Check their social media (followers, engagement), 5) Identify what they do well and poorly. Create a simple spreadsheet with: Company name, Price, Strengths, Weaknesses, Customer complaints. You'll understand your competitive landscape and find opportunities."
        
        # Language learning descriptions
        elif any(word in title.lower() for word in ['vocabulary', 'language', 'learn', 'practice', 'study']):
            if 'vocabulary' in title.lower():
                return f"Learn 10 new words using spaced repetition. Open Anki or Quizlet, create flashcards for: {goal.lower()} words. For each word: 1) Read the word aloud 3 times, 2) Look at the English meaning, 3) Cover the English and try to remember, 4) Write the word 3 times, 5) Use it in a simple sentence. Review all 10 words at the end. You'll know 10 new words and can use them in basic sentences."
            elif 'practice' in title.lower():
                return f"Practice speaking using HelloTalk or Tandem app. Find a native speaker learning English. Send them a voice message introducing yourself and asking about their day. Listen to their response and try to understand. Ask 3 follow-up questions. Practice for {minutes} minutes total. You'll improve your speaking confidence and pronunciation."
            else:
                return f"Complete a lesson on Duolingo or Babbel. Focus on {goal.lower()} vocabulary and grammar. Complete 1 full lesson (about {minutes} minutes). After each exercise, write down 3 new words you learned. Practice saying them aloud 5 times each. You'll build your {goal.lower()} foundation and vocabulary."
        
        # Fitness descriptions
        elif any(word in title.lower() for word in ['workout', 'exercise', 'run', 'cardio', 'strength', 'fitness']):
            if 'run' in title.lower() or 'cardio' in title.lower():
                return f"Run {minutes//10} minutes at conversational pace. Start with 5-minute walking warm-up. Run at a pace where you can talk in full sentences (not gasping). If you need to walk, that's fine - aim for {minutes} minutes total movement. Cool down with 5 minutes walking. Focus on steady breathing: inhale for 3 steps, exhale for 3 steps. You'll build endurance and feel energized."
            elif 'strength' in title.lower():
                return f"Complete a {minutes}-minute bodyweight workout. Do: 1) 10 push-ups, 2) 15 squats, 3) 10 lunges each leg, 4) 30-second plank, 5) 10 tricep dips. Rest 1 minute between exercises. Repeat the circuit 2-3 times. Focus on proper form over speed. You'll build strength and muscle tone."
            else:
                return f"Complete a {minutes}-minute workout using YouTube. Search 'beginner workout {minutes} minutes'. Choose a video with good reviews. Follow along with the instructor. Modify exercises if needed. Focus on moving your body and having fun. You'll get a complete workout and feel accomplished."
        
        # Writing descriptions
        elif any(word in title.lower() for word in ['write', 'blog', 'article', 'content', 'journal']):
            return f"Write a {minutes*10}-word article about {goal.lower()}. Start with: 1) Write 3 main points you want to cover, 2) Write an opening paragraph that hooks the reader, 3) Write one paragraph for each main point with a personal example, 4) Write a conclusion that summarizes your key message. Use simple, clear language. You'll have a complete article that shares your knowledge."
        
        # Music descriptions
        elif any(word in title.lower() for word in ['guitar', 'piano', 'music', 'practice', 'learn']):
            return f"Learn to play a simple song on your instrument. Find the chords/notes online for 'Happy Birthday' or 'Twinkle Twinkle'. Practice each chord/note: place your fingers correctly, play once, hold for 2 seconds. Then practice the progression slowly. Play the whole song 3 times. Focus on clean notes and steady rhythm. You'll be able to play a real song."
        
        # Cooking descriptions
        elif any(word in title.lower() for word in ['cook', 'meal', 'recipe', 'kitchen']):
            return f"Make a simple, healthy meal. Choose a recipe from AllRecipes.com or Food.com. Gather all ingredients first. Follow the recipe step-by-step. Take your time and focus on one step at a time. Taste as you go and adjust seasoning. You'll have a homemade meal and learn cooking skills."
        
        # Default fallback
        else:
            return f"Complete this {title.lower()} activity. Break it into 3 parts: 1) Preparation (5 minutes) - gather what you need, 2) Main activity ({minutes-10} minutes) - do the core work, 3) Review (5 minutes) - check your progress and plan next steps. Focus on one part at a time. You'll make steady progress toward {goal.lower()}."

    def choose_today_steps(self, context: dict, user_email: str = None) -> dict:
        try:
            can_use, reason = self.can_use_feature("alignment", user_email)
        except Exception:
            can_use = True
        if not can_use:
            from .fallback import FallbackAssistant
            fallback = FallbackAssistant()
            return fallback.fallback_alignment(context)
        prompt = PromptTemplates.alignment_prompt(context)
        out = self._chat_json(prompt)
        if not out:
            from .fallback import FallbackAssistant
            fallback = FallbackAssistant()
            return fallback.fallback_alignment(context)
        return out

    def adapt_plan(self, context: dict, user_email: str = None) -> dict:
        try:
            can_use, reason = self.can_use_feature("plan_adaptation", user_email)
        except Exception:
            can_use = True
        if not can_use:
            return {"change_summary": "No AI available; minimal rule-based reschedule", "diff": []}
        prompt = PromptTemplates.adaptation_prompt(context)
        out = self._chat_json(prompt)
        return out or {"change_summary": "No change", "diff": []} 