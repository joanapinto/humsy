"""
SQLite Database Manager for Focus Companion
Handles all data storage and retrieval operations
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database operations for Focus Companion"""
    
    def __init__(self, db_path: str = "data/focus_companion.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # API Usage Tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    tokens_used INTEGER,
                    cost_usd REAL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mood Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    moods TEXT NOT NULL,  -- JSON array of moods
                    reasons TEXT,         -- JSON object of reasons
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check-ins
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    time_period TEXT NOT NULL,
                    sleep_quality TEXT,
                    energy_level TEXT,
                    focus_today TEXT,
                    current_feeling TEXT,
                    day_progress TEXT,
                    accomplishments TEXT,
                    challenges TEXT,
                    task_plan TEXT,
                    task_completion TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User Profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_email TEXT PRIMARY KEY,
                    goal TEXT,
                    tone TEXT,
                    availability TEXT,
                    energy TEXT,
                    therapy_coaching TEXT,
                    emotional_patterns TEXT,
                    small_habit TEXT,
                    reminders TEXT,
                    situation TEXT,
                    joy_sources TEXT,
                    joy_other TEXT,
                    energy_drainers TEXT,
                    energy_drainer_other TEXT,
                    situation_other TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # --- GOALS / PLAN TABLES ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
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
              joy_sources TEXT,
              energy_drainers TEXT,
              therapy_coaching TEXT,
              obstacles TEXT,
              resources TEXT,
              reminder_preference TEXT,
              auto_adapt BOOLEAN DEFAULT 1,
              status TEXT DEFAULT 'active',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              goal_id INTEGER NOT NULL,
              title TEXT NOT NULL,
              description TEXT,
              target_date DATE,
              seq INTEGER,
              status TEXT DEFAULT 'pending',
              FOREIGN KEY(goal_id) REFERENCES goals(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              goal_id INTEGER NOT NULL,
              milestone_id INTEGER,
              title TEXT NOT NULL,
              description TEXT,
              estimate_minutes INTEGER,
              suggested_day TEXT,
              due_date DATE,
              status TEXT DEFAULT 'pending',
              last_scheduled DATE,
              FOREIGN KEY(goal_id) REFERENCES goals(id),
              FOREIGN KEY(milestone_id) REFERENCES milestones(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_adaptations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              goal_id INTEGER NOT NULL,
              checkin_timestamp TIMESTAMP NOT NULL,
              alignment_score INTEGER,
              reason TEXT,
              change_summary TEXT,
              diff_json TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY(goal_id) REFERENCES goals(id)
            );
            """)

            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_user_date ON api_usage(user_email, date(created_at))")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_usage_feature ON api_usage(feature)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mood_logs_user_date ON mood_logs(user_email, date(created_at))")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkins_user_date ON checkins(user_email, date(created_at))")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkins_period ON checkins(time_period)")
            
            # Migrate existing goals table if needed
            self._migrate_goals_table()
            
            conn.commit()
    
    def _migrate_goals_table(self):
        """Migrate existing goals table to new schema"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if goals table exists and get its columns
        cursor.execute("PRAGMA table_info(goals)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # List of new columns to add
        new_columns = [
            ('why_matters', 'TEXT'),
            ('starting_point', 'TEXT'),
            ('weekly_time', 'TEXT'),
            ('energy_time', 'TEXT'),
            ('free_days', 'TEXT'),
            ('intensity', 'TEXT'),
            ('joy_sources', 'TEXT'),
            ('energy_drainers', 'TEXT'),
            ('therapy_coaching', 'TEXT'),
            ('obstacles', 'TEXT'),
            ('resources', 'TEXT'),
            ('reminder_preference', 'TEXT'),
            ('auto_adapt', 'BOOLEAN DEFAULT 1')
        ]
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE goals ADD COLUMN {column_name} {column_type}")
                    print(f"Added column {column_name} to goals table")
                except sqlite3.OperationalError as e:
                    print(f"Could not add column {column_name}: {e}")
        
        conn.commit()
        conn.close()
    
    def record_api_usage(self, user_email: str, feature: str, tokens_used: int = None, 
                        cost_usd: float = None, success: bool = True, error_message: str = None):
        """Record an API usage event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage (user_email, feature, tokens_used, cost_usd, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_email, feature, tokens_used, cost_usd, success, error_message))
            conn.commit()
    
    def get_user_api_usage(self, user_email: str, days: int = 30) -> Dict[str, Any]:
        """Get API usage statistics for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Daily usage
            cursor.execute("""
                SELECT date(created_at) as date, COUNT(*) as count
                FROM api_usage 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
                GROUP BY date(created_at)
                ORDER BY date DESC
            """.format(days), (user_email,))
            daily_usage = dict(cursor.fetchall())
            
            # Monthly usage
            cursor.execute("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
                FROM api_usage 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
                GROUP BY strftime('%Y-%m', created_at)
                ORDER BY month DESC
            """.format(days), (user_email,))
            monthly_usage = dict(cursor.fetchall())
            
            # Feature breakdown
            cursor.execute("""
                SELECT feature, COUNT(*) as count
                FROM api_usage 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
                GROUP BY feature
                ORDER BY count DESC
            """.format(days), (user_email,))
            feature_usage = dict(cursor.fetchall())
            
            # Total cost
            cursor.execute("""
                SELECT COALESCE(SUM(cost_usd), 0) as total_cost
                FROM api_usage 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
            """.format(days), (user_email,))
            total_cost = cursor.fetchone()[0]
            
            return {
                "daily_usage": daily_usage,
                "monthly_usage": monthly_usage,
                "feature_usage": feature_usage,
                "total_cost": total_cost
            }
    
    def get_global_api_usage(self, days: int = 30) -> Dict[str, Any]:
        """Get global API usage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Daily totals
            cursor.execute("""
                SELECT date(created_at) as date, COUNT(*) as count
                FROM api_usage 
                WHERE created_at >= date('now', '-{} days')
                GROUP BY date(created_at)
                ORDER BY date DESC
            """.format(days))
            daily_usage = dict(cursor.fetchall())
            
            # Monthly totals
            cursor.execute("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
                FROM api_usage 
                WHERE created_at >= date('now', '-{} days')
                GROUP BY strftime('%Y-%m', created_at)
                ORDER BY month DESC
            """.format(days))
            monthly_usage = dict(cursor.fetchall())
            
            # Total cost
            cursor.execute("""
                SELECT COALESCE(SUM(cost_usd), 0) as total_cost
                FROM api_usage 
                WHERE created_at >= date('now', '-{} days')
            """.format(days))
            total_cost = cursor.fetchone()[0]
            
            return {
                "daily_usage": daily_usage,
                "monthly_usage": monthly_usage,
                "total_cost": total_cost
            }
    
    def save_mood_log(self, user_email: str, moods: list, reasons: dict = None, notes: str = None):
        """Save a mood log entry with multiple moods and reasons"""
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mood_logs (user_email, moods, reasons, notes)
                VALUES (?, ?, ?, ?)
            """, (user_email, json.dumps(moods), json.dumps(reasons or {}), notes))
            conn.commit()
    
    def get_mood_logs(self, user_email: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get mood logs for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT moods, reasons, notes, created_at
                FROM mood_logs 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
                ORDER BY created_at DESC
            """.format(days), (user_email,))
            
            logs = []
            for row in cursor.fetchall():
                import json
                logs.append({
                    "moods": json.loads(row[0]) if row[0] else [],
                    "reasons": json.loads(row[1]) if row[1] else {},
                    "notes": row[2],
                    "created_at": row[3]
                })
            return logs
    
    def save_checkin(self, user_email: str, checkin_data: Dict[str, Any]):
        """Save a check-in entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO checkins (
                    user_email, time_period, sleep_quality, energy_level, 
                    focus_today, current_feeling, day_progress, accomplishments, 
                    challenges, task_plan, task_completion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_email,
                checkin_data.get('time_period'),
                checkin_data.get('sleep_quality'),
                checkin_data.get('energy_level'),
                checkin_data.get('focus_today'),
                checkin_data.get('current_feeling'),
                checkin_data.get('day_progress'),
                checkin_data.get('accomplishments'),
                checkin_data.get('challenges'),
                json.dumps(checkin_data.get('task_plan', {})) if checkin_data.get('task_plan') else None,
                json.dumps(checkin_data.get('task_completion', {})) if checkin_data.get('task_completion') else None
            ))
            conn.commit()
    
    def get_checkins(self, user_email: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get check-ins for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT time_period, sleep_quality, energy_level, focus_today,
                       current_feeling, day_progress, accomplishments, challenges,
                       task_plan, task_completion, created_at
                FROM checkins 
                WHERE user_email = ? AND created_at >= date('now', '-{} days')
                ORDER BY created_at DESC
            """.format(days), (user_email,))
            
            checkins = []
            for row in cursor.fetchall():
                checkin = {
                    "time_period": row[0],
                    "sleep_quality": row[1],
                    "energy_level": row[2],
                    "focus_today": row[3],
                    "current_feeling": row[4],
                    "day_progress": row[5],
                    "accomplishments": row[6],
                    "challenges": row[7],
                    "task_plan": json.loads(row[8]) if row[8] else {},
                    "task_completion": json.loads(row[9]) if row[9] else {},
                    "created_at": row[10]
                }
                checkins.append(checkin)
            return checkins
    
    def save_user_profile(self, user_email: str, profile_data: Dict[str, Any]):
        """Save or update a user profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert lists to JSON strings
            profile_data = profile_data.copy()
            if 'joy_sources' in profile_data and isinstance(profile_data['joy_sources'], list):
                profile_data['joy_sources'] = json.dumps(profile_data['joy_sources'])
            if 'energy_drainers' in profile_data and isinstance(profile_data['energy_drainers'], list):
                profile_data['energy_drainers'] = json.dumps(profile_data['energy_drainers'])
            
            # Check if profile exists
            cursor.execute("SELECT user_email FROM user_profiles WHERE user_email = ?", (user_email,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing profile
                set_clause = ", ".join([f"{k} = ?" for k in profile_data.keys()])
                set_clause += ", updated_at = CURRENT_TIMESTAMP"
                cursor.execute(f"UPDATE user_profiles SET {set_clause} WHERE user_email = ?", 
                             list(profile_data.values()) + [user_email])
            else:
                # Insert new profile
                columns = ", ".join(profile_data.keys())
                placeholders = ", ".join(["?" for _ in profile_data])
                cursor.execute(f"INSERT INTO user_profiles ({columns}) VALUES ({placeholders})", 
                             list(profile_data.values()))
            
            conn.commit()
    
    def get_user_profile(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get a user profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_email = ?", (user_email,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                profile = dict(zip(columns, row))
                
                # Convert JSON strings back to lists
                if profile.get('joy_sources'):
                    try:
                        profile['joy_sources'] = json.loads(profile['joy_sources'])
                    except:
                        profile['joy_sources'] = []
                
                if profile.get('energy_drainers'):
                    try:
                        profile['energy_drainers'] = json.loads(profile['energy_drainers'])
                    except:
                        profile['energy_drainers'] = []
                
                return profile
            return None
    
    def delete_user_data(self, user_email: str):
        """Delete all data for a user (for GDPR compliance)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_usage WHERE user_email = ?", (user_email,))
            cursor.execute("DELETE FROM mood_logs WHERE user_email = ?", (user_email,))
            cursor.execute("DELETE FROM checkins WHERE user_email = ?", (user_email,))
            cursor.execute("DELETE FROM user_profiles WHERE user_email = ?", (user_email,))
            conn.commit()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            for table in ['api_usage', 'mood_logs', 'checkins', 'user_profiles']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Get unique users
            cursor.execute("SELECT COUNT(DISTINCT user_email) FROM user_profiles")
            stats['unique_users'] = cursor.fetchone()[0]
            
            # Get total API cost
            cursor.execute("SELECT COALESCE(SUM(cost_usd), 0) FROM api_usage")
            stats['total_api_cost'] = cursor.fetchone()[0]
            
            return stats

    # ---------- GOALS: HELPERS ----------
    def create_goal(self, user_email: str, data: dict) -> int:
        import sqlite3, datetime, json
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
          INSERT INTO goals (user_email, title, why_matters, deadline, success_metric, starting_point, 
                           weekly_time, energy_time, free_days, intensity, joy_sources, energy_drainers,
                           therapy_coaching, obstacles, resources, reminder_preference, auto_adapt, status)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (
            user_email,
            data.get("title",""),
            data.get("why_matters",""),
            data.get("deadline"),
            data.get("success_metric",""),
            data.get("starting_point",""),
            data.get("weekly_time",""),
            data.get("energy_time",""),
            data.get("free_days",""),
            data.get("intensity",""),
            json.dumps(data.get("joy_sources", [])),
            json.dumps(data.get("energy_drainers", [])),
            data.get("therapy_coaching",""),
            data.get("obstacles",""),
            data.get("resources",""),
            data.get("reminder_preference",""),
            data.get("auto_adapt", True)
        ))
        goal_id = cur.lastrowid
        conn.commit()
        conn.close()
        return goal_id

    def get_active_goal(self, user_email: str) -> dict | None:
        import sqlite3, json
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM goals WHERE user_email=? AND status='active' ORDER BY id DESC LIMIT 1", (user_email,))
        row = cur.fetchone()
        conn.close()
        if row:
            goal = dict(row)
            # Parse JSON fields
            try:
                goal['joy_sources'] = json.loads(goal.get('joy_sources', '[]'))
            except:
                goal['joy_sources'] = []
            try:
                goal['energy_drainers'] = json.loads(goal.get('energy_drainers', '[]'))
            except:
                goal['energy_drainers'] = []
            return goal
        return None

    def save_milestones(self, goal_id: int, milestones: list[dict]) -> None:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        for i, m in enumerate(milestones):
            cur.execute("""
              INSERT INTO milestones (goal_id, title, description, target_date, seq, status)
              VALUES (?, ?, ?, ?, ?, 'pending')
            """, (goal_id, m.get("title",""), m.get("description",""), m.get("target_date"), i))
        conn.commit()
        conn.close()

    def save_steps(self, goal_id: int, steps: list[dict]) -> None:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # map milestone titles to ids
        cur.execute("SELECT id, title FROM milestones WHERE goal_id=?", (goal_id,))
        mapping = {row[1]: row[0] for row in cur.fetchall()}
        for s in steps:
            mid = mapping.get(s.get("milestone_title"))
            cur.execute("""
              INSERT INTO steps (goal_id, milestone_id, title, description, estimate_minutes, suggested_day, due_date, status)
              VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (goal_id, mid, s.get("title",""), s.get("description",""),
                  int(s.get("estimate_minutes") or 30),
                  s.get("suggested_day","Any"),
                  s.get("due_date")))
        conn.commit()
        conn.close()

    def list_plan(self, goal_id: int) -> tuple[list[dict], list[dict]]:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM milestones WHERE goal_id=? ORDER BY seq ASC", (goal_id,))
        milestones = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM steps WHERE goal_id=? ORDER BY id ASC", (goal_id,))
        steps = [dict(r) for r in cur.fetchall()]
        conn.close()
        return milestones, steps

    def clear_plan(self, goal_id: int):
        """Clear all milestones and steps for a goal"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM steps WHERE goal_id=?", (goal_id,))
        cur.execute("DELETE FROM milestones WHERE goal_id=?", (goal_id,))
        conn.commit()
        conn.close()

    def update_goal(self, goal_id: int, data: dict):
        """Update goal data"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Build update query dynamically based on provided data
        set_clauses = []
        values = []
        
        for key, value in data.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if set_clauses:
            query = f"UPDATE goals SET {', '.join(set_clauses)} WHERE id = ?"
            values.append(goal_id)
            cur.execute(query, values)
            conn.commit()
        
        conn.close()

    def get_today_candidates(self, user_email: str, date_str: str) -> list[dict]:
        # simple heuristic: pending steps due today or with suggested_day matching weekday
        import sqlite3, datetime
        wd = datetime.datetime.fromisoformat(date_str).strftime("%a")  # e.g., Mon
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        goal = self.get_active_goal(user_email)
        if not goal: 
            conn.close()
            return []
        cur.execute("""
          SELECT * FROM steps 
          WHERE goal_id=? AND status IN ('pending','in_progress')
          ORDER BY COALESCE(due_date,'9999-12-31') ASC, estimate_minutes ASC
        """, (goal["id"],))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        def day_ok(s):
            sd = (s.get("suggested_day") or "Any")
            return sd == "Any" or wd in sd.split(",")
        return [r for r in rows if day_ok(r)]

    def mark_step_status(self, step_id: int, status: str):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE steps SET status=?, last_scheduled=date('now') WHERE id=?", (status, step_id))
        conn.commit()
        conn.close()

    def record_adaptation(self, goal_id: int, checkin_ts: str, alignment_score: int, reason: str, change_summary: str, diff_json: str):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
          INSERT INTO plan_adaptations (goal_id, checkin_timestamp, alignment_score, reason, change_summary, diff_json)
          VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, checkin_ts, alignment_score, reason, change_summary, diff_json))
        conn.commit()
        conn.close() 