import pickle
import os

model_path = 'tradeiq_backend/model.pkl'

if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        loaded = pickle.load(f)
    
    if isinstance(loaded, tuple):
        print(f"Loaded as tuple with {len(loaded)} elements")
        print(f"Item 0: {type(loaded[0])}")
        if len(loaded) > 1:
            print(f"Item 1: {type(loaded[1])}")
    else:
        print(f"Loaded as single object: {type(loaded)}")
        print(f"Has transform method: {hasattr(loaded, 'transform')}")
        print(f"Has predict method: {hasattr(loaded, 'predict')}")
else:
    print("model.pkl not found")
