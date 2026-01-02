-- Migration: Add Location Context and Text Sentiment fields to reports table
-- This migration adds fields for comprehensive context-aware AI analysis

-- Location context fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS location_context JSONB;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS location_priority_multiplier FLOAT DEFAULT 1.0;

-- Text sentiment analysis fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_sentiment_score FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_urgency_keywords TEXT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_emotion_category VARCHAR(50);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reports_location_priority ON reports(location_priority_multiplier);
CREATE INDEX IF NOT EXISTS idx_reports_sentiment ON reports(text_sentiment_score);
CREATE INDEX IF NOT EXISTS idx_reports_location_context ON reports USING GIN(location_context);

-- Add comments for documentation
COMMENT ON COLUMN reports.location_context IS 'JSON data about nearby sensitive locations (schools, hospitals, eco-zones)';
COMMENT ON COLUMN reports.location_priority_multiplier IS 'Location-based priority multiplier (0.9-1.5x)';
COMMENT ON COLUMN reports.text_sentiment_score IS 'NLP sentiment score from user description (0-1)';
COMMENT ON COLUMN reports.text_urgency_keywords IS 'Comma-separated urgency keywords detected';
COMMENT ON COLUMN reports.text_emotion_category IS 'Detected emotion: angry/concerned/neutral/positive';
