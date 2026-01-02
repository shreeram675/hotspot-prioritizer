# Parent Model Testing - README

## Overview
This directory contains test images and scripts for validating the AI parent model's multi-attribute severity analysis.

## Model Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT: Image + Context                   │
│              (Image, Lat/Lon, Description, Upvotes)          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼────┐                    ┌─────▼─────┐
    │  YOLO   │                    │  Context  │
    │ Object  │                    │ Analyzers │
    │Detector │                    └─────┬─────┘
    └────┬────┘                          │
         │                        ┌──────┴──────┐
         │                        │             │
    ┌────▼────┐            ┌──────▼──────┐ ┌───▼────┐
    │ Scene   │            │  Location   │ │  Text  │
    │Classify │            │   Context   │ │Sentiment│
    └────┬────┘            └──────┬──────┘ └───┬────┘
         │                        │            │
         │                  ┌─────▼─────┐      │
         │                  │   Waste   │      │
         │                  │Classifier │      │
         │                  └─────┬─────┘      │
         │                        │            │
         └────────┬───────────────┴────────────┘
                  │
           ┌──────▼──────┐
           │   PARENT    │
           │    MODEL    │
           │  (Severity  │
           │   Scorer)   │
           └──────┬──────┘
                  │
        ┌─────────▼─────────┐
        │  Final Severity   │
        │  Score (0-100)    │
        │  + Category       │
        │  + Explanation    │
        └───────────────────┘
```

## Weight Distribution

**Parent Model Fusion Weights:**
- Image Analysis: 40%
  - Coverage Area: 15%
  - Scene Dirtiness: 15%
  - Object Count: 10%
- Location Context: 25%
- Text Sentiment: 20%
- Social Signals: 10%
- Risk Factors: 5%

**Dynamic Adjustments:**
- Location Multiplier: 0.9x - 1.5x (applied to final score)
- Text Urgency Boost: +10 to +20 points for critical/high urgency
- Risk Amplification: +10% for open dumps near sensitive areas

## Test Scenarios

### Severity Levels
1. **Clean** (0-20): Clean streets, no garbage
2. **Low** (21-40): Light litter, few items
3. **Medium** (41-60): Moderate accumulation
4. **High** (61-80): Heavy garbage, significant coverage
5. **Extreme** (81-100): Open dumps, hazardous waste, critical situations

### Context Variations
- **Location**: Near school (1.5x), hospital (1.4x), park (1.3x), commercial (1.0x)
- **Text Urgency**: Critical, high, medium, low
- **Waste Type**: Hazardous, wet, dry, recyclable, e-waste

## Running Tests

### Prerequisites
```bash
# Start AI service
docker-compose up ai_service

# Ensure test images are in ai_service/test_images/
```

### Run Test Suite
```bash
python test_parent_model.py
```

### Expected Output
- Individual test results for each scenario
- Component score breakdown
- Accuracy metrics
- Performance analysis
- Tuning recommendations

## Test Images Needed

Place these images in `ai_service/test_images/`:
1. clean_street.jpg
2. light_litter.jpg
3. moderate_garbage.jpg
4. heavy_garbage.jpg
5. food_waste.jpg
6. plastic_bottles.jpg
7. hazardous_waste.jpg
8. e_waste.jpg

(Or use generated/downloaded sample images)

## Interpreting Results

### Good Performance Indicators
- ✅ Severity accuracy > 70%
- ✅ Waste classification accuracy > 60%
- ✅ Average inference time < 10s
- ✅ Component scores balanced (no single component dominates)

### Tuning Recommendations
If accuracy is low:
1. **Image scores low** → Improve object detection threshold
2. **Location scores too high** → Reduce location weight
3. **Text scores too high** → Reduce text sentiment weight
4. **Misclassified waste types** → Add more keyword mappings

## Model Validation Checklist

- [ ] YOLO detects garbage objects correctly
- [ ] Scene classifier assesses dirtiness accurately
- [ ] Location context detects nearby sensitive areas
- [ ] Text sentiment extracts urgency keywords
- [ ] Waste classifier categorizes waste types
- [ ] Parent model combines all factors appropriately
- [ ] Severity scores match expected ranges
- [ ] Explanations are clear and accurate
