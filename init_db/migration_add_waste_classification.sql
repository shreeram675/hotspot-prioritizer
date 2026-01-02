-- Migration: Add Waste Type Classification fields to reports table
-- This migration adds fields for waste type categorization and disposal recommendations

-- Waste type classification fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_primary_type VARCHAR(50);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_composition JSONB;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_hazardous_waste BOOLEAN DEFAULT FALSE;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS waste_disposal_recommendations TEXT;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reports_waste_type ON reports(waste_primary_type);
CREATE INDEX IF NOT EXISTS idx_reports_hazardous ON reports(is_hazardous_waste) WHERE is_hazardous_waste = TRUE;
CREATE INDEX IF NOT EXISTS idx_reports_waste_composition ON reports USING GIN(waste_composition);

-- Add comments for documentation
COMMENT ON COLUMN reports.waste_primary_type IS 'Primary waste category: hazardous/wet/dry/recyclable/e_waste/other';
COMMENT ON COLUMN reports.waste_composition IS 'JSON breakdown of waste type percentages';
COMMENT ON COLUMN reports.is_hazardous_waste IS 'Flag for hazardous waste requiring special handling';
COMMENT ON COLUMN reports.waste_disposal_recommendations IS 'AI-generated disposal and handling recommendations';
