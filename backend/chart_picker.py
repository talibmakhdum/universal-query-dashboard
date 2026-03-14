from typing import List, Dict, Any
import math

class ChartPicker:
    def pick_chart_type(self, data: List[Dict[str, Any]], schema: Dict[str, str]) -> str:
        """
        Determine the appropriate chart type based on the data structure and schema.
        """
        if not data:
            return 'bar'  # Default fallback
        
        # Get the keys from the first row to understand the structure
        keys = list(data[0].keys()) if data else []
        
        # Case 1: KPI card - single value or single row with one numeric field
        if len(data) == 1:
            numeric_fields = self._get_numeric_fields(data[0])
            if len(numeric_fields) == 1:
                return 'kpi'
        
        # Case 2: Time series - if we have a date/datetime column
        date_col = self._find_date_column(keys)
        if date_col:
            return 'line'
        
        # Case 3: Categorical data with low cardinality - pie chart
        categorical_col = self._find_categorical_column(keys, data, schema)
        if categorical_col:
            unique_values = set(row[categorical_col] for row in data if categorical_col in row)
            if len(unique_values) <= 10:  # Low cardinality
                return 'pie'
        
        # Case 4: Default to bar chart for other aggregations
        return 'bar'
    
    def _get_numeric_fields(self, row: Dict[str, Any]) -> List[str]:
        """
        Identify which fields in a row contain numeric values.
        """
        numeric_fields = []
        for key, value in row.items():
            if isinstance(value, (int, float)) or (isinstance(value, str) and self._is_numeric_string(value)):
                numeric_fields.append(key)
        return numeric_fields
    
    def _is_numeric_string(self, s: str) -> bool:
        """
        Check if a string represents a numeric value.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def _find_date_column(self, keys: List[str]) -> str | None:
        """
        Look for a column that might represent dates.
        """
        date_indicators = ['date', 'time', 'year', 'month', 'day']
        for key in keys:
            lower_key = key.lower()
            for indicator in date_indicators:
                if indicator in lower_key:
                    return key
        return None
    
    def _find_categorical_column(self, keys: List[str], data: List[Dict[str, Any]], schema: Dict[str, str]) -> str | None:
        """
        Look for a categorical column that could be used for pie charts.
        """
        for key in keys:
            # Check if it's not numeric in schema
            if 'int' not in schema[key].lower() and 'float' not in schema[key].lower():
                # Check if there are reasonable number of unique values
                unique_values = set(row[key] for row in data if key in row)
                if 2 <= len(unique_values) <= 10:  # Between 2 and 10 unique values
                    return key
        return None