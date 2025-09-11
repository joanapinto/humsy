-- Plan adaptations table for tracking plan changes
CREATE TABLE IF NOT EXISTS plan_adaptations (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
    checkin_timestamp TIMESTAMP NOT NULL,
    alignment_score INTEGER,
    reason TEXT,
    change_summary TEXT,
    diff_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security (RLS)
ALTER TABLE plan_adaptations ENABLE ROW LEVEL SECURITY;

-- Create policy for public access (for now)
CREATE POLICY "Enable all operations for all users" ON plan_adaptations FOR ALL USING (true);
