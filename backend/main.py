from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict
from pathlib import Path
import os

# Local imports
from .config import settings
from .database.connector import DatabaseConnector
from .services.query_service import QueryService
from .services.html_generator import HTMLGenerator

# Initialize app
app = FastAPI()

# Configure paths
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Verify frontend directory
if not FRONTEND_DIR.exists():
    raise RuntimeError(f"Frontend directory not found at: {FRONTEND_DIR}")

# Initialize services
db = DatabaseConnector()
query_service = QueryService()
html_gen = HTMLGenerator()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/query")
async def handle_query(payload: Dict):
    try:
        user_query = payload.get("query", "")
        
        # Generate SQL
        sql_response = query_service.generate_sql(user_query)
        
        # Execute Query
        results, columns = db.execute_safe_query(sql_response.sql)
        
        # Generate HTML
        html = html_gen.generate_table(results, columns)
        
        return {
            "sql": sql_response.sql,
            "html": html,
            "columns": columns,
            "row_count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve frontend files
app.mount(
    "/", 
    StaticFiles(directory=str(FRONTEND_DIR), html=True), 
    name="frontend"
)

# Debug output
print(f"\n{'='*50}")
print(f"Frontend path: {FRONTEND_DIR}")
print(f"Directory exists: {FRONTEND_DIR.exists()}")
print(f"Files found: {len(list(FRONTEND_DIR.glob('*')))} files")
print(f"Index.html exists: {(FRONTEND_DIR/'index.html').exists()}")
print(f"Current working directory: {os.getcwd()}")
print(f"{'='*50}\n")