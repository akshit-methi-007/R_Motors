"""
Database utility for IVR data management
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional

class IVRDatabase:
    """Handler for IVR SQLite database operations"""
    
    def __init__(self, db_path: str = 'ivr_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # IVR inputs table (raw data from each step)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ivr_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT NOT NULL,
                from_number TEXT,
                to_number TEXT,
                step_name TEXT NOT NULL,
                digit_input TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exophone TEXT,
                caller_circle TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_call_sid ON ivr_inputs(call_sid)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON ivr_inputs(timestamp)
        """)
        
        # IVR paths table (aggregated complete paths)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ivr_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT UNIQUE NOT NULL,
                from_number TEXT,
                to_number TEXT,
                language_choice TEXT,
                state_choice TEXT,
                service_choice TEXT,
                model_choice TEXT,
                hp_choice TEXT,
                complete_path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_paths_call_sid ON ivr_paths(call_sid)
        """)
        
        conn.commit()
        conn.close()
    
    def get_ivr_paths(self, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None) -> pd.DataFrame:
        """Retrieve IVR paths as DataFrame"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM ivr_paths WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_ivr_stats(self) -> dict:
        """Get IVR statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total calls
        cursor.execute("SELECT COUNT(DISTINCT call_sid) FROM ivr_inputs")
        stats['total_calls'] = cursor.fetchone()[0]
        
        # Most common complete paths
        cursor.execute("""
            SELECT complete_path, COUNT(*) as count 
            FROM ivr_paths 
            WHERE complete_path IS NOT NULL AND complete_path != '----'
            GROUP BY complete_path 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats['top_paths'] = cursor.fetchall()
        
        # Language distribution
        cursor.execute("""
            SELECT 
                CASE language_choice
                    WHEN '1' THEN 'Hindi'
                    WHEN '2' THEN 'English'
                    ELSE language_choice
                END as language,
                COUNT(*) as count 
            FROM ivr_paths 
            WHERE language_choice IS NOT NULL 
            GROUP BY language_choice
        """)
        stats['language_distribution'] = cursor.fetchall()
        
        # State distribution
        cursor.execute("""
            SELECT 
                CASE state_choice
                    WHEN '1' THEN 'Rajasthan'
                    WHEN '2' THEN 'Maharashtra'
                    WHEN '3' THEN 'Karnataka'
                    WHEN '4' THEN 'Delhi'
                    ELSE state_choice
                END as state,
                COUNT(*) as count 
            FROM ivr_paths 
            WHERE state_choice IS NOT NULL 
            GROUP BY state_choice
            ORDER BY count DESC
        """)
        stats['state_distribution'] = cursor.fetchall()
        
        # Service distribution
        cursor.execute("""
            SELECT service_choice, COUNT(*) as count 
            FROM ivr_paths 
            WHERE service_choice IS NOT NULL 
            GROUP BY service_choice
            ORDER BY count DESC
        """)
        stats['service_distribution'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    def merge_with_call_data(self, call_df: pd.DataFrame) -> pd.DataFrame:
        """Merge IVR paths with call data"""
        ivr_df = self.get_ivr_paths()
        
        if ivr_df.empty:
            # No IVR data, return call data as-is
            call_df['IVRPath'] = None
            call_df['IVRSelections'] = None
            return call_df
        
        # Merge on CallSid
        merged_df = call_df.merge(
            ivr_df[['call_sid', 'complete_path', 'language_choice', 'state_choice', 
                    'service_choice', 'model_choice', 'hp_choice']],
            left_on='CallSid',
            right_on='call_sid',
            how='left'
        )
        
        # Create IVRPath and IVRSelections columns
        merged_df['IVRPath'] = merged_df['complete_path']
        merged_df['IVRSelections'] = merged_df.apply(
            lambda row: [x for x in [
                row.get('language_choice'),
                row.get('state_choice'),
                row.get('service_choice'),
                row.get('model_choice'),
                row.get('hp_choice')
            ] if pd.notna(x)] if pd.notna(row.get('complete_path')) else None,
            axis=1
        )
        
        # Drop temporary columns
        merged_df = merged_df.drop(columns=['call_sid', 'complete_path', 
                                           'language_choice', 'state_choice',
                                           'service_choice', 'model_choice', 
                                           'hp_choice'], errors='ignore')
        
        return merged_df

if __name__ == '__main__':
    # Test database creation
    db = IVRDatabase()
    print(f"✅ Database initialized: {db.db_path}")
    
    # Test retrieving data
    paths = db.get_ivr_paths()
    print(f"📊 IVR Paths: {len(paths)} records")
    
    stats = db.get_ivr_stats()
    print(f"📈 Stats: {stats}")
