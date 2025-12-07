# curatel_lms/database.py

"""
Database connection and query execution module.
Handles all MySQL database operations with error handling.
"""

import mysql.connector
from mysql.connector import Error

class Database:
    """Manages MySQL database connections and operations."""
    
    def __init__(self):
        """Initialize database parameters."""
        self.connection = None
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''
        self.database = 'db_library'
        print("[INFO] Database initialized")
    
    def connect(self):
        """
        Establish database connection.
        Returns: True if successful, False otherwise.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print("[OK] Connected to database")
                return True
            
            print("[ERROR] Connection failed")
            return False
                
        except Error as e:
            print(f"[ERROR] Connection error: {e}")
            self.connection = None
            return False
    
    def execute_query(self, query, params=None):
        """
        Execute INSERT, UPDATE, DELETE queries.
        Args:
            query: SQL query string
            params: Query parameters tuple
        Returns: True if successful, False otherwise.
        """
        if not self._is_connected():
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            self.connection.commit()
            cursor.close()
            print("[OK] Query executed")
            return True
            
        except Error as e:
            print(f"[ERROR] Query failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """
        Fetch all records from SELECT query.
        Args:
            query: SQL query string
            params: Query parameters tuple
        Returns: List of dictionaries containing results.
        """
        if not self._is_connected():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params) if params else cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            print(f"[OK] Fetched {len(results)} records")
            return results
            
        except Error as e:
            print(f"[ERROR] Fetch failed: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """
        Fetch single record from SELECT query.
        Args:
            query: SQL query string
            params: Query parameters tuple
        Returns: Dictionary containing result or None.
        """
        if not self._is_connected():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params) if params else cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
            
        except Error as e:
            print(f"[ERROR] Fetch one failed: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[INFO] Connection closed")
    
    def _is_connected(self):
        """Check if database is connected."""
        if not self.connection or not self.connection.is_connected():
            print("[ERROR] No database connection")
            return False
        return True