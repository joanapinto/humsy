"""
PostgreSQL Database Manager for Humsy
Handles all data storage and retrieval operations with Supabase PostgreSQL
"""

import os
import json
import asyncio
import asyncpg
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st

class PostgreSQLManager:
    """Manages PostgreSQL database operations for Humsy"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
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
    
    async def _get_connection(self):
        """Get database connection"""
        if not self.connection_string:
            raise Exception("No database connection string found. Please configure DATABASE_URL in secrets.")
        
        return await asyncpg.connect(self.connection_string)
    
    def init_database(self):
        """Initialize the database with all required tables"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Goals table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS goals (
                            id SERIAL PRIMARY KEY,
                            user_email TEXT NOT NULL,
                            title TEXT NOT NULL,
                            why_matters TEXT,
                            deadline DATE,
                            success_metric TEXT,
                            starting_point TEXT,
                            weekly_time TEXT,
                            energy_time TEXT,
                            free_days TEXT,
                            intensity TEXT,
                            joy_sources JSONB,
                            energy_drainers JSONB,
                            therapy_coaching TEXT,
                            obstacles TEXT,
                            resources TEXT,
                            reminder_preference TEXT,
                            auto_adapt BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Milestones table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS milestones (
                            id SERIAL PRIMARY KEY,
                            goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                            title TEXT NOT NULL,
                            description TEXT,
                            target_date DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Steps table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS steps (
                            id SERIAL PRIMARY KEY,
                            goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                            title TEXT NOT NULL,
                            description TEXT,
                            due_date DATE,
                            suggested_day TEXT,
                            estimated_time INTEGER,
                            estimate_minutes INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Mood logs table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS mood_logs (
                            id SERIAL PRIMARY KEY,
                            user_email TEXT NOT NULL,
                            mood TEXT NOT NULL,
                            intensity INTEGER NOT NULL,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Check-ins table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS checkins (
                            id SERIAL PRIMARY KEY,
                            user_email TEXT NOT NULL,
                            goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                            completed_steps JSONB,
                            skipped_steps JSONB,
                            notes TEXT,
                            mood TEXT,
                            energy_level INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
        except Exception as e:
            st.error(f"Database initialization failed: {str(e)}")
            raise
    
    def create_goal(self, user_email: str, goal_data: Dict) -> int:
        """Create a new goal and return its ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO goals (
                            user_email, title, why_matters, deadline, success_metric,
                            starting_point, weekly_time, energy_time, free_days, intensity,
                            joy_sources, energy_drainers, therapy_coaching, obstacles,
                            resources, reminder_preference, auto_adapt
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING id
                    """, (
                        user_email,
                        goal_data.get('title', ''),
                        goal_data.get('why_matters', ''),
                        goal_data.get('deadline'),
                        goal_data.get('success_metric', ''),
                        goal_data.get('starting_point', ''),
                        goal_data.get('weekly_time', ''),
                        goal_data.get('energy_time', ''),
                        goal_data.get('free_days', ''),
                        goal_data.get('intensity', ''),
                        json.dumps(goal_data.get('joy_sources', [])),
                        json.dumps(goal_data.get('energy_drainers', [])),
                        goal_data.get('therapy_coaching', ''),
                        goal_data.get('obstacles', ''),
                        goal_data.get('resources', ''),
                        goal_data.get('reminder_preference', ''),
                        goal_data.get('auto_adapt', True)
                    ))
                    
                    goal_id = cursor.fetchone()[0]
                    conn.commit()
                    return goal_id
        except Exception as e:
            st.error(f"Failed to create goal: {str(e)}")
            raise
    
    def get_active_goal(self, user_email: str) -> Optional[Dict]:
        """Get the most recent active goal for a user"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM goals 
                        WHERE user_email = %s 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """, (user_email,))
                    
                    result = cursor.fetchone()
                    if result:
                        goal = dict(result)
                        # Parse JSON fields
                        goal['joy_sources'] = json.loads(goal.get('joy_sources', '[]'))
                        goal['energy_drainers'] = json.loads(goal.get('energy_drainers', '[]'))
                        return goal
                    return None
        except Exception as e:
            st.error(f"Failed to get active goal: {str(e)}")
            return None
    
    def save_milestones(self, goal_id: int, milestones: List[Dict]):
        """Save milestones for a goal"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clear existing milestones
                    cursor.execute("DELETE FROM milestones WHERE goal_id = %s", (goal_id,))
                    
                    # Insert new milestones
                    for milestone in milestones:
                        cursor.execute("""
                            INSERT INTO milestones (goal_id, title, description, target_date)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            goal_id,
                            milestone.get('title', ''),
                            milestone.get('description', ''),
                            milestone.get('target_date')
                        ))
                    
                    conn.commit()
        except Exception as e:
            st.error(f"Failed to save milestones: {str(e)}")
            raise
    
    def save_steps(self, goal_id: int, steps: List[Dict]):
        """Save steps for a goal"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clear existing steps
                    cursor.execute("DELETE FROM steps WHERE goal_id = %s", (goal_id,))
                    
                    # Insert new steps
                    for step in steps:
                        cursor.execute("""
                            INSERT INTO steps (goal_id, title, description, due_date, suggested_day, estimated_time, estimate_minutes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            goal_id,
                            step.get('title', ''),
                            step.get('description', ''),
                            step.get('due_date'),
                            step.get('suggested_day', ''),
                            step.get('estimated_time', 0),
                            step.get('estimate_minutes', 0)
                        ))
                    
                    conn.commit()
        except Exception as e:
            st.error(f"Failed to save steps: {str(e)}")
            raise
    
    def get_milestones(self, goal_id: int) -> List[Dict]:
        """Get milestones for a goal"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM milestones 
                        WHERE goal_id = %s 
                        ORDER BY target_date ASC
                    """, (goal_id,))
                    
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"Failed to get milestones: {str(e)}")
            return []
    
    def get_steps(self, goal_id: int) -> List[Dict]:
        """Get steps for a goal"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM steps 
                        WHERE goal_id = %s 
                        ORDER BY due_date ASC, suggested_day ASC
                    """, (goal_id,))
                    
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"Failed to get steps: {str(e)}")
            return []
    
    def update_goal(self, goal_id: int, updates: Dict):
        """Update a goal with new data"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Build dynamic update query
                    set_clauses = []
                    values = []
                    
                    for key, value in updates.items():
                        if key in ['joy_sources', 'energy_drainers']:
                            set_clauses.append(f"{key} = %s")
                            values.append(json.dumps(value))
                        else:
                            set_clauses.append(f"{key} = %s")
                            values.append(value)
                    
                    if set_clauses:
                        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                        values.append(goal_id)
                        
                        query = f"UPDATE goals SET {', '.join(set_clauses)} WHERE id = %s"
                        cursor.execute(query, values)
                        conn.commit()
        except Exception as e:
            st.error(f"Failed to update goal: {str(e)}")
            raise
