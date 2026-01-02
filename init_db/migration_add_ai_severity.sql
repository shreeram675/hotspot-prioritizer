-- Migration: Add AI Severity Analysis columns to reports table
-- This migration adds fields to store comprehensive AI analysis results

-- Add AI severity analysis columns
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_severity_score INTEGER;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_severity_category VARCHAR(20);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_object_count INTEGER;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_coverage_area FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_scene_dirtiness FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_confidence_explanation TEXT;

-- Add comments for documentation
COMMENT ON COLUMN reports.ai_severity_score IS 'AI-calculated severity score (0-100)';
COMMENT ON COLUMN reports.ai_severity_category IS 'AI severity category: Clean/Low/Medium/High/Extreme';
COMMENT ON COLUMN reports.ai_object_count IS 'Number of garbage objects detected by YOLO';
COMMENT ON COLUMN reports.ai_coverage_area IS 'Garbage coverage area ratio (0-1)';
COMMENT ON COLUMN reports.ai_scene_dirtiness IS 'Scene dirtiness score from classifier (0-1)';
COMMENT ON COLUMN reports.ai_confidence_explanation IS 'Human-readable AI analysis explanation';
