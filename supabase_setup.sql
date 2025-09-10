-- Supabase Database Setup for Humsy
-- Run this in your Supabase SQL Editor

-- Goals table
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
);

-- Milestones table
CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    target_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Steps table
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
);

-- Mood logs table
CREATE TABLE IF NOT EXISTS mood_logs (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    mood TEXT NOT NULL,
    intensity INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check-ins table
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
);

-- Enable Row Level Security (RLS)
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (for now)
CREATE POLICY "Enable all operations for all users" ON goals FOR ALL USING (true);
CREATE POLICY "Enable all operations for all users" ON milestones FOR ALL USING (true);
CREATE POLICY "Enable all operations for all users" ON steps FOR ALL USING (true);
CREATE POLICY "Enable all operations for all users" ON mood_logs FOR ALL USING (true);
CREATE POLICY "Enable all operations for all users" ON checkins FOR ALL USING (true);
