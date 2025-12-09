# curatel_lms/database.py

"""
Database management module.
Handles all MySQL database connections and CRUD operations with comprehensive error handling.
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple, Any

class Database:
    """
    MySQL database connection manager.
    Provides methods for executing queries and fetching results safely.
    """
    
    def __init__(self, host: str = 'localhost', user: str = 'root', 
                 password: str = '', database: str = 'db_library'):
        """
        Initialize database connection parameters.
        
        Args:
            host: Database server hostname
            user: Database username
            password: Database password
            database: Database name
        """
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        print(f"[INFO] Database initialized: {database}")
    
    def connect(self) -> bool:
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print(f"[OK] Connected to database: {self.database}")
                return True
            
            print("[ERROR] Connection failed")
            return False
                
        except Error as e:
            print(f"[ERROR] Connection error: {e}")
            self.connection = None
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Optional tuple of query parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._is_connected():
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # Execute with or without parameters
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            print(f"[OK] Query executed: {cursor.rowcount} rows affected")
            return True
            
        except Error as e:
            print(f"[ERROR] Query execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Fetch all records from SELECT query.
        
        Args:
            query: SQL SELECT query string
            params: Optional tuple of query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        if not self._is_connected():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Execute with or without parameters
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            print(f"[OK] Fetched {len(results)} records")
            return results
            
        except Error as e:
            print(f"[ERROR] Fetch all failed: {e}")
            return []
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch single record from SELECT query.
        
        Args:
            query: SQL SELECT query string
            params: Optional tuple of query parameters
            
        Returns:
            Dictionary containing single result or None if not found
        """
        if not self._is_connected():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Execute with or without parameters
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print("[OK] Record fetched successfully")
            else:
                print("[INFO] No record found")
            
            return result
            
        except Error as e:
            print(f"[ERROR] Fetch one failed: {e}")
            return None
    
    def close(self) -> None:
        """Close database connection if open."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[INFO] Database connection closed")
    
    def _is_connected(self) -> bool:
        """
        Check if database connection is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            print("[ERROR] No active database connection")
            return False
        return True
    
    def __enter__(self):
        """Context manager entry - establishes connection."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes connection."""
        self.close()