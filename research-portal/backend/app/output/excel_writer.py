import pandas as pd
import os
from datetime import datetime


def write_to_excel(headers, rows):

    OUTPUT_DIR = "outputs"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not rows:
        raise ValueError("No rows to write")

    # Determine max number of columns
    max_cols = max(len(row) for row in rows)

    # Generate headers safely
    if headers and len(headers) >= max_cols:
        columns = headers[:max_cols]
    else:
        columns = ["Particulars"] + [f"FY_{i}" for i in range(1, max_cols)]

    df = pd.DataFrame(rows, columns=columns)

    filename = f"financial_output_{datetime.now().timestamp()}.xlsx"
    path = os.path.join(OUTPUT_DIR, filename)

    df.to_excel(path, index=False)

    return path
