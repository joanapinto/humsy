"""
Prompt Templates for Focus Companion AI Assistant
Provides structured prompts for generating personalized insights and recommendations
"""

from typing import Dict, List

class PromptTemplates:
    """Collection of prompt templates for different AI interactions"""
    
    @staticmethod
    def mood_analysis_prompt(mood_data: List[Dict], user_goal: str) -> str:
        """Generate prompt for mood pattern analysis"""
        return f"""
        Analyze the following mood data for a user focused on: {user_goal}
        
        Mood Entries: {mood_data}
        
        Please provide:
        1. Key patterns in mood over time
        2. Correlation between mood and productivity
        3. Specific recommendations for improving mood and focus
        4. Encouraging insights based on positive trends
        
        Focus on actionable, supportive advice that aligns with their goal.
        """
    
    @staticmethod
    def daily_recommendation_prompt(user_profile: Dict, recent_data: Dict) -> str:
        """Generate prompt for daily recommendations"""
        return f"""
        User Profile: {user_profile}
        Recent Activity: {recent_data}
        
        Generate a personalized daily recommendation that:
        1. Acknowledges their current situation and energy level
        2. Provides specific, actionable advice
        3. Maintains their preferred tone: {user_profile.get('tone', 'Gentle & Supportive')}
        4. Supports their goal: {user_profile.get('goal', 'Improve focus')}
        5. Is encouraging and motivating
        
        Keep it concise and practical.
        """
    
    @staticmethod
    def weekly_reflection_prompt(weekly_data: Dict, user_goal: str) -> str:
        """Generate prompt for weekly reflection insights"""
        return f"""
        Weekly Summary: {weekly_data}
        User Goal: {user_goal}
        
        Provide a thoughtful weekly reflection that:
        1. Celebrates achievements and progress
        2. Identifies patterns and insights
        3. Offers constructive feedback
        4. Suggests improvements for next week
        5. Maintains an encouraging, growth-oriented tone
        
        Focus on both emotional wellness and goal progress.
        """
    
    @staticmethod
    def focus_optimization_prompt(checkin_data: List[Dict], mood_data: List[Dict]) -> str:
        """Generate prompt for focus optimization advice"""
        return f"""
        Check-in Data: {checkin_data}
        Mood Data: {mood_data}
        
        Analyze patterns to provide focus optimization advice:
        1. Identify optimal times for deep work
        2. Suggest energy management strategies
        3. Recommend break patterns
        4. Address common focus blockers
        5. Provide environment optimization tips
        
        Base recommendations on actual user patterns and preferences.
        """
    
    @staticmethod
    def sleep_optimization_prompt(sleep_data: List[Dict], energy_data: List[Dict]) -> str:
        """Generate prompt for sleep and energy optimization"""
        return f"""
        Sleep Quality Data: {sleep_data}
        Energy Level Data: {energy_data}
        
        Provide sleep and energy optimization advice:
        1. Identify sleep quality patterns
        2. Suggest sleep routine improvements
        3. Recommend energy-boosting activities
        4. Address sleep-energy correlations
        5. Provide practical lifestyle adjustments
        
        Focus on evidence-based, practical recommendations.
        """
    
    @staticmethod
    def goal_progress_prompt(user_goal: str, progress_data: Dict) -> str:
        """Generate prompt for goal progress analysis"""
        return f"""
        User Goal: {user_goal}
        Progress Data: {progress_data}
        
        Analyze progress toward the user's goal:
        1. Assess current progress level
        2. Identify successful strategies
        3. Suggest adjustments or improvements
        4. Provide motivation and encouragement
        5. Recommend next steps
        
        Be specific and actionable while maintaining encouragement.
        """
    
    @staticmethod
    def stress_management_prompt(mood_data: List[Dict], checkin_data: List[Dict]) -> str:
        """Generate prompt for stress management advice"""
        return f"""
        Mood Data: {mood_data}
        Check-in Data: {checkin_data}
        
        Provide stress management advice based on patterns:
        1. Identify stress triggers and patterns
        2. Suggest coping strategies
        3. Recommend preventive measures
        4. Provide relaxation techniques
        5. Suggest lifestyle adjustments
        
        Focus on practical, accessible stress management techniques.
        """
    
    @staticmethod
    def productivity_insights_prompt(all_data: Dict) -> str:
        """Generate prompt for productivity insights"""
        return f"""
        User Context: {all_data}
        
        Based on this user's profile, mood patterns, and check-in data, provide ONE specific productivity tip that:
        - Addresses their current situation and energy drainers
        - Is practical and immediately actionable
        - Considers their availability and preferences
        - Helps them work toward their goals more effectively
        
        Keep the response focused and concise.
        """
    
    @staticmethod
    def morning_checkin_prompt(user_profile: Dict, previous_data: Dict, current_checkin: Dict) -> str:
        """Generate prompt for morning check-in analysis and recommendations"""
        return f"""
        User Profile: {user_profile}
        Previous Evening Check-in: {previous_data}
        Current Morning Check-in: {current_checkin}
        
        Provide morning-focused insights and recommendations:
        
        1. **Sleep Analysis**: 
           - Assess sleep quality impact on daily energy
           - Suggest sleep routine improvements if needed
           - Connect sleep patterns to productivity
        
        2. **Energy Assessment**:
           - Analyze current energy level for the day ahead
           - Suggest energy-boosting activities if low
           - Recommend optimal timing for important tasks
        
        3. **Focus Planning**:
           - Help refine the day's focus goals
           - Suggest task prioritization based on energy
           - Recommend morning routine adjustments
        
        4. **Motivation & Mindset**:
           - Provide encouraging morning motivation
           - Address any concerns from previous day
           - Set positive tone for the day ahead
        
        5. **Wellness Tips**:
           - Suggest morning wellness practices
           - Recommend hydration and nutrition
           - Suggest movement or exercise ideas
        
        Tone: {user_profile.get('tone', 'Gentle & Supportive')}
        Goal: {user_profile.get('goal', 'Improve focus and productivity')}
        
        Keep recommendations practical and actionable for the morning hours.
        """
    
    @staticmethod
    def afternoon_checkin_prompt(user_profile: Dict, morning_data: Dict, current_checkin: Dict) -> str:
        """Generate prompt for afternoon check-in analysis and recommendations"""
        return f"""
        User Profile: {user_profile}
        Morning Check-in: {morning_data}
        Current Afternoon Check-in: {current_checkin}
        
        Provide afternoon-focused insights and recommendations:
        
        1. **Progress Assessment**:
           - Evaluate progress against morning goals
           - Identify what's working well
           - Highlight areas needing adjustment
        
        2. **Energy Management**:
           - Analyze energy changes since morning
           - Suggest energy maintenance strategies
           - Recommend optimal afternoon activities
        
        3. **Plan Adjustment**:
           - Help refine remaining day's plan
           - Suggest task reprioritization if needed
           - Recommend realistic afternoon goals
        
        4. **Break & Recovery**:
           - Assess break needs and timing
           - Suggest effective break activities
           - Recommend stress management techniques
        
        5. **Focus Optimization**:
           - Identify focus challenges and solutions
           - Suggest environment adjustments
           - Recommend focus techniques for afternoon
        
        6. **Motivation Boost**:
           - Provide mid-day encouragement
           - Celebrate progress made so far
           - Maintain momentum for rest of day
        
        Tone: {user_profile.get('tone', 'Gentle & Supportive')}
        Goal: {user_profile.get('goal', 'Improve focus and productivity')}
        
        Focus on maintaining momentum and optimizing the remaining day.
        """
    
    @staticmethod
    def evening_checkin_prompt(user_profile: Dict, daily_journey: Dict, current_checkin: Dict) -> str:
        """Generate prompt for evening check-in analysis and recommendations"""
        return f"""
        User Profile: {user_profile}
        Daily Journey (Morning + Afternoon): {daily_journey}
        Current Evening Check-in: {current_checkin}
        
        Provide evening-focused insights and recommendations:
        
        1. **Day Reflection**:
           - Celebrate accomplishments and progress
           - Acknowledge challenges and learning
           - Provide perspective on the day's journey
        
        2. **Emotional Processing**:
           - Help process any difficult emotions
           - Validate feelings and experiences
           - Suggest healthy coping strategies
        
        3. **Wellness Assessment**:
           - Evaluate overall daily wellness
           - Suggest evening relaxation techniques
           - Recommend stress relief activities
        
        4. **Tomorrow Preparation**:
           - Help plan for tomorrow based on today's learnings
           - Suggest adjustments to routine or approach
           - Set positive intentions for next day
        
        5. **Sleep Preparation**:
           - Suggest evening routine improvements
           - Recommend sleep hygiene practices
           - Help wind down from the day
        
        6. **Growth & Learning**:
           - Identify key learnings from the day
           - Suggest areas for personal growth
           - Encourage self-compassion and kindness
        
        Tone: {user_profile.get('tone', 'Gentle & Supportive')}
        Goal: {user_profile.get('goal', 'Improve focus and productivity')}
        
        Focus on reflection, processing, and preparation for rest and tomorrow.
        """
    
    @staticmethod
    def daily_summary_prompt(user_profile: Dict, complete_daily_data: Dict) -> str:
        """Generate prompt for complete daily summary and insights"""
        return f"""
        User Profile: {user_profile}
        Complete Daily Data (Morning + Afternoon + Evening): {complete_daily_data}
        
        Provide a comprehensive daily summary and insights:
        
        1. **Daily Overview**:
           - Summarize the complete day's journey
           - Highlight key moments and transitions
           - Identify overall daily theme or pattern
        
        2. **Goal Progress**:
           - Assess progress toward user's main goal
           - Identify successful strategies used
           - Suggest improvements for future days
        
        3. **Pattern Recognition**:
           - Identify recurring patterns or themes
           - Connect morning energy to afternoon productivity
           - Analyze evening reflection patterns
        
        4. **Wellness Assessment**:
           - Evaluate overall daily wellness
           - Identify stress points and coping strategies
           - Suggest wellness improvements
        
        5. **Tomorrow's Preparation**:
           - Suggest specific improvements for tomorrow
           - Recommend routine adjustments
           - Set positive intentions and goals
        
        6. **Growth Insights**:
           - Identify personal growth opportunities
           - Suggest habit improvements
           - Encourage continued progress
        
        Tone: {user_profile.get('tone', 'Gentle & supportive')}
        Goal: {user_profile.get('goal', 'Improve focus and productivity')}
        
        Provide a balanced, encouraging summary that celebrates progress while suggesting improvements.
        """

    @staticmethod
    def goal_plan_prompt(goal: dict) -> str:
        return PromptTemplates._personalized_plan_prompt(goal)
    
    @staticmethod
    def _personalized_plan_prompt(goal: dict) -> str:
        from datetime import datetime, timedelta
        
        # Calculate realistic timeline based on weekly time commitment
        weekly_time = goal.get('weekly_time', 'Not specified')
        deadline = goal.get('deadline', None)
        
        # Parse weekly time to get hours per week
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
            weekly_hours = 3  # Default assumption
        
        # Calculate realistic timeline if no deadline provided
        if not deadline or deadline == 'No deadline set':
            # Estimate total training time needed based on goal complexity
            goal_title = goal.get('title', '').lower()
            if any(word in goal_title for word in ['marathon', '26.2', '42k']):
                total_hours_needed = 200  # Marathon training typically needs 200+ hours
            elif any(word in goal_title for word in ['half', '13.1', '21k']):
                total_hours_needed = 100
            elif any(word in goal_title for word in ['5k', '10k']):
                total_hours_needed = 50
            elif any(word in goal_title for word in ['learn', 'study', 'course']):
                total_hours_needed = 80  # Learning goals typically need 80+ hours
            elif any(word in goal_title for word in ['weight', 'muscle', 'strength']):
                total_hours_needed = 120  # Fitness goals typically need 120+ hours
            else:
                total_hours_needed = 60  # Default for other goals
            
            weeks_needed = max(12, int(total_hours_needed / weekly_hours))  # Minimum 12 weeks
            start_date = datetime.now()
            end_date = start_date + timedelta(weeks=weeks_needed)
            calculated_deadline = end_date.strftime('%Y-%m-%d')
        else:
            calculated_deadline = deadline
        
        return f"""
You are an expert personal coach and planning specialist. Analyze the user's goal and create a completely personalized, actionable plan based on their specific situation, needs, and preferences.

USER'S GOAL & CONTEXT:
- **What they want to achieve:** {goal.get('title', 'Not specified')}
- **Why this matters to them:** {goal.get('why_matters', 'Not specified')}
- **How they'll know they succeeded:** {goal.get('success_metric', 'Not specified')}
- **Where they're starting from:** {goal.get('starting_point', 'Not specified')}
- **When they want to achieve it:** {goal.get('deadline', 'No deadline set')}
- **Realistic timeline calculated:** {calculated_deadline} (based on {weekly_hours} hours/week)

THEIR LIFESTYLE & PREFERENCES:
- **Weekly time available:** {goal.get('weekly_time', 'Not specified')} ({weekly_hours} hours/week)
- **Best energy time:** {goal.get('energy_time', 'Not specified')}
- **Days they want to keep free:** {goal.get('free_days', 'None specified')}
- **Preferred intensity:** {goal.get('intensity', 'Balanced')}

WHAT MOTIVATES & CHALLENGES THEM:
- **What energizes them:** {goal.get('joy_sources', [])}
- **What drains their energy:** {goal.get('energy_drainers', [])}
- **Potential obstacles:** {goal.get('obstacles', 'None specified')}
- **Resources they already have:** {goal.get('resources', 'None specified')}

🚨 CRITICAL PLANNING RULES - MUST FOLLOW EXACTLY:
1. **TIME CONSTRAINT VIOLATION = FAILURE**: If user has {weekly_hours} hours/week, you MUST schedule exactly 2-3 sessions per week, NEVER daily. Total minutes MUST NOT exceed {int(weekly_hours * 60)} minutes per week.
2. **DAILY SCHEDULING = FORBIDDEN**: For {weekly_hours} hours/week, schedule activities on ONLY 2-3 specific days (e.g., "Tuesday" and "Thursday"), NEVER schedule activities for all 7 days.
3. **SPECIFIC INSTRUCTIONS REQUIRED**: Every step MUST include exact details: distance, pace, duration, specific exercises. NO vague terms like "long run" or "training".
4. **DATE REQUIREMENT**: ALL dates MUST start from today ({datetime.now().strftime('%Y-%m-%d')}) and go forward. NEVER use past dates or dates more than 12 months away.
5. **FREE DAYS RESPECT**: If user specified free days, NEVER schedule activities on those days.
6. **VALIDATION**: Before returning, verify total weekly minutes ≤ {int(weekly_hours * 60)} and activities scheduled on ≤ 3 days.

DETAILED PLANNING REQUIREMENTS:
- Create 4-6 meaningful milestones that logically build toward their specific goal
- Break each milestone into 3-8 highly specific, actionable steps taking in consideration that the user has {weekly_hours} hours/week
- Schedule activities on 2-4 days per week maximum (based on their time commitment, moods, time per week)
- Include specific, detailed instructions for each step
- Schedule steps on specific days of the week based on their preferences
- Incorporate their joy sources naturally into specific activities
- Address their specific obstacles with concrete solutions
- Use their existing resources in specific ways
- Make the timeline realistic based on their weekly time commitment
- Include preparation, execution, and follow-up activities
- Add variety to prevent boredom while maintaining focus

WEEKLY SCHEDULING EXAMPLES:
- **1-2 hours/week**: 2 sessions of 30-60 minutes each
- **2-3 hours/week**: 2-3 sessions of 45-60 minutes each  
- **3-4 hours/week**: 3-4 sessions of 45-60 minutes each
- **4+ hours/week**: 4-5 sessions of 45-90 minutes each

            PRACTICAL INSTRUCTION EXAMPLES:
            
            **Language Learning (Polish example):**
            Instead of "Daily Vocabulary Practice" → "Learn 10 new Polish words using spaced repetition. Open Anki or Quizlet, create flashcards for: dzień (day), noc (night), dom (house), szkoła (school), praca (work), rodzina (family), przyjaciel (friend), jedzenie (food), woda (water), miłość (love). For each word: 1) Read the Polish word aloud 3 times, 2) Look at the English meaning, 3) Cover the English and try to remember, 4) Write the word 3 times, 5) Use it in a simple sentence. Review all 10 words at the end. You'll know 10 new Polish words and can use them in basic sentences."
            
            **Fitness (Running example):**
            Instead of "cardio workout" → "Run 2 miles at conversational pace. Start with 5-minute walking warm-up. Run at a pace where you can talk in full sentences (not gasping). If you need to walk, that's fine - aim for 20 minutes total movement. Cool down with 5 minutes walking. Focus on steady breathing: inhale for 3 steps, exhale for 3 steps. You'll build endurance and feel energized."
            
            **Writing (Blog example):**
            Instead of "write blog post" → "Write a 300-word article about your topic. Start with: 1) Write 3 main points you want to cover, 2) Write an opening paragraph that hooks the reader, 3) Write one paragraph for each main point with a personal example, 4) Write a conclusion that summarizes your key message. Use simple, clear language. You'll have a complete article that shares your knowledge."
            
            **Music (Guitar example):**
            Instead of "practice guitar" → "Learn to play 'Happy Birthday' on guitar. Find the chords online (G, D, D7, G). Practice each chord: place your fingers correctly, strum down once, hold for 2 seconds. Then practice the chord progression: G-G-D-D-G-G-D7-D7-G. Play slowly and focus on clean chord changes. You'll be able to play a real song for someone's birthday."
            
            **Cooking (Healthy meal example):**
            Instead of "cook healthy meal" → "Make a simple stir-fry with vegetables and protein. Heat 1 tablespoon oil in a pan. Add chopped onion and garlic, cook 2 minutes. Add your protein (chicken, tofu, or beans), cook 5 minutes. Add mixed vegetables (bell peppers, broccoli, carrots), cook 5 more minutes. Season with soy sauce, ginger, and a pinch of salt. Serve over rice or noodles. You'll have a nutritious, homemade meal in 20 minutes."

REQUIRED FORMAT FOR EVERY STEP:
Each step description MUST be:
1. **SPECIFIC**: Exact steps with numbers, times, and clear actions
2. **PRACTICAL**: Real tools, apps, or methods the user can actually use
3. **ACHIEVABLE**: Something they can complete in the time given
4. **MEANINGFUL**: Actually helps them progress toward their goal
5. **CLEAR**: Easy to read and follow without confusion

Focus on WHAT to do, HOW to do it, and WHY it matters. Avoid generic advice like "set up workspace" or "take breaks" unless it's truly necessary for that specific activity.

Return STRICT JSON only with this schema:
{{
  "milestones": [{{"title": str, "description": str, "target_date": "YYYY-MM-DD"}}],
  "steps": [{{ 
      "milestone_title": str,
      "title": str,
      "description": str,
      "estimate_minutes": int,
      "suggested_day": str,
      "due_date": "YYYY-MM-DD"
  }}]
}}
""".strip()

    @staticmethod
    def alignment_prompt(context: dict) -> str:
        return f"""
Given today's check-in, mood history, and the active goal plan, select 1–3 steps for TODAY and return:
{{
  "alignment_score": int,
  "today_steps": [{{"step_id": int, "title": str}}],
  "adjustments": [str],
  "why": str
}}
Context: {context}
""".strip()

    @staticmethod
    def adaptation_prompt(context: dict) -> str:
        return f"""
Given repeated blockers and skipped steps, adapt the plan minimally. Return changes as:
{{
  "change_summary": str,
  "diff": [
    {{"action": "reschedule|split|scope_down|merge", "step_id": int, "details": str}}
  ]
}}
Context: {context}
""".strip()

