from .connector import DatabaseConnector

class SchemaManager:
    def __init__(self):
        self.db = DatabaseConnector()

    def get_full_schema(self) -> dict:
        schema = {}
        tables, _ = self.db.execute_safe_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        for table in tables:
            table_name = table['name']
            columns, _ = self.db.execute_safe_query(
                f"PRAGMA table_info({table_name})"
            )
            schema[table_name] = [col['name'] for col in columns]
        return schema

    def get_schema_prompt(self) -> str:
        schema = self.get_full_schema()
        prompt = "Database Schema:\n"
        for table, columns in schema.items():
            prompt += f"- {table} ({', '.join(columns)})\n"
        return prompt