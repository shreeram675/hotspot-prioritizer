# How to Integrate Your Trained .pkl Model

## Quick Start

### 1. Place Your Model File

Put your `.pkl` file in the models directory:
```
ai_service/
  └── models/
      └── severity_model.pkl  # Your trained model here
```

### 2. Update main.py

Replace the severity scorer import:

```python
# OLD:
from severity_scorer import SeverityScorer

# NEW:
from hybrid_severity_scorer import HybridSeverityScorer as SeverityScorer
```

That's it! The system will automatically:
- Try to load your trained model
- Use it for predictions if available
- Fall back to rule-based scoring if model fails

---

## Model Requirements

### Expected Input Features (21 features)

Your model should be trained on these features in this order:

**Object Detection (6 features):**
1. `object_count` - Number of garbage objects (0-50+)
2. `coverage_area` - Area covered by garbage (0.0-1.0)
3. `density` - Objects per megapixel (0.0-20.0)
4. `has_overflow` - Binary (0 or 1)
5. `is_open_dump` - Binary (0 or 1)
6. `bin_detected` - Binary (0 or 1)

**Scene Classification (4 features):**
7. `dirtiness_score` - Scene dirtiness (0.0-1.0)
8. `scene_confidence` - Classifier confidence (0.0-1.0)
9. `dirty_indicators` - Dirty class probability (0.0-1.0)
10. `clean_indicators` - Clean class probability (0.0-1.0)

**Location Context (5 features):**
11. `location_multiplier` - Priority multiplier (0.9-1.5)
12. `zone_educational` - Binary (0 or 1)
13. `zone_healthcare` - Binary (0 or 1)
14. `zone_eco` - Binary (0 or 1)
15. `zone_residential` - Binary (0 or 1)

**Text Sentiment (5 features):**
16. `sentiment_score` - Sentiment (0.0-1.0)
17. `text_boost_normalized` - Urgency boost (0.0-1.0)
18. `urgency_critical` - Binary (0 or 1)
19. `urgency_high` - Binary (0 or 1)
20. `urgency_medium` - Binary (0 or 1)

**Social Signals (1 feature):**
21. `upvote_count_normalized` - Upvotes (0.0-1.0)

### Expected Output

Your model should output one of:

**Option 1: Regression (Recommended)**
- Output: Severity score (0-100)
- Example: `model.predict(features) → [67.5]`

**Option 2: Classification**
- Output: Class (0-4) for Clean/Low/Medium/High/Extreme
- Example: `model.predict(features) → [3]` (High)
- Will be mapped to: 0→20, 1→40, 2→60, 3→80, 4→100

---

## Supported Model Types

The system supports any scikit-learn compatible model:

✅ **Regression Models:**
- `LinearRegression`
- `Ridge`, `Lasso`
- `RandomForestRegressor`
- `GradientBoostingRegressor`
- `XGBRegressor`
- `LGBMRegressor`

✅ **Classification Models:**
- `LogisticRegression`
- `RandomForestClassifier`
- `GradientBoostingClassifier`
- `XGBClassifier`
- `SVC` (with probability=True)

✅ **Neural Networks:**
- `MLPRegressor`
- `MLPClassifier`
- Keras/TensorFlow models (saved with pickle)

---

## Example: Training Your Own Model

```python
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load your training data
# Features: 21 columns as listed above
# Target: severity_score (0-100)
df = pd.read_csv('training_data.csv')

X = df.drop('severity_score', axis=1)
y = df['severity_score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"R² Score: {score}")

# Save model
with open('ai_service/models/severity_model.pkl', 'wb') as f:
    pickle.dump(model, f)
```

---

## Configuration Options

### Use Trained Model Only

```python
# In main.py
result = HybridSeverityScorer.calculate_severity(
    ...,
    use_trained_model=True  # Default
)
```

### Use Rule-Based Only

```python
result = HybridSeverityScorer.calculate_severity(
    ...,
    use_trained_model=False
)
```

### Custom Model Path

```python
result = HybridSeverityScorer.calculate_severity(
    ...,
    model_path="path/to/your/custom_model.pkl"
)
```

---

## Testing Your Model

### 1. Check Model Loading

```python
from hybrid_severity_scorer import HybridSeverityScorer

info = HybridSeverityScorer.get_model_info()
print(info)
```

Expected output:
```json
{
  "loaded": true,
  "path": "ai_service/models/severity_model.pkl",
  "model_type": "RandomForestRegressor",
  "feature_count": 21,
  "features": [...]
}
```

### 2. Test Prediction

```bash
# Start AI service
docker-compose up ai_service

# Test with image
curl -X POST http://localhost:8001/analyze-severity \
  -F "file=@test_image.jpg" \
  -F "lat=12.9716" \
  -F "lon=77.5946"
```

Response will include:
```json
{
  "severity_score": 67,
  "prediction_method": "trained_model",
  "model_type": "RandomForestRegressor",
  "rule_based_score": 72
}
```

---

## Troubleshooting

### Model Not Loading

**Error:** `Model not found at: ai_service/models/severity_model.pkl`

**Solution:**
1. Check file path is correct
2. Ensure file has `.pkl` extension
3. Verify file permissions

### Feature Mismatch

**Error:** `Feature shape mismatch`

**Solution:**
1. Check your model expects 21 features
2. Verify feature order matches the list above
3. Re-train model with correct features

### Poor Predictions

**Issue:** Model predictions don't match expectations

**Solution:**
1. Check training data quality
2. Verify feature scaling (if used during training)
3. Compare with rule-based scores
4. Retrain with more data

---

## Comparison Mode

The hybrid scorer returns both predictions:

```json
{
  "severity_score": 67,        // Trained model
  "rule_based_score": 72,      // Rule-based
  "prediction_method": "trained_model"
}
```

This allows you to:
- Compare model vs rules
- Identify where they disagree
- Improve model training

---

## Next Steps

1. **Place your .pkl file** in `ai_service/models/`
2. **Update main.py** to use `HybridSeverityScorer`
3. **Restart AI service**: `docker-compose restart ai_service`
4. **Test predictions** with sample images
5. **Monitor performance** and retrain as needed
