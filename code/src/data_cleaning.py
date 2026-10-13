from pathlib import Path
import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "research_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

def clean_research_data():
    print("Loading research dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "paper_id",
        "year",
        "topic",
        "findings",
        "source_type",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Remove duplicate records
    df = df.drop_duplicates(subset=["paper_id"])

    # Remove records without essential information
    df = df.dropna(
        subset=["paper_id", "year", "findings"]
    )

    # Standardise text fields
    for col in ["paper_id", "topic", "findings", "source_type"]:
        df[col] = df[col].astype(str).str.strip()

    # Convert publication year to a number
    df["year"] = pd.to_numeric(
        df["year"], errors="coerce"
    )

    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    # Save the cleaned dataset
    output_file = OUTPUT_DIR / "cleaned_research_data.csv"
    df.to_csv(output_file, index=False)

    print("Cleaning completed successfully.")
    print("Number of records:", len(df))
    print("Saved to:", output_file)

    print("\nPreview:")
    print(df.head())

if __name__ == "__main__":
    clean_research_data()
