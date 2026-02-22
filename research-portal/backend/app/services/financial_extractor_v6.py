import re
from typing import Dict, List, Tuple, Optional


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
        Cleaned numeric string or "NA"
    """
    if not value_str:
        return "NA"
    
    value_str = value_str.strip()
    
    # Check for dash/empty
    if value_str in ['-', '–', '—', 'NA', 'N/A', '']:
        return 'NA'
    
    # Remove spaces and try to parse
    cleaned = value_str.replace(' ', '').strip()
    
    if not cleaned or cleaned == '':
        return 'NA'
    
    # If it contains any digits, return it (will be decimal, comma-separated, etc)
    if re.search(r'\d', cleaned):
        # Clean up: remove rupee symbols, currency signs
        cleaned = re.sub(r'[₹$€£]', '', cleaned)
        # Keep digits, dots, commas, minus signs
        cleaned = re.sub(r'[^\d.,\-]', '', cleaned)
        return cleaned if cleaned else 'NA'
    
    return 'NA'


def extract_financial_data(text: str) -> Dict:
    """
    Extract financial data from tables in the document.
    
    Strategy:
    1. Look for common financial keywords (Revenue, Expenses, Assets, etc.)
    2. When found, extract that row and subsequent similar rows
    3. Collect all rows until we hit a different section or end of data
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
    
    # Detect currency and unit
    currency, unit = detect_currency_and_unit(text)
    
    # Common financial statement keywords to look for
    # These are reliable indicators of financial data
    financial_keywords = [
        'revenue', 'income', 'expenses', 'cost', 'profit', 'loss', 
        'asset', 'liability', 'equity', 'cash', 'sales', 'purchase',
        'gross', 'operating', 'ebit', 'ebitda', 'tax', 'net',
        'depreciation', 'amortization', 'interest', 'dividend'
    ]
    
    # Search for lines containing financial keywords
    print("[DEBUG] Looking for financial data rows...")
    
    for idx, line in enumerate(lines):
        lower_line = line.lower()
        
        # Check if this line contains financial keywords
        has_financial_keyword = any(keyword in lower_line for keyword in financial_keywords)
        
        if not has_financial_keyword:
            continue
        
        # Found a potential financial data section
        # Now collect this and adjacent rows
        print(f"[DEBUG] Found potential financial data at line {idx}: {line[:50]}...")
        
        # Go backward to find the header row
        header_row_idx = -1
        for offset in range(1, 20):
            check_idx = idx - offset
            if check_idx < 0:
                break
            check_line = lines[check_idx].strip()
            
            # Headers usually contain dates or column names
            # Look for lines with parentheses (dates), or multiple separated parts
            if '(' in check_line or '20' in check_line or '31/12' in check_line or '30/09' in check_line:
                header_row_idx = check_idx
                print(f"[DEBUG] Found header at line {check_idx}: {check_line[:50]}...")
                break
        
        # Now collect this and adjacent rows
        print(f"[DEBUG] Found potential financial data at line {idx}: {line[:50]}...")
        
        # Try to extract data from this line
        # Split by any amount of whitespace (2+ spaces or tabs)
        parts = re.split(r'\s{2,}|\t+', line)
        
        if len(parts) < 2:
            # Try with single space split
            # But be careful to preserve the first part (item name)
            # Format is usually: "ItemName Number Number Number ..."
            match = re.match(r'^([A-Za-z\s/()[-]+?)\s+([\d\s.,\-]*)', line)
            if match:
                parts = [match.group(1).strip(), match.group(2).strip()]
        
        if len(parts) < 2:
            continue
        
        # Start collecting rows
        table_rows = []
        seen_items = set()
        
        # We found one row, now collect similar rows in the vicinity
        for row_offset in range(-5, 50):  # Look 5 lines before and 50 after
            check_idx = idx + row_offset
            
            if check_idx < 0 or check_idx >= len(lines):
                continue
            
            row_text = lines[check_idx].strip()
            
            if not row_text or len(row_text) < 3:
                continue
            
            # Stop at next section "Particulars" or major break  
            lower_text = row_text.lower()
            if 'particulars' in lower_text or 'note' in lower_text and ':' in row_text:
                if check_idx > idx:  # Only stop if we're past the current row
                    print(f"[DEBUG] Stopping at section break: {row_text[:40]}")
                    break
            
            # Must have some numbers
            if not re.search(r'\d', row_text):
                continue
            
            # Try to parse the row
            row_parts = re.split(r'\s{2,}|\t+', row_text)
            
            if not row_parts or len(row_parts) < 1:
                continue
            
            item_name = row_parts[0].strip()
            
            # Skip if we've seen this exact item before
            if item_name in seen_items:
                continue
            
            # Skip very short items or obvious table elements
            if len(item_name) < 2 or item_name.startswith('|') or item_name.startswith('('):
                continue
            
            # Extract values - remaining parts or parse numbers from text
            values = []
            
            if len(row_parts) > 1:
                # Use split parts as values
                for part in row_parts[1:]:
                    values.append(extract_numeric_value(part))
            else:
                # Try to extract numbers from the line after the item name
                # Find where numbers start
                match = re.search(r'([\d,.\-]+)', row_text[len(item_name):])
                if match:
                    # Extract all numbers from remainder of line
                    number_parts = re.findall(r'[\d,.\-]+', row_text[len(item_name):])
                    for num_part in number_parts:
                        values.append(extract_numeric_value(num_part))
            
            if not values:
                continue
            
            # Add the row
            table_rows.append([item_name] + values)
            seen_items.add(item_name)
            
            if len(table_rows) <= 10:
                print(f"[DEBUG] Row {len(table_rows)}: {item_name[:35]}... -> {[str(v)[:10] for v in values[:3]]}")
        
        # If we found data rows, use them
        if table_rows and len(table_rows) >= 1:
            # Determine column count from first row
            num_cols = len(table_rows[0])
            
            # Create headers
            headers = ["Particulars"] + [f"Col_{i+1}" for i in range(num_cols - 1)]
            
            # Ensure all rows have same column count
            for row in table_rows:
                while len(row) < num_cols:
                    row.append("NA")
                del row[num_cols:]
            
            print(f"[DEBUG] Successfully extracted {len(table_rows)} financial data rows")
            return {
                "headers": headers,
                "rows": table_rows,
                "currency": currency,
                "unit": unit,
                "notes": None
            }
    
    # No valid table found
    print("[ERROR] No financial data rows found")
    return {
        "headers": [],
        "rows": [],
        "currency": currency,
        "unit": unit,
        "notes": ["Could not find financial data"]
    }
