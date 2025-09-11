"""
Supabase REST API Manager for Humsy
Handles all data storage and retrieval operations using Supabase REST API
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st

class SupabaseManager:
    """Manages Supabase REST API operations for Humsy"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
        self.supabase_url, self.supabase_key = self._parse_connection_string()
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        self.init_database()
    
    def _get_connection_string(self) -> str:
        """Get database connection string from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first (for Streamlit Cloud)
            return st.secrets.get("database_url", "")
        except:
            pass
        
        # Fallback to environment variable
        return os.getenv('DATABASE_URL', '')
    
    def _parse_connection_string(self):
        """Parse PostgreSQL connection string to get Supabase URL and key"""
        # For now, we'll use a simpler approach with environment variables
        try:
            supabase_url = st.secrets.get("supabase_url", "")
            supabase_key = st.secrets.get("supabase_key", "")
            return supabase_url, supabase_key
        except:
            # Fallback - we'll need to get these from Supabase dashboard
            return "", ""
    
    def init_database(self):
        """Initialize the database with all required tables"""
        # Supabase tables are created through the dashboard
        # This is just a placeholder for compatibility
        pass
    
    def create_goal(self, user_email: str, goal_data: Dict) -> int:
        """Create a new goal and return its ID"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Prepare data for Supabase
            data = {
                "user_email": user_email,
                "title": goal_data.get('title', ''),
                "why_matters": goal_data.get('why_matters', ''),
                "deadline": goal_data.get('deadline'),
                "success_metric": goal_data.get('success_metric', ''),
                "starting_point": goal_data.get('starting_point', ''),
                "weekly_time": goal_data.get('weekly_time', ''),
                "energy_time": goal_data.get('energy_time', ''),
                "free_days": goal_data.get('free_days', ''),
                "intensity": goal_data.get('intensity', ''),
                "joy_sources": goal_data.get('joy_sources', []),
                "energy_drainers": goal_data.get('energy_drainers', []),
                "therapy_coaching": goal_data.get('therapy_coaching', ''),
                "obstacles": goal_data.get('obstacles', ''),
                "resources": goal_data.get('resources', ''),
                "reminder_preference": goal_data.get('reminder_preference', ''),
                "auto_adapt": goal_data.get('auto_adapt', True)
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/goals",
                headers=self.headers,
                json=data,
                params={"select": "id"}  # Return the ID in the response
            )
            
            if response.status_code == 201:
                if response.text.strip():
                    try:
                        result = response.json()
                        if result and len(result) > 0:
                            return result[0]['id']
                        else:
                            return "temp_supabase_id"
                    except Exception as json_error:
                        raise Exception(f"Failed to parse JSON response: {response.text}")
                else:
                    # Empty response - this is normal for Supabase
                    return "temp_supabase_id"
            else:
                raise Exception(f"Failed to create goal: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to create goal: {str(e)}")
            raise
    
    def get_active_goal(self, user_email: str) -> Optional[Dict]:
        """Get the most recent active goal for a user"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/goals",
                headers=self.headers,
                params={
                    "user_email": f"eq.{user_email}",
                    "order": "created_at.desc",
                    "limit": "1"
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    return results[0]
                return None
            else:
                raise Exception(f"Failed to get active goal: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get active goal: {str(e)}")
            return None
    
    def save_milestones(self, goal_id: int, milestones: List[Dict]):
        """Save milestones for a goal"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Clear existing milestones
            requests.delete(
                f"{self.supabase_url}/rest/v1/milestones",
                headers=self.headers,
                params={"goal_id": f"eq.{goal_id}"}
            )
            
            # Insert new milestones
            for milestone in milestones:
                data = {
                    "goal_id": goal_id,
                    "title": milestone.get('title', ''),
                    "description": milestone.get('description', ''),
                    "target_date": milestone.get('target_date')
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/milestones",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 201:
                    raise Exception(f"Failed to save milestone: {response.text}")
                    
        except Exception as e:
            st.error(f"Failed to save milestones: {str(e)}")
            raise
    
    def save_steps(self, goal_id: int, steps: List[Dict]):
        """Save steps for a goal"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Clear existing steps
            requests.delete(
                f"{self.supabase_url}/rest/v1/steps",
                headers=self.headers,
                params={"goal_id": f"eq.{goal_id}"}
            )
            
            # Insert new steps
            for step in steps:
                data = {
                    "goal_id": goal_id,
                    "title": step.get('title', ''),
                    "description": step.get('description', ''),
                    "due_date": step.get('due_date'),
                    "suggested_day": step.get('suggested_day', ''),
                    "estimated_time": step.get('estimated_time', 0),
                    "estimate_minutes": step.get('estimate_minutes', 0)
                }
                
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/steps",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 201:
                    raise Exception(f"Failed to save step: {response.text}")
                    
        except Exception as e:
            st.error(f"Failed to save steps: {str(e)}")
            raise
    
    def get_milestones(self, goal_id: int) -> List[Dict]:
        """Get milestones for a goal"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/milestones",
                headers=self.headers,
                params={
                    "goal_id": f"eq.{goal_id}",
                    "order": "id.asc"  # Fallback to id ordering if seq doesn't exist
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get milestones: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get milestones: {str(e)}")
            return []
    
    def get_steps(self, goal_id: int) -> List[Dict]:
        """Get steps for a goal"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/steps",
                headers=self.headers,
                params={
                    "goal_id": f"eq.{goal_id}",
                    "order": "due_date.asc,suggested_day.asc"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get steps: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get steps: {str(e)}")
            return []
    
    def update_goal(self, goal_id: int, updates: Dict):
        """Update a goal with new data"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/goals",
                headers=self.headers,
                params={"id": f"eq.{goal_id}"},
                json=updates
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to update goal: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to update goal: {str(e)}")
            raise
    
    def list_plan(self, goal_id: int) -> tuple[list[dict], list[dict]]:
        """Get both milestones and steps for a goal"""
        milestones = self.get_milestones(goal_id)
        steps = self.get_steps(goal_id)
        return milestones, steps
    
    def clear_plan(self, goal_id: int):
        """Clear all milestones and steps for a goal"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Delete steps first
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/steps",
                headers=self.headers,
                params={"goal_id": f"eq.{goal_id}"}
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to clear steps: {response.text}")
            
            # Delete milestones
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/milestones",
                headers=self.headers,
                params={"goal_id": f"eq.{goal_id}"}
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to clear milestones: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to clear plan: {str(e)}")
            raise
    
    @property
    def db_path(self):
        """Compatibility property for SQLite-style access"""
        # Return a dummy path since Supabase doesn't use local files
        return "supabase://remote"
    
    def save_mood_log(self, user_email: str, mood: str, intensity: int, notes: str = None):
        """Save a mood log entry"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            data = {
                "user_email": user_email,
                "mood": mood,
                "intensity": intensity,
                "notes": notes
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/mood_logs",
                headers=self.headers,
                json=data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to save mood log: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to save mood log: {str(e)}")
            raise
    
    def get_mood_logs(self, user_email: str, days: int = 30) -> List[Dict]:
        """Get mood logs for a user"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/mood_logs",
                headers=self.headers,
                params={
                    "user_email": f"eq.{user_email}",
                    "order": "created_at.desc",
                    "limit": "1000"  # Adjust as needed
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get mood logs: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get mood logs: {str(e)}")
            return []
    
    def save_checkin(self, user_email: str, checkin_data: Dict[str, Any]):
        """Save a check-in entry"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Convert energy level string to integer
            energy_level = checkin_data.get('energy_level')
            if isinstance(energy_level, str):
                energy_mapping = {
                    "Very low": 1,
                    "Low": 2, 
                    "Moderate": 3,
                    "Good": 4,
                    "High": 5
                }
                energy_level = energy_mapping.get(energy_level, 3)  # Default to 3 if not found

            data = {
                "user_email": user_email,
                "goal_id": checkin_data.get('goal_id'),
                "completed_steps": checkin_data.get('completed_steps'),
                "skipped_steps": checkin_data.get('skipped_steps'),
                "notes": checkin_data.get('notes'),
                "mood": checkin_data.get('mood'),
                "energy_level": energy_level
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/checkins",
                headers=self.headers,
                json=data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to save check-in: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to save check-in: {str(e)}")
            raise
    
    def get_checkins(self, user_email: str, days: int = 30) -> List[Dict]:
        """Get check-ins for a user"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/checkins",
                headers=self.headers,
                params={
                    "user_email": f"eq.{user_email}",
                    "order": "created_at.desc",
                    "limit": "1000"  # Adjust as needed
                }
            )
            
            if response.status_code == 200:
                checkins = response.json()
                # Convert energy level integers back to strings
                energy_mapping = {
                    1: "Very low",
                    2: "Low",
                    3: "Moderate", 
                    4: "Good",
                    5: "High"
                }
                for checkin in checkins:
                    if 'energy_level' in checkin and isinstance(checkin['energy_level'], int):
                        checkin['energy_level'] = energy_mapping.get(checkin['energy_level'], "Moderate")
                return checkins
            else:
                raise Exception(f"Failed to get check-ins: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get check-ins: {str(e)}")
            return []
    
    def mark_step_status(self, step_id: int, status: str):
        """Mark a step as completed or update its status"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            data = {
                "status": status,
                "last_scheduled": datetime.now().isoformat()
            }
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/steps",
                headers=self.headers,
                params={"id": f"eq.{step_id}"},
                json=data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update step status: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to mark step status: {str(e)}")
            raise
    
    def get_today_candidates(self, user_email: str, date_str: str) -> list[dict]:
        """Get today's candidate steps for the user"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            # Get the active goal first
            goal = self.get_active_goal(user_email)
            if not goal:
                return []
            
            # Get weekday from date string
            wd = datetime.fromisoformat(date_str).strftime("%a")  # e.g., Mon
            
            # Get pending steps for this goal
            response = requests.get(
                f"{self.supabase_url}/rest/v1/steps",
                headers=self.headers,
                params={
                    "goal_id": f"eq.{goal['id']}",
                    "status": "in.(pending,in_progress)",
                    "order": "due_date.asc,estimate_minutes.asc"
                }
            )
            
            if response.status_code == 200:
                steps = response.json()
                # Filter steps by suggested_day
                def day_ok(s):
                    sd = (s.get("suggested_day") or "Any")
                    return sd == "Any" or wd in sd.split(",")
                return [s for s in steps if day_ok(s)]
            else:
                raise Exception(f"Failed to get today's candidates: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get today's candidates: {str(e)}")
            return []
    
    def record_adaptation(self, goal_id: int, checkin_ts: str, alignment_score: int, reason: str, change_summary: str, diff_json: str):
        """Record a plan adaptation"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise Exception("Supabase URL or key not configured")
            
            data = {
                "goal_id": goal_id,
                "checkin_timestamp": checkin_ts,
                "alignment_score": alignment_score,
                "reason": reason,
                "change_summary": change_summary,
                "diff_json": diff_json
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/plan_adaptations",
                headers=self.headers,
                json=data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to record adaptation: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to record adaptation: {str(e)}")
            raise
