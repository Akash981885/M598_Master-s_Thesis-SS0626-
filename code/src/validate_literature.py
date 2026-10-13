
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "literature_register.csv"
)

OUTPUT_DIR = BASE_DIR / "outputs"

REQUIRED_COLUMNS = [
    "paper_id",
    "paper_title",
    "authors",
    "year",
    "journal_or_publisher",
    "doi_or_url",
    "search_database",
    "screening_decision",
    "exclusion_reason",
]

def validate_literature():
    print("Validating literature register...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # Check the required column names
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        print("Missing columns:", missing_columns)
        print("Check the header row in the CSV file.")
        return

    if df.empty:
        print("The register contains no literature records yet.")
        print("This is expected because only the header exists.")
        return

    # Remove accidental spaces in text fields
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    # Check for missing information
    df["missing_fields"] = ""

    for column in REQUIRED_COLUMNS:
        missing = (
            df[column].isna()
            | df[column].astype(str).str.strip().eq("")
        )

        df.loc[missing, "missing_fields"] += (
            column + "; "
        )

    # Check duplicate paper IDs
    df["duplicate_paper_id"] = (
        df["paper_id"].duplicated(keep=False)
        & df["paper_id"].notna()
    )

    # Check publication year
    df["year"] = pd.to_numeric(
        df["year"], errors="coerce"
    )

    current_year = pd.Timestamp.now().year

    df["year_valid"] = (
        df["year"].notna()
        & df["year"].between(1900, current_year)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR / "literature_validation_report.csv"
    )

    df.to_csv(output_file, index=False)

    print("Validation completed.")
    print("Records checked:", len(df))
    print(
        "Records with missing fields:",
        df["missing_fields"].ne("").sum()
    )
    print(
        "Duplicate paper IDs:",
        df["duplicate_paper_id"].sum()
    )
    print(
        "Invalid publication years:",
        (~df["year_valid"]).sum()
    )
    print("Report saved to:", output_file)

if __name__ == "__main__":
    validate_literature()
