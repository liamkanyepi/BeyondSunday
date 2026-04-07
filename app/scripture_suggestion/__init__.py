import os
key = os.getenv("OPENROUTER_API_KEY")
print("LOADED KEY:", key)
print("KEY LENGTH:", len(key) if key else "None")