import pickle
import sys
import os

path = "ai_service/models/parent_severity_model.pkl"
print(f"Testing load of: {path}")

if not os.path.exists(path):
    print("❌ File does not exist")
    sys.exit(1)

try:
    with open(path, 'rb') as f:
        model = pickle.load(f)
    print("✅ Load successful")
    print(f"Type: {type(model)}")
except Exception as e:
    print(f"❌ Load failed: {e}")
