
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "verified_paper_review.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

THEMES = {
    "Human Error": [
        "human error",
        "phishing",
        "social engineering",
        "weak passwords",
        "password practices",
        "negligence",
        "mistake",
    ],
    "Awareness Programmes": [
        "training",
        "awareness",
        "practical exercises",
        "recognition",
        "education",
        "behavioural measures",
    ],
    "Security Culture": [
        "leadership",
        "security culture",
        "policies",
        "compliance",
        "secure employee behaviour",
        "organisational culture",
    ],
}


def assign_themes(text):
    text = str(text).lower()
    matched_themes = []
    matched_keywords = []

    for theme, keywords in THEMES.items():
        found = [
            keyword for keyword in keywords
            if keyword in text
        ]

        if found:
            matched_themes.append(theme)
            matched_keywords.extend(found)

    return pd.Series({
        "candidate_themes": "; ".join(matched_themes),
        "matched_keywords": "; ".join(
            dict.fromkeys(matched_keywords)
        ),
    })


def run_thematic_analysis():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Review file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE).fillna("")

    required_columns = [
        "paper_id",
        "topic",
        "findings",
        "verified_theme",
        "evidence_from_paper",
        "review_status",
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Generate provisional keyword suggestions.
    text_to_analyse = (
        df["topic"].astype(str) + " " +
        df["findings"].astype(str) + " " +
        df["evidence_from_paper"].astype(str)
    )

    suggestions = text_to_analyse.apply(assign_themes)
    df["suggested_themes"] = suggestions["candidate_themes"]
    df["matched_keywords"] = suggestions["matched_keywords"]

    # A record is eligible for final analysis only when
    # its review, verified theme and evidence are present.
    reviewed = (
        df["review_status"].str.strip().str.lower()
        .isin(["reviewed", "complete", "completed"])
    )

    has_verified_theme = (
        df["verified_theme"].str.strip() != ""
    )

    has_evidence = (
        df["evidence_from_paper"].str.strip() != ""
    )

    df["eligible_for_final_analysis"] = (
        reviewed & has_verified_theme & has_evidence
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR / "verified_thematic_coding_results.csv"
    )
    df.to_csv(output_file, index=False)

    eligible = df[df["eligible_for_final_analysis"]].copy()

    print("Thematic analysis completed.")
    print("Review records:", len(df))
    print("Eligible for final analysis:", len(eligible))
    print("Pending or incomplete records:", len(df) - len(eligible))

    if eligible.empty:
        print(
            "\nNo records qualify for final analysis yet."
            "\nComplete the manual review and add a verified "
            "theme and supporting evidence from each paper."
        )
    else:
        print("\nVerified theme counts:")
        print(
            eligible["verified_theme"]
            .value_counts()
            .to_string()
        )

    print("\nSaved results to:", output_file)
    print("Keyword suggestions are provisional, not confirmed findings.")


if __name__ == "__main__":
    run_thematic_analysis()
