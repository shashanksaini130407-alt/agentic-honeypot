import pandas as pd

datasets = {
    "UPI_FRAUD": "data/raw/upi_fraud.csv",
    "TWITTER_SCAM": "data/raw/twitter_scam.csv",
    "SMS_SPAMS": "data/raw/sms_spams.csv",
    "PHISHING_URLS": "data/raw/phishing_urls.csv"
}

for name, path in datasets.items():
    print("\n" + "=" * 50)
    print(f"DATASET: {name}")
    
    try:
        df = pd.read_csv(path)
        print("Columns:", df.columns.tolist())
        print("Number of rows:", len(df))
        print("Sample rows:")
        print(df.head(3))
    except Exception as e:
        print("❌ Error reading file:", e)
