import pandas as pd
import os

BASE_DIR = os.getcwd()
print("Running from:", BASE_DIR)

input_path = os.path.join(BASE_DIR, "data", "raw", "twitter_scam.csv")
output_dir = os.path.join(BASE_DIR, "data", "interim")
output_path = os.path.join(output_dir, "twitter_scam_clean.csv")

# Ensure folder exists
os.makedirs(output_dir, exist_ok=True)

# --- READ AS RAW TEXT (no pandas parsing yet) ---
with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Clean lines
texts = [line.strip() for line in lines if line.strip()]

# Create DataFrame
df = pd.DataFrame({
    "text": texts,
    "label": 1,
    "source": "twitter"
})

print("Rows cleaned:", len(df))
print(df.head())

# Save
df.to_csv(output_path, index=False)
print("✅ Twitter scam dataset cleaned & saved at:")
print(output_path)
