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
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                return result[0]['id']
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
                    "order": "target_date.asc"
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
