import pandas as pd
import os

BASE_DIR = os.getcwd()
print("Running from:", BASE_DIR)

input_path = os.path.join(BASE_DIR, "data", "raw", "upi_fraud.csv")
output_dir = os.path.join(BASE_DIR, "data", "interim")
output_path = os.path.join(output_dir, "upi_fraud_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

def txn_to_text(row):
    return (
        f"A {row['type']} transaction of amount ₹{row['amount']} occurred. "
        f"The sender balance changed from {row['oldbalanceOrg']} to {row['newbalanceOrig']}. "
        f"The receiver balance changed from {row['oldbalanceDest']} to {row['newbalanceDest']}."
    )

df["text"] = df.apply(txn_to_text, axis=1)
df["label"] = df["isFraud"]
df["source"] = "upi"

final_df = df[["text", "label", "source"]]

print("Rows processed:", len(final_df))
print(final_df.head())

final_df.to_csv(output_path, index=False)
print("✅ UPI fraud dataset cleaned & saved")
