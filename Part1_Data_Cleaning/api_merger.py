import pandas as pd
import requests
from tqdm import tqdm

def enhance_gender(df: pd.DataFrame, name_col: str = "Full Name") -> pd.DataFrame:
    """
    Receives a DataFrame with a column of full names and returns the same DataFrame
    with an added 'Gender' column filled using the Genderize.io API.
    Only updates rows where gender is missing.
    It only can fill 1000 names per day for free (100 per hour).
    """
    # Ensure the Gender column exists
    if "Gender" not in df.columns:
        df["Gender"] = None

    # Filter names missing gender
    missing_mask = df["Gender"].isna() | (df["Gender"] == "")
    missing_names = df.loc[missing_mask, name_col].dropna().astype(str).str.strip().unique().tolist()

    # Fetch gender for each name 
    gender_map = {}
    for name in tqdm(missing_names, desc="Fetching genders"):
        try:
            response = requests.get("https://api.genderize.io", params={"name": name})
            data = response.json()
            gender_map[name] = data.get("gender")
        except Exception:
            gender_map[name] = None

    # Map results back to DataFrame
    df.loc[missing_mask, "Gender"] = df.loc[missing_mask, name_col].map(gender_map)

    # Capitalize first letter
    df["Gender"] = df["Gender"].str.capitalize()

    return df

# For our data:
if __name__ == "__main__":
    df = pd.read_excel("cleaned_salesforce_report.xlsx")
    enhanced_df = enhance_gender(df)
    enhanced_df.to_excel("enhanced_salesforce_report.xlsx", index=False)
    print("Gender column updated and saved!")
