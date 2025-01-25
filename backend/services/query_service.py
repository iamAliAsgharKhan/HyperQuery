import instructor
from groq import Groq
from pydantic import BaseModel
from typing import Optional
from ..config import settings
from ..database.schema_manager import SchemaManager

class SQLResponse(BaseModel):
    sql: str
    explanation: Optional[str] = None

class QueryService:
    def __init__(self):
        self.client = instructor.from_groq(
            Groq(api_key=settings.GROQ_API_KEY)
        )
        self.schema_manager = SchemaManager()
        self.system_prompt = f"""
        You are a SQL expert assistant. Convert natural language queries to SQL following these rules:
        1. Use only the following tables: {self.schema_manager.get_schema_prompt()}
        2. Always use explicit JOIN syntax
        3. Use table aliases for clarity
        4. Include only necessary columns
        5. Add LIMIT 100 unless specified
        6. Return valid SQL only
        """

    def generate_sql(self, user_query: str) -> SQLResponse:
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_model=SQLResponse
        )
        return response