class ResponseFormats:
    """Standard response formats for consistent AI outputs"""
    
    @staticmethod
    def daily_recommendation_format() -> str:
        return """
        Format your response as:
        
        🌟 **Today's Focus**: [Main recommendation]
        
        💡 **Quick Tips**:
        - [Tip 1]
        - [Tip 2]
        - [Tip 3]
        
        🎯 **Remember**: [Goal reminder]
        """
    
    @staticmethod
    def weekly_summary_format() -> str:
        return """
        Format your response as:
        
        📊 **This Week's Progress**:
        [Summary of achievements and patterns]
        
        🎉 **Celebrations**:
        [Positive highlights]
        
        🔍 **Insights**:
        [Key learnings and patterns]
        
        🚀 **Next Week's Focus**:
        [Specific recommendations]
        """
    
    @staticmethod
    def mood_insight_format() -> str:
        return """
        Format your response as:
        
        📈 **Mood Patterns**:
        [Key patterns identified]
        
        💭 **Insights**:
        [What these patterns mean]
        
        🛠️ **Recommendations**:
        [Actionable advice]
        
        🌟 **Positive Notes**:
        [Encouraging observations]
        """
    
    @staticmethod
    def morning_checkin_format() -> str:
        return """
        Format your response as:
        
        🌅 **Morning Energy Assessment**:
        [Analysis of sleep and energy]
        
        🎯 **Focus Planning**:
        [Specific focus recommendations]
        
        💪 **Motivation & Mindset**:
        [Encouraging morning message]
        
        🌟 **Wellness Tips**:
        [Morning wellness suggestions]
        
        📋 **Today's Action Plan**:
        [3 specific actionable steps]
        """
    
    @staticmethod
    def afternoon_checkin_format() -> str:
        return """
        Format your response as:
        
        📊 **Progress Assessment**:
        [Evaluation of morning progress]
        
        🔋 **Energy Management**:
        [Energy optimization suggestions]
        
        🔄 **Plan Adjustments**:
        [Specific plan refinements]
        
        ☕ **Break & Recovery**:
        [Break and stress management tips]
        
        🚀 **Afternoon Focus**:
        [3 specific afternoon priorities]
        """
    
    @staticmethod
    def evening_checkin_format() -> str:
        return """
        Format your response as:
        
        🌆 **Day Reflection**:
        [Celebration of accomplishments]
        
        💭 **Emotional Processing**:
        [Support for feelings and challenges]
        
        🌙 **Evening Wellness**:
        [Relaxation and preparation tips]
        
        🌟 **Tomorrow's Preparation**:
        [Specific improvements for tomorrow]
        
        📝 **Key Learnings**:
        [3 important insights from today]
        """
    
    @staticmethod
    def daily_summary_format() -> str:
        return """
        Format your response as:
        
        📅 **Daily Overview**:
        [Complete day summary]
        
        🎯 **Goal Progress**:
        [Progress toward main goal]
        
        🔍 **Pattern Recognition**:
        [Key patterns and insights]
        
        💚 **Wellness Assessment**:
        [Overall wellness evaluation]
        
        🚀 **Tomorrow's Focus**:
        [3 specific improvements]
        
        🌟 **Growth Celebration**:
        [Personal growth highlights]
        """

    @staticmethod
    def ai_task_planning_prompt(context: Dict, checkin_data: Dict, recent_moods: List[Dict], recent_checkins: List[Dict]) -> str:
        """Generate comprehensive prompt for AI task planning"""
        current_hour = context.get('current_hour', 12)
        time_period = context.get('time_period', 'morning')
        
        return f"""
You are an expert productivity coach and life strategist who creates deeply personalized, thoughtful daily plans. Your goal is to help users feel empowered, not overwhelmed, while making meaningful progress toward their goals.

USER CONTEXT:
- Primary Goal: {context.get('user_goal', 'Improve focus and productivity')}
- Communication Style: {context.get('user_tone', 'Friendly')}
- Available Time: {context.get('availability', '2-4 hours')}
- Current Time: {time_period} ({current_hour}:00)
- Life Situation: {context.get('situation', 'Not specified')}

CURRENT STATE ANALYSIS:
- Sleep Quality: {checkin_data.get('sleep_quality', 'Not specified')}
- Energy Level: {checkin_data.get('energy_level', 'Not specified')}
- Emotional State: {checkin_data.get('current_feeling', 'Not specified')}
- Day Progress: {checkin_data.get('day_progress', 'Not specified')}
- Main Focus: {checkin_data.get('focus_today', 'Not specified')}

PERSONAL PREFERENCES & PATTERNS:
- Energy Drainers (Avoid): {context.get('energy_drainers', [])}
- Joy Sources (Incorporate): {context.get('joy_sources', [])}
- Small Habit: {context.get('small_habit', '')}
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

CREATE A PERSONALIZED {time_period.upper()} PLAN THAT:
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

