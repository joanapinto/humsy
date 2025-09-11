-- Update checkins table to include all necessary fields for daily check-ins
ALTER TABLE checkins 
ADD COLUMN IF NOT EXISTS time_period TEXT,
ADD COLUMN IF NOT EXISTS sleep_quality TEXT,
ADD COLUMN IF NOT EXISTS focus_today TEXT,
ADD COLUMN IF NOT EXISTS current_feeling TEXT,
ADD COLUMN IF NOT EXISTS day_progress TEXT,
ADD COLUMN IF NOT EXISTS accomplishments TEXT,
ADD COLUMN IF NOT EXISTS challenges TEXT,
ADD COLUMN IF NOT EXISTS task_plan JSONB,
ADD COLUMN IF NOT EXISTS task_completion JSONB,
ADD COLUMN IF NOT EXISTS checkin_hour INTEGER;
