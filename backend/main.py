from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict
from pathlib import Path
import os
import logging
logger = logging.getLogger(__name__)
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

# backend/main.py#
@app.post("/api/query")
async def handle_query(payload: Dict):
    try:
        logger.info(f"New query: {payload}")
        user_query = payload.get("query", "").strip()
        
        if not user_query:
            logger.warning("Empty query received")
            raise HTTPException(status_code=400, detail="Empty query")

        # SQL Generation
        logger.debug("Generating SQL...")
        sql_response = query_service.generate_sql(user_query)
        logger.info(f"Generated SQL: {sql_response.sql}")

        # Query Execution
        try:
            logger.debug("Executing database query...")
            print(f"Query received {sql_response}")
            results, columns = db.execute_safe_query(sql_response.sql)
            logger.debug(f"Execution results: {type(results)}, {type(columns)}")
            logger.info(f"Received {len(results)} rows, {len(columns)} columns")
        except RuntimeError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Result Validation
        if not isinstance(results, list) or not isinstance(columns, list):
            logger.error(f"Invalid result types: {type(results)}, {type(columns)}")
            raise HTTPException(status_code=500, detail="Invalid result format")

        if len(columns) == 0 and len(results) > 0:
            logger.error("Columns missing with non-empty results")
            raise HTTPException(status_code=500, detail="Data format mismatch")

        logger.debug("Generating HTML response...")
        return {
            "sql": sql_response.sql,
            "html": html_gen.generate_table(results, columns),
            "columns": columns,
            "row_count": len(results)
        }

    except HTTPException as he:
        logger.error(f"HTTP Error {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.critical(f"System failure: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
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