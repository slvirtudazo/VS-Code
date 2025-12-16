# curatel_lms/database.py

# Manages MySQL connections and performs create, read, update, and delete operations with error handling

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple, Any

class Database:
    # MySQL connection manager: safely executes queries and fetches results.
    
    def __init__(self, host: str = 'localhost', user: str = 'root', 
                 password: str = '', database: str = 'db_library'):
        # Set connection parameters and log init
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        print(f"[INFO] Database initialized: {database}")
    
    def connect(self) -> bool:
        # Connect to MySQL; return True on success.
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
        # Run INSERT/UPDATE/DELETE; return success status.
        if not self._is_connected():
            return False
            
        try:
            cursor = self.connection.cursor()
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
        # Run SELECT; return all results as list of dicts.
        if not self._is_connected():
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
            print(f"[ERROR] Fetch all failed: {e}")
            return []
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        # Run SELECT; return one result as dict or None.
        if not self._is_connected():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
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
        # Close connection if open.
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[INFO] Database connection closed")
    
    def _is_connected(self) -> bool:
        # Check if connection is active.
        if not self.connection or not self.connection.is_connected():
            print("[ERROR] No active database connection")
            return False
        return True
    
    def __enter__(self):
        # Context entry: connect.
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context exit: close connection.
        self.close()