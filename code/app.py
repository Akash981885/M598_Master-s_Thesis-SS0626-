
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

LITERATURE_FILE = DATA_DIR / "literature_register.csv"
REVIEW_FILE = DATA_DIR / "verified_paper_review.csv"
RESULTS_FILE = OUTPUT_DIR / "verified_thematic_coding_results.csv"
CHART_FILE = OUTPUT_DIR / "verified_theme_frequency.png"

st.set_page_config(
    page_title="Cybersecurity Awareness Research",
    page_icon="🔐",
    layout="wide",
)

st.title("Cybersecurity Awareness Research")
st.caption(
    "Python-based literature management, manual review "
    "and thematic analysis"
)

st.warning(
    "Research limitation: this dashboard currently contains "
    "only one reviewed paper. Its results demonstrate the "
    "software workflow and are not sufficient to establish "
    "general conclusions about employee cybersecurity awareness."
)


def load_csv(file_path):
    """Load a CSV file safely."""
    if not file_path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path).fillna("")
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Could not read {file_path.name}: {error}")
        return pd.DataFrame()


literature_df = load_csv(LITERATURE_FILE)
review_df = load_csv(REVIEW_FILE)
results_df = load_csv(RESULTS_FILE)


def is_eligible(value):
    """Handle Boolean values and Boolean strings from CSV files."""
    return str(value).strip().lower() in ("true", "1", "yes")


# Count review statuses
if not review_df.empty and "review_status" in review_df.columns:
    statuses = review_df["review_status"].astype(str).str.strip().str.lower()
    reviewed_count = int(statuses.isin(["reviewed", "complete", "completed"]).sum())
    pending_count = int((~statuses.isin(["reviewed", "complete", "completed"])).sum())
else:
    reviewed_count = 0
    pending_count = 0

if (
    not results_df.empty
    and "eligible_for_final_analysis" in results_df.columns
):
    eligible_df = results_df[
        results_df["eligible_for_final_analysis"].apply(is_eligible)
    ].copy()
else:
    eligible_df = pd.DataFrame()

if not eligible_df.empty and "verified_theme" in eligible_df.columns:
    eligible_df["verified_theme"] = (
        eligible_df["verified_theme"].astype(str).str.strip()
    )
    eligible_df = eligible_df[eligible_df["verified_theme"] != ""]

# Dashboard metrics
st.subheader("Research overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Literature records", len(literature_df))
col2.metric("Review records", len(review_df))
col3.metric("Reviewed records", reviewed_count)
col4.metric("Pending records", pending_count)

st.caption(
    "Counts describe records entered in the project files. "
    "A reviewed record is not automatically proof that its "
    "interpretation is correct."
)

# Literature register
st.subheader("1. Literature register")

if not literature_df.empty:
    st.dataframe(literature_df, width="stretch")
else:
    st.info("No literature records are available yet.")

# Manual review and evidence
st.subheader("2. Manual review and evidence")

if not review_df.empty:
    display_columns = [
        column for column in [
            "paper_id",
            "year",
            "topic",
            "findings",
            "candidate_themes",
            "verified_theme",
            "evidence_from_paper",
            "review_status",
            "reviewer_notes",
        ]
        if column in review_df.columns
    ]

    st.dataframe(
        review_df[display_columns],
        width="stretch",
    )
else:
    st.info("No paper-review records were found.")

# Verified themes
st.subheader("3. Verified thematic analysis")

if not eligible_df.empty:
    theme_counts = eligible_df["verified_theme"].value_counts()
    theme_summary = theme_counts.rename_axis("Verified theme").reset_index(
        name="Number of reviewed papers"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(theme_summary, width="stretch")

    with col2:
        st.metric("Eligible reviewed records", len(eligible_df))
        st.metric("Distinct verified themes", len(theme_counts))

    if CHART_FILE.exists():
        st.image(
            str(CHART_FILE),
            caption="Verified themes in reviewed literature",
            width="stretch",
        )
    else:
        st.info(
            "The verified theme chart is not available. "
            "Run python src/visualise_results.py."
        )

    st.markdown("**Records included in final theme counts**")
    evidence_columns = [
        column for column in [
            "paper_id",
            "year",
            "topic",
            "verified_theme",
            "evidence_from_paper",
            "reviewer_notes",
        ]
        if column in eligible_df.columns
    ]
    st.dataframe(
        eligible_df[evidence_columns],
        width="stretch",
    )
else:
    st.info(
        "No records currently qualify for final thematic analysis. "
        "Complete the manual review, verified theme and supporting "
        "evidence before generating final counts."
    )

# Downloads
st.subheader("4. Download research outputs")

if LITERATURE_FILE.exists():
    st.download_button(
        "Download literature register",
        data=LITERATURE_FILE.read_bytes(),
        file_name="literature_register.csv",
        mime="text/csv",
    )

if REVIEW_FILE.exists():
    st.download_button(
        "Download paper-review file",
        data=REVIEW_FILE.read_bytes(),
        file_name="verified_paper_review.csv",
        mime="text/csv",
    )

if RESULTS_FILE.exists():
    st.download_button(
        "Download verified analysis results",
        data=RESULTS_FILE.read_bytes(),
        file_name="verified_thematic_coding_results.csv",
        mime="text/csv",
    )

st.info(
    "Methodological note: keyword matching generates provisional "
    "suggestions. The researcher must assess each paper, verify the "
    "supporting evidence and justify the final theme. Theme counts "
    "describe this reviewed sample and do not establish causation."
)
