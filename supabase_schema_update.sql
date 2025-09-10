-- Supabase Schema Update for Humsy
-- Run this in your Supabase SQL Editor to add missing columns

-- Add missing columns to milestones table
ALTER TABLE milestones 
ADD COLUMN IF NOT EXISTS seq INTEGER,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';

-- Add missing columns to steps table  
ALTER TABLE steps
ADD COLUMN IF NOT EXISTS milestone_id INTEGER REFERENCES milestones(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';

-- Update existing milestones to have sequence numbers
-- This will set seq = id for existing milestones
UPDATE milestones 
SET seq = id 
WHERE seq IS NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_milestones_goal_seq ON milestones(goal_id, seq);
CREATE INDEX IF NOT EXISTS idx_steps_milestone ON steps(milestone_id);
