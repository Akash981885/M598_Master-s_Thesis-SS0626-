from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    BASE_DIR / "outputs" / "verified_thematic_coding_results.csv"
)
OUTPUT_DIR = BASE_DIR / "outputs"


def create_theme_chart():
    if not INPUT_FILE.exists():
        print("Verified thematic results file not found.")
        print("Run python src/thematic_analysis.py first.")
        return

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "verified_theme",
        "eligible_for_final_analysis",
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        print("Required columns missing:", missing)
        return

    # Include only records eligible for final analysis.
    eligible = df[
        df["eligible_for_final_analysis"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1"])
    ].copy()

    eligible["verified_theme"] = (
        eligible["verified_theme"].fillna("").str.strip()
    )

    eligible = eligible[
        eligible["verified_theme"].ne("")
    ]

    if eligible.empty:
        print("No eligible verified themes are available.")
        print("Complete the manual review before charting.")
        return

    theme_counts = eligible["verified_theme"].value_counts()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ax = theme_counts.sort_values().plot(
        kind="barh",
        figsize=(9, 5),
        title="Verified Themes in Reviewed Literature",
    )

    ax.set_xlabel("Number of reviewed papers")
    ax.set_ylabel("Verified theme")

    for container in ax.containers:
        ax.bar_label(container, padding=3)

    plt.tight_layout()

    chart_file = OUTPUT_DIR / "verified_theme_frequency.png"
    plt.savefig(chart_file, dpi=300, bbox_inches="tight")
    plt.close()

    print("Eligible reviewed papers:", len(eligible))
    print("\nVerified theme counts:")
    print(theme_counts.to_string())
    print("\nChart saved to:", chart_file)


if __name__ == "__main__":
    create_theme_chart()
