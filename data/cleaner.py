import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean dataframe and return cleaned df + cleaning report.
    """
    report = {}
    original_shape = df.shape

    # 1. Remove fully duplicate rows
    dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    report["duplicates_removed"] = int(dupes)

    # 2. Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # 3. Fix common date columns
    date_keywords = ["date", "order_date", "ship_date"]
    for col in df.columns:
        if any(kw in col.lower() for kw in date_keywords):
            try:
                df[col] = pd.to_datetime(df[col], dayfirst=False, errors="coerce")
            except Exception:
                pass

    # 4. Fill missing numeric values with median
    num_cols = df.select_dtypes(include="number").columns
    missing_numeric = df[num_cols].isnull().sum().sum()
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())

    # 5. Fill missing text values with "Unknown"
    missing_text = df[str_cols].isnull().sum().sum()
    for col in str_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna("Unknown")

    report["missing_numeric_filled"] = int(missing_numeric)
    report["missing_text_filled"] = int(missing_text)
    report["original_shape"] = original_shape
    report["final_shape"] = df.shape
    report["rows_after_cleaning"] = len(df)

    print(f"✅ Cleaning done: {report}")
    return df, report


def validate_superstore_schema(df: pd.DataFrame) -> tuple[bool, list]:
    """
    Check if the dataframe has expected Superstore columns.
    Returns (is_valid, missing_columns)
    """
    expected_cols = [
        "order_id", "order_date", "ship_date", "ship_mode",
        "customer_id", "customer_name", "segment", "country",
        "city", "state", "region", "product_id", "category",
        "sub_category", "product_name", "sales", "quantity",
        "discount", "profit"
    ]
    
    actual_cols = df.columns.tolist()
    missing = [col for col in expected_cols if col not in actual_cols]
    
    is_valid = len(missing) == 0
    return is_valid, missing