import pandas as pd
import numpy as np

def generate_profile(df: pd.DataFrame) -> dict:
    """
    Auto data quality report — shown when user uploads a file.
    This is the Dataset Profiler feature (novel/resume-worthy).
    """
    profile = {}

    # Basic stats
    profile["total_rows"] = len(df)
    profile["total_columns"] = len(df.columns)
    profile["total_cells"] = len(df) * len(df.columns)

    # Missing values
    missing = df.isnull().sum()
    profile["missing_values"] = int(missing.sum())
    profile["missing_percent"] = round((missing.sum() / profile["total_cells"]) * 100, 2)
    profile["columns_with_missing"] = missing[missing > 0].to_dict()

    # Duplicates
    profile["duplicate_rows"] = int(df.duplicated().sum())

    # Column types
    profile["numeric_columns"] = df.select_dtypes(include="number").columns.tolist()
    profile["text_columns"] = df.select_dtypes(include="object").columns.tolist()
    profile["date_columns"] = df.select_dtypes(include="datetime").columns.tolist()

    # Numeric summaries
    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        profile["numeric_summary"] = num_df.describe().round(2).to_dict()

    # Outlier detection (IQR method)
    outlier_cols = {}
    for col in num_df.columns:
        Q1 = num_df[col].quantile(0.25)
        Q3 = num_df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((num_df[col] < Q1 - 1.5 * IQR) | 
                    (num_df[col] > Q3 + 1.5 * IQR)).sum()
        if outliers > 0:
            outlier_cols[col] = int(outliers)
    profile["outliers_detected"] = outlier_cols

    # Data health score (0-100)
    missing_score = max(0, 100 - profile["missing_percent"] * 10)
    dupe_score = max(0, 100 - (profile["duplicate_rows"] / len(df)) * 100)
    profile["data_health_score"] = round((missing_score + dupe_score) / 2, 1)

    return profile