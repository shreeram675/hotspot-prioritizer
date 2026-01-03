-- Add missing AI and Waste Analysis columns to reports table

-- AI Severity Analysis Fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_severity_score INTEGER;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_severity_category VARCHAR(20);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_object_count INTEGER;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_coverage_area FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_scene_dirtiness FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS ai_confidence_explanation TEXT;

-- Road Importance
ALTER TABLE reports ADD COLUMN IF NOT EXISTS road_importance INTEGER DEFAULT 1;

-- Waste Type Classification Fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_primary_type VARCHAR(50);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_composition JSONB;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_hazardous_waste BOOLEAN DEFAULT FALSE;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_disposal_recommendations TEXT;

-- Location Context Context Fields (Ensure these are present too)
ALTER TABLE reports ADD COLUMN IF NOT EXISTS location_context JSONB;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS location_priority_multiplier FLOAT DEFAULT 1.0;

-- Text Sentiment Analysis Fields (Ensure these are present too)
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_sentiment_score FLOAT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_urgency_keywords TEXT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS text_emotion_category VARCHAR(50);
