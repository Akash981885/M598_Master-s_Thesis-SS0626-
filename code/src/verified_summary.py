
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "outputs" / "manual_review_template.csv"
)

OUTPUT_DIR = BASE_DIR / "outputs"

THEMES = [
    "Human Error",
    "Awareness Programmes",
    "Security Culture",
]

def create_verified_summary():
    df = pd.read_csv(INPUT_FILE)

    # Only include records explicitly marked as reviewed
    reviewed = df[
        df["review_status"].astype(str).str.strip().str.lower()
        == "reviewed"
    ].copy()

    if reviewed.empty:
        print("No reviewed records found yet.")
        print("Review the CSV against original research papers.")
        print("Do not count automatic suggestions as verified.")
        return

    # Count reviewed records by verified theme
    counts = {theme: 0 for theme in THEMES}

    for value in reviewed["verified_theme"].fillna(""):
        assigned = [
            theme.strip()
            for theme in str(value).split(";")
            if theme.strip()
        ]

        for theme in set(assigned):
            if theme in counts:
                counts[theme] += 1

    summary = pd.DataFrame(
        [
            {"Theme": theme, "Reviewed records": count}
            for theme, count in counts.items()
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "verified_theme_summary.csv"
    summary.to_csv(csv_path, index=False)

    print("\nVerified theme summary:")
    print(summary.to_string(index=False))
    print("\nSaved:", csv_path)

    # Create chart only from reviewed classifications
    chart = summary.set_index("Theme")["Reviewed records"]

    ax = chart.sort_values().plot(
        kind="barh",
        figsize=(9, 5),
        title="Manually Verified Research Themes",
    )

    ax.set_xlabel("Number of reviewed records")
    ax.set_ylabel("Theme")

    plt.tight_layout()

    image_path = OUTPUT_DIR / "verified_theme_summary.png"
    plt.savefig(image_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Chart saved:", image_path)

if __name__ == "__main__":
    create_verified_summary()
