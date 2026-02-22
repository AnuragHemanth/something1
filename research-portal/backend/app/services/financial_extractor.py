import re
from typing import Dict, List, Tuple, Optional, Union


def detect_currency_and_unit(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect currency and measurement units from document headers.
    
    Args:
        text: Document text
        
    Returns:
        Tuple of (currency, unit) or (None, None)
    """
    text_upper = text.upper()
    first_2000_chars = text_upper[:2000]  # Check headers/beginning
    
    # Detect currency
    currency = None
    if 'INR' in text_upper:
        currency = 'INR'
    elif 'USD' in text_upper:
        currency = 'USD'
    elif 'EUR' in text_upper:
        currency = 'EUR'
    elif 'GBP' in text_upper:
        currency = 'GBP'
    
    # Detect unit
    unit = None
    if 'LAKHS' in first_2000_chars or 'LAKH' in first_2000_chars:
        unit = 'Lakhs'
    elif 'CRORES' in first_2000_chars or 'CRORE' in first_2000_chars:
        unit = 'Crores'
    elif 'MILLIONS' in first_2000_chars or 'MILLION' in first_2000_chars:
        unit = 'Millions'
    elif 'THOUSANDS' in first_2000_chars or 'THOUSAND' in first_2000_chars:
        unit = 'Thousands'
    
    return currency, unit


def extract_numeric_value(value_str: str) -> str:
    """
    Extract and clean numeric values.
    Handles: 204813, 163,210, 9,756.31, –, -, NA, etc.
    
    Args:
        value_str: String containing numeric value
        
    Returns:
        Cleaned numeric string or "NA" if invalid/empty
    """
    value_str = value_str.strip()
    
    # Empty or dash indicators
    if not value_str or value_str in ['–', '-', '--', '−']:
        return "NA"
    
    if value_str.lower() in ['na', 'n/a']:
        return "NA"
    
    # Remove commas for formatting (keep decimals)
    cleaned = value_str.replace(',', '')
    
    # Verify it's actually numeric
    try:
        float(cleaned)
        return cleaned
    except ValueError:
        return "NA"


def detect_header_row(line: str) -> Optional[List[str]]:
    """
    Detect if line is a header row with FY columns.
    Handles formats like: "Particulars  FY 25  FY 24  FY 23  FY 22  FY 21  FY 20"
    
    Args:
        line: Text line to check
        
    Returns:
        List of headers or None if not a header row
    """
    # Look for FY pattern (FY 25, FY25, FY2025, FY25, etc)
    fy_matches = re.findall(r"FY\s*(\d{1,4})", line, re.IGNORECASE)
    
    if fy_matches and len(fy_matches) >= 2:
        # Format headers as "FY XX"
        headers = ["Particulars"] + [f"FY {year}" for year in fy_matches]
        return headers
    
    # Fallback: Look for just numbers that look like fiscal years (e.g., "25  24  23  22")
    # Only if line looks like numbers separated by spaces
    if re.search(r"^\s*\d{1,4}\s+\d{1,4}", line) and not re.search(r"[a-z]", line.lower()):
        # This might be year columns
        year_tokens = re.findall(r"\d{1,4}", line)
        if len(year_tokens) >= 2:
            headers = ["Particulars"] + [f"FY {year}" for year in year_tokens]
            return headers
    
    return None



def extract_financial_data(text: str) -> Dict:
    """
    Extract financial data from tables by finding lines with financial keywords
    and extracting numbers from them.
    """
    if not text or len(text.strip()) < 10:
        return {
            "headers": [],
            "rows": [],
            "currency": None,
            "unit": None,
            "notes": ["No extractable content found"]
        }
    
    lines = text.split("\n")
    print(f"[DEBUG] Total lines: {len(lines)}, Text length: {len(text)}")
    
    currency, unit = detect_currency_and_unit(text)
    
    # Financial statement keywords
    financial_keywords = [
        'revenue', 'income', 'expenses', 'cost', 'profit', 'loss',
        'asset', 'liability', 'equity', 'cash', 'sales', 'purchase',
        'gross', 'operating', 'ebit', 'ebitda', 'tax', 'net',
        'depreciation', 'amortization', 'interest', 'dividend'
    ]
    
    print("[DEBUG] Searching for financial data rows...")
    
    collected_rows = []
    headers = None
    num_columns = 0
    
    for idx, line in enumerate(lines):
        lower_line = line.lower()
        
        # Check for financial keyword
        has_keyword = any(kw in lower_line for kw in financial_keywords)
        
        if not has_keyword:
            continue
        
        # Must also have numbers
        if not re.search(r'\d', line):
            continue
        
        # Found a potential financial data row
        print(f"[DEBUG] Line {idx}: {line[:70]}")
        
        # Extract all numbers from the line
        numbers = re.findall(r'[\d,.\-]+', line)
        
        if not numbers:
            continue
        
        # The first part (before first number) is the item name
        first_num_pos = re.search(r'[\d,.\-]+', line)
        if first_num_pos:
            item_name = line[:first_num_pos.start()].strip()
        else:
            continue
        
        # Skip if item name is too short (likely spurious)
        if len(item_name) < 2:
            continue
        
        # Clean numbers
        cleaned_values = [extract_numeric_value(n) for n in numbers]
        
        # Create row
        row = [item_name] + cleaned_values
        collected_rows.append(row)
        
        # Set header info based on first row
        if not headers:
            num_columns = len(cleaned_values)
            headers = ["Particulars"] + [f"Col_{i+1}" for i in range(num_columns)]
            print(f"[DEBUG] Will use {num_columns} data columns")
        
        if len(collected_rows) <= 10:
            print(f"[DEBUG]  Row {len(collected_rows)}: {item_name[:35]}... -> {cleaned_values[:2]}")
        
        # Stop if we have enough rows
        if len(collected_rows) >= 20:
            print("[DEBUG] Collected enough rows, stopping")
            break
    
    # Process collected rows - ensure uniform column count
    if collected_rows and headers:
        print(f"[DEBUG] Processing {len(collected_rows)} collected rows")
        
        # Ensure all rows have same column count
        final_rows = []
        for row in collected_rows:
            item_name = row[0]
            values = row[1:]
            
            # Pad or trim to match expected columns
            while len(values) < num_columns:
                values.append("NA")
            values = values[:num_columns]
            
            final_rows.append([item_name] + values)
        
        if final_rows:
            print(f"[DEBUG] Successfully extracted {len(final_rows)} financial rows")
            return {
                "headers": headers,
                "rows": final_rows,
                "currency": currency,
                "unit": unit,
                "notes": None
            }
    
    print("[ERROR] No financial data extracted")
    return {
        "headers": [],
        "rows": [],
        "currency": currency,
        "unit": unit,
        "notes": ["No financial data found"]
    }

