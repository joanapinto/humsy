-- Update mood_logs table to support rich mood tracking features
-- This script updates the existing mood_logs table to support:
-- 1. Multiple moods per entry (JSON array)
-- 2. Reasons for each mood (JSON object)
-- 3. Better notes field
-- 4. Remove unused intensity field

-- First, create a backup of existing data
CREATE TABLE IF NOT EXISTS mood_logs_backup AS 
SELECT * FROM mood_logs;

-- Drop the old table and recreate with new schema
DROP TABLE IF EXISTS mood_logs;

-- Create new mood_logs table with rich schema
CREATE TABLE IF NOT EXISTS mood_logs (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    moods JSONB NOT NULL,              -- Array of mood strings: ["😊 Happy", "😌 Calm"]
    reasons JSONB,                     -- Object mapping moods to reasons: {"😊 Happy": ["Time with friends", "Good weather"]}
    notes TEXT,                        -- Optional detailed notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mood_logs_user_email ON mood_logs(user_email);
CREATE INDEX IF NOT EXISTS idx_mood_logs_created_at ON mood_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_mood_logs_moods_gin ON mood_logs USING GIN (moods);
CREATE INDEX IF NOT EXISTS idx_mood_logs_reasons_gin ON mood_logs USING GIN (reasons);

-- Enable Row Level Security
ALTER TABLE mood_logs ENABLE ROW LEVEL SECURITY;

-- Create policy for public access (for now)
CREATE POLICY "Enable all operations for all users" ON mood_logs FOR ALL USING (true);

-- Migrate existing data from backup (if any)
-- Convert old single mood entries to new format
INSERT INTO mood_logs (user_email, moods, reasons, notes, created_at)
SELECT 
    user_email,
    jsonb_build_array(mood) as moods,  -- Convert single mood to array
    NULL as reasons,                   -- No reasons in old format
    notes,
    created_at
FROM mood_logs_backup
WHERE mood IS NOT NULL;

-- Add comment to document the schema
COMMENT ON TABLE mood_logs IS 'Rich mood tracking with multiple moods and reasons per entry';
COMMENT ON COLUMN mood_logs.moods IS 'JSON array of mood strings: ["😊 Happy", "😌 Calm"]';
COMMENT ON COLUMN mood_logs.reasons IS 'JSON object mapping moods to reasons: {"😊 Happy": ["Time with friends"]}';
COMMENT ON COLUMN mood_logs.notes IS 'Optional detailed notes about the mood entry';
