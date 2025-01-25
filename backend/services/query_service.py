#query_service.py
import instructor
from groq import Groq
from pydantic import BaseModel
from ..config import settings
from ..database.schema_manager import SchemaManager
import re

class SQLResponse(BaseModel):
    sql: str

class QueryService:
    def __init__(self):
        self.client = instructor.from_groq(Groq(api_key=settings.GROQ_API_KEY))
        self.schema_manager = SchemaManager()
        self.base_prompt = f"""
        You are a SQLite expert. Convert natural language queries to SQL following these rules:
        
        Database Schema:
        {self.schema_manager.get_schema_prompt()}
        
        SQLite-Specific Requirements:
        1. Use SQLite date functions (DATE(), STRFTIME())
        2. No stored procedures or user-defined functions
        3. Table names are case-sensitive
        4. Use LIMIT instead of TOP
        5. Always qualify column names with table aliases
        6. Use explicit JOIN syntax
        7. Include only columns that exist in the schema
        8. Never include semicolons
        9. Return only valid SQLite SELECT queries
        
        Example Valid Response:
        SELECT c.name, o.order_date 
        FROM customers AS c
        JOIN orders AS o ON c.id = o.customer_id
        WHERE o.amount > 100
        ORDER BY o.order_date DESC
        LIMIT 10
        """

    def generate_sql(self, user_query: str) -> SQLResponse:
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": self.base_prompt},
                {"role": "user", "content": f"Query: {user_query}\nSQL:"}
            ],
            response_model=SQLResponse,
            temperature=0.1
        )

         # print(response.sql)

        validated_sql = self._validate_sql(response.sql)
        
        # Additional SQLite syntax check
        if "FROM" not in validated_sql.sql.upper():
            raise ValueError("Invalid SQL: Missing FROM clause")
            
        return validated_sql

    def _validate_sql(self, sql: str) -> SQLResponse:
        """Basic SQL validation"""
        sql = sql.strip().rstrip(';')

        if not sql.upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        if "SELECT *" in sql.upper():
            sql = self._expand_star_selector(sql)
        return SQLResponse(sql=sql)
    
    def _expand_star_selector(self, sql: str) -> str:
        """Convert SELECT * to explicit columns using schema"""
        schema = self.schema_manager.get_full_schema()
        table_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
        
        if not table_match:
            return sql
            
        table = table_match.group(1)
        if table not in schema:
            return sql
            
        columns = ", ".join(schema[table])
        return re.sub(r"\*", columns, sql, count=1)