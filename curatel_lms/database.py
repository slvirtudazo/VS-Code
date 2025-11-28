# database.py

import mysql.connector
from mysql.connector import Error

class Database:
    """Database connection manager"""
    
    def __init__(self):
        """Initialize database connection parameters"""
        self.connection = None
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''
        self.database = 'db_library'
        print("[INFO] Database object initialized")
    
    def connect(self):
        """
        Attempt to connect to MySQL database
        Returns: True if successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print("[OK] Database connected successfully")
                return True
            else:
                print("[ERROR] Failed to connect to database")
                return False
                
        except Error as e:
            print(f"[ERROR] Database connection error: {e}")
            self.connection = None
            return False
    
    def execute_query(self, query, params=None):
        """
        Execute INSERT, UPDATE, DELETE queries
        Args:
            query: SQL query string
            params: Tuple of parameters for query
        Returns: True if successful, False otherwise
        """
        if self.connection is None or not self.connection.is_connected():
            print("[ERROR] No database connection")
            return False
            
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            print(f"[OK] Query executed successfully")
            return True
            
        except Error as e:
            print(f"[ERROR] Query execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """
        Fetch all results from SELECT query
        Args:
            query: SQL query string
            params: Tuple of parameters for query
        Returns: List of dictionaries containing results
        """
        if self.connection is None or not self.connection.is_connected():
            print("[ERROR] No database connection")
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            print(f"[OK] Fetched {len(results)} records")
            return results
            
        except Error as e:
            print(f"[ERROR] Fetch error: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """
        Execute query and fetch one result
        Args:
            query: SQL query string
            params: Tuple of parameters for query
        Returns: Dictionary containing result or None
        """
        if self.connection is None or not self.connection.is_connected():
            print("[ERROR] No database connection")
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            return result
            
        except Error as e:
            print(f"[ERROR] Fetch one error: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[INFO] Database connection closed")