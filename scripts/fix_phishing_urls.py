import pandas as pd
import os
from urllib.parse import urlparse

BASE_DIR = os.getcwd()
print("Running from:", BASE_DIR)

input_path = os.path.join(BASE_DIR, "data", "raw", "phishing_urls.csv")
output_dir = os.path.join(BASE_DIR, "data", "interim")
output_path = os.path.join(output_dir, "phishing_urls_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

def url_to_text(row):
    domain = urlparse(row["url"]).netloc
    return (
        f"A phishing website URL was detected. "
        f"The domain is {domain}. "
        f"The target brand is {row['target']}."
    )

df["text"] = df.apply(url_to_text, axis=1)
df["label"] = 1  # phishing
df["source"] = "url"

final_df = df[["text", "label", "source"]]

print("Rows processed:", len(final_df))
print(final_df.head())

final_df.to_csv(output_path, index=False)
print("✅ Phishing URLs dataset cleaned & saved")
