import pandas as pd
import os

BASE_DIR = os.getcwd()

interim = os.path.join(BASE_DIR, "data", "interim")
output = os.path.join(BASE_DIR, "data", "processed", "master_fraud_dataset.csv")

os.makedirs(os.path.dirname(output), exist_ok=True)

files = [
    "twitter_scam_clean.csv",
    "sms_spams_clean.csv",
    "upi_fraud_clean.csv",
    "phishing_urls_clean.csv"
]

dfs = []

for file in files:
    path = os.path.join(interim, file)
    print("Loading:", path)
    dfs.append(pd.read_csv(path))

final_df = pd.concat(dfs, ignore_index=True)

print("Total rows:", len(final_df))
print(final_df.sample(5))

final_df.to_csv(output, index=False)
print("✅ MASTER DATASET CREATED")
