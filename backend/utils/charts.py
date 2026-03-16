from typing import List, Dict, Any

def suggest_chart(data: List[Dict[str, Any]]) -> str:
    """Detect chart type based on data columns."""
    if not data or len(data) == 0:
        return "none"
    
    # Single row with one numeric value -> KPI
    if len(data) == 1:
        nums = [v for v in data[0].values() if isinstance(v, (int, float))]
        if len(nums) == 1:
            return "kpi"
            
    columns = list(data[0].keys())
    
    # Look for time-based column
    time_keywords = ["date", "year", "month", "time", "timestamp", "day"]
    has_time = any(any(kw in col.lower() for kw in time_keywords) for col in columns)
    
    if has_time:
        return "line"
        
    # Check for categorical vs numeric
    numeric_cols = []
    categorical_cols = []
    
    for col in columns:
        val = data[0][col]
        if isinstance(val, (int, float)):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
            
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        # If low cardinality on categorical, pie is good
        unique_cats = set(row[categorical_cols[0]] for row in data)
        if len(unique_cats) <= 5:
            return "pie"
        return "bar"
        
    return "bar"
