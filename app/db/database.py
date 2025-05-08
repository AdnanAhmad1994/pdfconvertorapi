"""
Database module for the PDF Converter API.
Provides functions for working with SQLite database.
"""

import os
import sqlite3
import json
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.conversion import ConversionStatus

logger = logging.getLogger(__name__)

# Define database path
DB_PATH = os.path.join(settings.TEMP_DIR, 'conversions.db')

def init_db():
    """Initialize the database and create required tables."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversion_tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            file_name TEXT NOT NULL,
            format TEXT NOT NULL,
            options TEXT NOT NULL,
            progress REAL DEFAULT 0.0,
            error_message TEXT,
            result_path TEXT,
            expires_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        if conn:
            conn.close()

def save_task(task: Dict[str, Any]):
    """
    Save a task to the database.
    
    Args:
        task: Dictionary containing task information
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert datetime objects to strings
        task_copy = task.copy()
        task_copy['created_at'] = task_copy['created_at'].isoformat()
        task_copy['updated_at'] = task_copy['updated_at'].isoformat()
        task_copy['expires_at'] = task_copy['expires_at'].isoformat()
        
        # Convert options to JSON string
        task_copy['options'] = json.dumps(task_copy['options'])
        
        # Check if task already exists
        cursor.execute("SELECT task_id FROM conversion_tasks WHERE task_id = ?", (task_copy['task_id'],))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing task
            cursor.execute('''
            UPDATE conversion_tasks SET
                status = ?,
                updated_at = ?,
                progress = ?,
                error_message = ?,
                result_path = ?
            WHERE task_id = ?
            ''', (
                task_copy['status'],
                task_copy['updated_at'],
                task_copy['progress'],
                task_copy['error_message'],
                task_copy['result_path'],
                task_copy['task_id']
            ))
        else:
            # Insert new task
            cursor.execute('''
            INSERT INTO conversion_tasks VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ''', (
                task_copy['task_id'],
                task_copy['status'],
                task_copy['created_at'],
                task_copy['updated_at'],
                task_copy['file_name'],
                task_copy['format'],
                task_copy['options'],
                task_copy['progress'],
                task_copy['error_message'],
                task_copy['result_path'],
                task_copy['expires_at']
            ))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving task to database: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a task from the database.
    
    Args:
        task_id: ID of the task to retrieve
        
    Returns:
        Dictionary containing task information or None if not found
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM conversion_tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            # Convert to dictionary
            task = dict(row)
            
            # Parse datetime strings
            task['created_at'] = datetime.fromisoformat(task['created_at'])
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
            task['expires_at'] = datetime.fromisoformat(task['expires_at'])
            
            # Parse options JSON
            task['options'] = json.loads(task['options'])
            
            return task
        
        return None
    except Exception as e:
        logger.error(f"Error getting task from database: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def get_expired_tasks() -> List[Dict[str, Any]]:
    """
    Get tasks that have expired.
    
    Returns:
        List of expired tasks
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("SELECT * FROM conversion_tasks WHERE expires_at < ?", (now,))
        rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            # Convert to dictionary
            task = dict(row)
            
            # Parse datetime strings
            task['created_at'] = datetime.fromisoformat(task['created_at'])
            task['updated_at'] = datetime.fromisoformat(task['updated_at'])
            task['expires_at'] = datetime.fromisoformat(task['expires_at'])
            
            # Parse options JSON
            task['options'] = json.loads(task['options'])
            
            tasks.append(task)
        
        return tasks
    except Exception as e:
        logger.error(f"Error getting expired tasks from database: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def delete_task(task_id: str):
    """
    Delete a task from the database.
    
    Args:
        task_id: ID of the task to delete
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversion_tasks WHERE task_id = ?", (task_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error deleting task from database: {str(e)}")
    finally:
        if conn:
            conn.close()

def update_task_status(task_id: str, status: ConversionStatus, progress: float = None, error_message: str = None, result_path: str = None):
    """
    Update the status of a task.
    
    Args:
        task_id: ID of the task to update
        status: New status of the task
        progress: New progress percentage (optional)
        error_message: Error message (optional)
        result_path: Path to the result file (optional)
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current time
        updated_at = datetime.now().isoformat()
        
        # Prepare update query
        query = "UPDATE conversion_tasks SET status = ?, updated_at = ?"
        params = [status, updated_at]
        
        if progress is not None:
            query += ", progress = ?"
            params.append(progress)
        
        if error_message is not None:
            query += ", error_message = ?"
            params.append(error_message)
        
        if result_path is not None:
            query += ", result_path = ?"
            params.append(result_path)
        
        query += " WHERE task_id = ?"
        params.append(task_id)
        
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}")
    finally:
        if conn:
            conn.close()
