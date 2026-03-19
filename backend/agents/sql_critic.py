import re
from agents.state import AgentState

class SQLCritic:
    def __init__(self):
        # Enhanced forbidden patterns for comprehensive security
        self.forbidden_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b', 
            r'\bTRUNCATE\b', r'\bALTER\b', r'\bCREATE\b', r'\bGRANT\b',
            r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bSP_\w+',
            r'\bXP_\w+', r'\bOPENROWSET\b', r'\bOPENDATASOURCE\b'
        ]
        
        # SQL injection patterns
        self.injection_patterns = [
            r"'.*'.*OR.*'.*'.*=",  # Basic OR injection
            r"'.*'.*AND.*'.*'.*=",  # Basic AND injection
            r"'.*'.*UNION.*SELECT",  # UNION injection
            r"'.*'.*DROP.*TABLE",   # DROP injection
            r"'.*'.*INSERT.*INTO",  # INSERT injection
            r"'.*'.*UPDATE.*SET",   # UPDATE injection
            r"'.*'.*DELETE.*FROM",  # DELETE injection
            r"'.*'.*EXEC.*\(",      # EXEC injection
            r"'.*'.*EXECUTE.*\(",   # EXECUTE injection
            r"'.*'.*SP_\w+",        # Stored procedure injection
            r"'.*'.*XP_\w+",        # Extended procedure injection
            r"'.*'.*OPENROWSET",    # OPENROWSET injection
            r"'.*'.*OPENDATASOURCE", # OPENDATASOURCE injection
            r"'.*'.*WAITFOR.*DELAY", # Time-based injection
            r"'.*'.*BENCHMARK",     # Benchmark injection
            r"'.*'.*SLEEP",         # Sleep injection
            r"'.*'.*PG_SLEEP",      # PostgreSQL sleep
            r"'.*'.*DBMS_LOCK.SLEEP", # Oracle sleep
        ]
        
        # Performance anti-patterns
        self.performance_patterns = [
            r'SELECT\s+\*',  # SELECT * anti-pattern
            r'LIKE\s+\'%.*%\'',  # Leading wildcard
            r'ORDER\s+BY\s+\d+',  # ORDER BY column numbers
            r'GROUP\s+BY\s+\d+',  # GROUP BY column numbers
            r'WHERE\s+1\s*=\s*1',  # Always true condition
            r'WHERE\s+0\s*=\s*0',  # Always true condition
            r'WHERE\s+1\s*=\s*0',  # Always false condition
            r'WHERE\s+0\s*=\s*1',  # Always false condition
            r'NOT\s+IN\s*\(',      # NOT IN performance issue
            r'NOT\s+EXISTS\s*\(',  # NOT EXISTS performance issue
            r'OR\s+\d+\s*=\s*\d+',  # OR with constants
            r'AND\s+\d+\s*=\s*\d+', # AND with constants
        ]

    def validate(self, state: AgentState) -> AgentState:
        state["thought_process"].append("SQL Critic: Performing comprehensive security and performance validation...")
        
        sql = state["sql_query"]
        sql_upper = sql.upper().strip()
        
        # 1. Security validation
        security_issues = self._check_security(sql_upper)
        if security_issues:
            state["critic_error"] = f"Security Violation: {security_issues[0]}"
            state["thought_process"].append(f"Critic: {state['critic_error']}")
            return state
        
        # 2. SQL injection validation
        injection_issues = self._check_injection(sql)
        if injection_issues:
            state["critic_error"] = f"SQL Injection Risk: {injection_issues[0]}"
            state["thought_process"].append(f"Critic: {state['critic_error']}")
            return state
        
        # 3. Query type validation
        if not sql_upper.startswith("SELECT"):
            state["critic_error"] = "Invalid Query: Must be a SELECT statement."
            state["thought_process"].append(f"Critic: {state['critic_error']}")
            return state
        
        # 4. Schema validation
        schema_issues = self._validate_schema(sql, state.get('schema', ''))
        if schema_issues:
            state["critic_error"] = f"Schema Violation: {schema_issues[0]}"
            state["thought_process"].append(f"Critic: {state['critic_error']}")
            return state
        
        # 5. Performance validation
        performance_issues = self._check_performance(sql_upper)
        if performance_issues:
            # Performance issues are warnings, not errors
            state["thought_process"].append(f"Critic Warning: Performance issue detected - {performance_issues[0]}")
        
        # 6. SQL syntax validation
        syntax_issues = self._validate_syntax(sql)
        if syntax_issues:
            state["critic_error"] = f"Syntax Error: {syntax_issues[0]}"
            state["thought_process"].append(f"Critic: {state['critic_error']}")
            return state

        state["critic_error"] = None
        state["thought_process"].append("SQL Critic: Query validation passed successfully")
        return state

    def _check_security(self, sql: str) -> list:
        """Check for forbidden SQL operations."""
        issues = []
        for pattern in self.forbidden_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                forbidden_word = re.search(pattern, sql, re.IGNORECASE).group()
                issues.append(f"'{forbidden_word}' operations are not allowed for security reasons.")
        return issues

    def _check_injection(self, sql: str) -> list:
        """Check for SQL injection patterns."""
        issues = []
        for pattern in self.injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append("Potential SQL injection detected. Please use parameterized queries.")
                break  # Only report the first injection pattern found
        return issues

    def _validate_schema(self, sql: str, schema: str) -> list:
        """Validate that the query uses valid schema elements."""
        issues = []
        
        if not schema:
            return issues  # Skip validation if no schema provided
        
        # Extract column names from schema
        schema_columns = set()
        for col in schema.split(','):
            col_name = col.split('(')[0].strip()
            schema_columns.add(col_name.lower())
        
        # Extract column references from SQL
        # This is a simplified check - in production, you'd want a proper SQL parser
        column_patterns = [
            r'SELECT\s+([^FROM]+)',
            r'FROM\s+\w+\s+WHERE\s+([^=]+)',
            r'ORDER\s+BY\s+([^,\s]+)',
            r'GROUP\s+BY\s+([^,\s]+)',
            r'JOIN\s+\w+\s+ON\s+([^=]+)'
        ]
        
        for pattern in column_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            for match in matches:
                # Extract individual column names
                columns = re.findall(r'\b\w+\b', match)
                for col in columns:
                    if col.lower() not in schema_columns and col.lower() not in ['and', 'or', 'not', 'in', 'exists', 'between', 'like', 'is', 'null', 'distinct']:
                        issues.append(f"Column '{col}' not found in schema.")
        
        return issues

    def _check_performance(self, sql: str) -> list:
        """Check for performance anti-patterns."""
        issues = []
        for pattern in self.performance_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                if 'SELECT *' in pattern:
                    issues.append("Use specific column names instead of SELECT * for better performance.")
                elif 'LIKE' in pattern:
                    issues.append("Leading wildcards in LIKE clauses can cause performance issues.")
                elif 'ORDER BY' in pattern or 'GROUP BY' in pattern:
                    issues.append("Avoid using column numbers in ORDER BY and GROUP BY clauses.")
                elif 'NOT IN' in pattern or 'NOT EXISTS' in pattern:
                    issues.append("NOT IN and NOT EXISTS can be slow on large datasets.")
                break  # Only report the first performance issue
        return issues

    def _validate_syntax(self, sql: str) -> list:
        """Basic SQL syntax validation."""
        issues = []
        
        # Check for balanced parentheses
        open_parens = sql.count('(')
        close_parens = sql.count(')')
        if open_parens != close_parens:
            issues.append("Unbalanced parentheses detected.")
        
        # Check for basic SELECT structure
        if not re.search(r'SELECT\s+.*\s+FROM\s+\w+', sql, re.IGNORECASE):
            issues.append("Invalid SELECT statement structure.")
        
        # Check for common syntax errors
        if re.search(r',\s*,', sql):  # Double commas
            issues.append("Double commas detected.")
        
        return issues
