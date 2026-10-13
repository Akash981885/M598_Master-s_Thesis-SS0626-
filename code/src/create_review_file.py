
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "outputs" / "thematic_coding_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "outputs" / "manual_review_template.csv"
)

def create_review_file():
    df = pd.read_csv(INPUT_FILE)

    review_columns = [
        "paper_id",
        "year",
        "topic",
        "findings",
        "candidate_themes",
        "matched_keywords",
    ]

    review_df = df[review_columns].copy()

    # Fields for researcher validation
    review_df["verified_theme"] = ""
    review_df["evidence_from_paper"] = ""
    review_df["review_status"] = "Pending"
    review_df["reviewer_notes"] = ""

    review_df.to_csv(OUTPUT_FILE, index=False)

    print("Manual-review template created.")
    print("Records requiring review:", len(review_df))
    print("Output file:", OUTPUT_FILE)

if __name__ == "__main__":
    create_review_file()
