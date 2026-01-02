import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Create a dummy model that expects 7 features
# 1. Object Count (0-50)
# 2. Coverage Area (0-1)
# 3. Dirtiness Score (0-1)
# 4. Location Multiplier (0.9-1.5)
# 5. Text Severity (0-1)
# 6. Social Score (0-1)
# 7. Risk Factor (0-1)

X = np.random.rand(100, 7)
y = np.random.randint(0, 100, 100)

model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X, y)

print("Created dummy model expecting 7 features")

with open('ai_service/models/parent_severity_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Saved to ai_service/models/parent_severity_model.pkl")
