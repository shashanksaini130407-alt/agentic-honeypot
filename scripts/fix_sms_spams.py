import pandas as pd
import os

BASE_DIR = os.getcwd()
print("Running from:", BASE_DIR)

input_path = os.path.join(BASE_DIR, "data", "raw", "sms_spams.csv")
output_dir = os.path.join(BASE_DIR, "data", "interim")
output_path = os.path.join(output_dir, "sms_spams_clean.csv")

os.makedirs(output_dir, exist_ok=True)

# Read raw SMS lines
with open(input_path, "r", encoding="latin-1", errors="ignore") as f:
    lines = f.readlines()

texts = [line.strip() for line in lines if line.strip()]

df = pd.DataFrame({
    "text": texts,
    "label": 1,
    "source": "sms"
})

print("Rows cleaned:", len(df))
print(df.head())

df.to_csv(output_path, index=False)
print("✅ SMS spam dataset cleaned & saved at:")
print(output_path)
