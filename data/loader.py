import pandas as pd
import os


SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls"]

def load_file(filepath: str) -> pd.DataFrame:
    """Load CSV or Excel file into a DataFrame."""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}. Use CSV or Excel.")
    
    try:
        if ext == ".csv":
            df = pd.read_csv(filepath, encoding="utf-8")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
    except UnicodeDecodeError:
        # Handle encoding issues
        df = pd.read_csv(filepath, encoding="latin-1")
    
    # Clean column names: lowercase, replace spaces with underscores
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace("-", "_")
                  .str.replace("/", "_")
    )
    
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def get_column_info(df: pd.DataFrame) -> dict:
    """Return column names grouped by type."""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    
    return {
        "numeric": numeric_cols,
        "text": text_cols,
        "date": date_cols,
        "all": df.columns.tolist()
    }