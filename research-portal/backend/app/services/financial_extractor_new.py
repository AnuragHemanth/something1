import re
from typing import Dict, List, Tuple, Optional


def detect_currency_and_unit(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Detect currency and measurement units from document."""
    text_upper = text.upper()
    first_2000_chars = text_upper[:2000]
    
    currency = None
    if 'INR' in text_upper:
        currency = 'INR'
    elif 'USD' in text_upper:
        currency = 'USD'
    elif 'EUR' in text_upper:
        currency = 'EUR'
    elif 'GBP' in text_upper:
        currency = 'GBP'
    
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
    """Extract and clean numeric values."""
    if not value_str:
        return "NA"
    
    value_str = value_str.strip()
    
    if value_str in ['-', '–', '—', 'NA', 'N/A', '']:
        return 'NA'
    
    cleaned = value_str.replace(' ', '').strip()
    
    if not cleaned or cleaned == '':
        return 'NA'
    
    if re.search(r'\d', cleaned):
        cleaned = re.sub(r'[₹$€£]', '', cleaned)
        cleaned = re.sub(r'[^\d.,\-]', '', cleaned)
        return cleaned if cleaned else 'NA'
    
    return 'NA'


def extract_financial_data(text: str) -> Dict:
    """
    Extract financial data from tables by finding lines with financial keywords
    and numeric values, then extracting all numbers from those lines.
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
        'gross', 'operating', 'ebit', 'ebitda','tax', 'net',
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
        print(f"[DEBUG] Line {idx}: {line[:80]}")
        
        # Extract all numbers from the line
        numbers = re.findall(r'[\d,.\-]+', line)
        
        if not numbers:
            continue
        
        # The first part (before numbers) is the item name
        # Find where first number starts
        first_num_pos = re.search(r'[\d,.\-]+', line)
        if first_num_pos:
            item_name = line[:first_num_pos.start()].strip()
        else:
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
        
        if len(collected_rows) <= 5:
            print(f"[DEBUG]  Row {len(collected_rows)}: {item_name[:30]}... -> {cleaned_values[:3]}")
        
        # Stop if we have enough rows
        if len(collected_rows) >= 15:
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
