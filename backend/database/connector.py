# backend/database/connector.py
from ..config import settings
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def convert_date(val):
    return datetime.strptime(val.decode(), "%Y-%m-%d").date()

def convert_timestamp(val):
    """Handle multiple timestamp formats including ISO 8601 with microseconds"""
    decoded = val.decode()
    
    # Try ISO format with T separator and microseconds
    try:
        return datetime.strptime(decoded, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    
    # Try ISO format without microseconds
    try:
        return datetime.strptime(decoded, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    
    # Try space-separated format with microseconds
    try:
        return datetime.strptime(decoded, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    
    # Try space-separated format without microseconds
    try:
        return datetime.strptime(decoded, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # Fallback to date-only
    try:
        return datetime.strptime(decoded, "%Y-%m-%d")
    except ValueError:
        logger.warning(f"Failed to parse timestamp: {decoded}")
        return decoded  # Return raw value if all parsing fails

# Update the adapter to use ISO format
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())

class DatabaseConnector:
    @contextmanager
    def get_connection(self):
        """Create connection with custom type handlers"""
        logger.debug("Creating new SQLite connection")
        try:
            conn = sqlite3.connect(
                settings.DATABASE_PATH,
                timeout=20,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False
            )
            # Register type handlers
            conn.execute("PRAGMA journal_mode=WAL")
            sqlite3.register_converter('date', convert_date)
            sqlite3.register_converter('timestamp', convert_timestamp)
            sqlite3.register_adapter(datetime, lambda dt: dt.isoformat(' '))
            
            conn.row_factory = sqlite3.Row
            logger.debug(f"Connection opened: {id(conn)}")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Connection error: {str(e)}")
            raise
        finally:
            logger.debug(f"Closing connection: {id(conn)}")
            conn.close()

    def execute_safe_query(self, query: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute query with error handling"""
        logger.debug(f"Executing query: {query}")
        
        clean_query = query.strip().upper()
        if not any(clean_query.startswith(op) for op in settings.ALLOWED_OPERATIONS):
            logger.error(f"Invalid query type: {query}")
            raise ValueError(f"Only {settings.ALLOWED_OPERATIONS} queries allowed")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                logger.debug(f"Cursor created: {id(cursor)}")
                cursor.execute(query)
                logger.debug("Query executed successfully")

                # Handle empty results
                if cursor.description is None:
                    return [], []

                columns = [col[0] for col in cursor.description]
                results = []
                
                # Process rows with error handling
                for row in cursor:
                    try:
                        results.append(dict(row))
                    except sqlite3.ProgrammingError as e:
                        logger.error(f"Row processing error: {str(e)}")
                        continue

                logger.info(f"Returning {len(results)} rows, {len(columns)} columns")
                return results, columns

            except sqlite3.Error as e:
                logger.error(f"SQL Error: {str(e)}")
                raise RuntimeError(f"Database Error: {str(e)}")
            finally:
                logger.debug(f"Closing cursor: {id(cursor)}")
                cursor.close()