import pandas as pd
import requests
from tqdm import tqdm

def get_genders_in_batches(names, batch_size=10):
    """
    Fetch gender predictions in batches (up to 10 names per request).
    Returns a dictionary mapping name -> gender.
    """
    results = {}
    for i in tqdm(range(0, len(names), batch_size), desc="Fetching batches", unit="batch"):
        batch = names[i:i+batch_size]
        try:
            response = requests.get(
                "https://api.genderize.io",
                params=[("name[]", name) for name in batch]
            )
            data = response.json()
            for entry in data:
                results[entry["name"]] = entry.get("gender")
        except Exception as e:
            print(f"⚠️ Error fetching batch starting at index {i}: {e}")
            for name in batch:
                results[name] = None
    return results


if __name__ == "__main__":
    print("📂 Loading dataset...")
    df = pd.read_excel("enhanced_salesforce_report.xlsx")

    # Ensure the column exists
    if "Gender" not in df.columns:
        df["Gender"] = None

    # Get only names with missing gender
    missing_gender_mask = df["Gender"].isna() | (df["Gender"] == "")
    missing_names = df.loc[missing_gender_mask, "Full Name"].dropna().astype(str).str.strip().unique().tolist()

    print(f"🚀 Fetching gender data for {len(missing_names)} names without gender info...")

    try:
        if missing_names:
            gender_map = get_genders_in_batches(missing_names)

            # Update only missing genders
            df.loc[missing_gender_mask, "Gender"] = df.loc[missing_gender_mask, "Full Name"].map(gender_map)
        else:
            print("✅ No missing gender values found. Skipping API requests.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        # Save progress regardless of success or error
        output_file = "enhanced_salesforce_report.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n💾 Progress saved to '{output_file}' (even if an error occurred).")

    print("✅ Script finished.")
