"""
Database Manager for Hot Parts System
Handles all SQLite database operations for hot parts and excess inventory data.
"""

import sqlite3
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the Hot Parts system."""
    
    def __init__(self, db_path: str = "hotparts.db"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Read and execute schema
                schema_path = "database_schema.sql"
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        schema = f.read()
                    conn.executescript(schema)
                    logger.info(f"Database initialized: {self.db_path}")
                else:
                    logger.warning(f"Schema file not found: {schema_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_connection(self):
        """Get database connection with proper configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def insert_hot_parts(self, data: List[Dict]) -> int:
        """Insert hot parts data into database.
        
        Args:
            data: List of dictionaries containing hot parts data
            
        Returns:
            Number of records inserted
        """
        if not data:
            return 0
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                inserted = 0
                skipped = 0
                
                for record in data:
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO hot_parts 
                            (mpn, date, reqs_count, manufacturer, product_class, description, source_file)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            record.get('MPN', ''),
                            record.get('Date', ''),
                            record.get('Reqs_Count', 0),
                            record.get('Manufacturer', ''),
                            record.get('Product_Class', ''),
                            record.get('Description', ''),
                            record.get('source_file', '')
                        ))
                        
                        if cursor.rowcount > 0:
                            inserted += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        logger.error(f"Error inserting hot parts record: {e}")
                        skipped += 1
                
                conn.commit()
                logger.info(f"Hot parts: {inserted} inserted, {skipped} skipped")
                return inserted
                
        except Exception as e:
            logger.error(f"Failed to insert hot parts data: {e}")
            raise
    
    def insert_excess_inventory(self, data: List[Dict]) -> int:
        """Insert excess inventory data into database.
        
        Args:
            data: List of dictionaries containing excess inventory data
            
        Returns:
            Number of records inserted
        """
        if not data:
            return 0
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                inserted = 0
                skipped = 0
                
                for record in data:
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO excess_inventory 
                            (mpn, excess_filename, excess_qty, target_price, manufacturer, sheet_name)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            record.get('MPN', ''),
                            record.get('Excess_Filename', ''),
                            record.get('Excess_QTY', 0),
                            record.get('Target_Price'),
                            record.get('Manufacturer', ''),
                            record.get('sheet_name', '')
                        ))
                        
                        if cursor.rowcount > 0:
                            inserted += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        logger.error(f"Error inserting excess record: {e}")
                        skipped += 1
                
                conn.commit()
                logger.info(f"Excess inventory: {inserted} inserted, {skipped} skipped")
                return inserted
                
        except Exception as e:
            logger.error(f"Failed to insert excess inventory data: {e}")
            raise
    
    def insert_matches(self, data: List[Dict]) -> int:
        """Insert match data into database.
        
        Args:
            data: List of dictionaries containing match data
            
        Returns:
            Number of records inserted
        """
        if not data:
            return 0
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                inserted = 0
                skipped = 0
                
                for record in data:
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO matches 
                            (mpn, hot_parts_date, reqs_count, manufacturer, product_class, 
                             description, excess_filename, excess_qty, target_price)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            record.get('MPN', ''),
                            record.get('Weekly_Hot_Parts_Date', ''),
                            record.get('Reqs_Count', 0),
                            record.get('Manufacturer', ''),
                            record.get('Product_Class', ''),
                            record.get('Description', ''),
                            record.get('Excess_Filename', ''),
                            record.get('Excess_QTY', 0),
                            record.get('Target_Price')
                        ))
                        
                        if cursor.rowcount > 0:
                            inserted += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        logger.error(f"Error inserting match record: {e}")
                        skipped += 1
                
                conn.commit()
                logger.info(f"Matches: {inserted} inserted, {skipped} skipped")
                return inserted
                
        except Exception as e:
            logger.error(f"Failed to insert match data: {e}")
            raise
    
    def log_processing(self, filename: str, file_type: str, status: str, 
                      records_processed: int = 0, records_added: int = 0, 
                      records_skipped: int = 0, error_message: str = None):
        """Log file processing results.
        
        Args:
            filename: Name of processed file
            file_type: Type of file ('hot_parts' or 'excess')
            status: Processing status ('success', 'error', 'duplicate')
            records_processed: Number of records processed
            records_added: Number of records added
            records_skipped: Number of records skipped
            error_message: Error message if any
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processing_log 
                    (filename, file_type, status, records_processed, records_added, 
                     records_skipped, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (filename, file_type, status, records_processed, 
                     records_added, records_skipped, error_message))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log processing: {e}")
    
    def get_random_parts(self, count: int = 10, min_price: float = 10.0, 
                        max_manufacturers: int = 5) -> List[Dict]:
        """Get random parts matching criteria.
        
        Args:
            count: Number of parts to return
            min_price: Minimum target price
            max_manufacturers: Maximum number of manufacturers
            
        Returns:
            List of dictionaries containing part data
        """
        try:
            with self.get_connection() as conn:
                query = """
                    WITH ranked_parts AS (
                        SELECT 
                            mpn,
                            manufacturer,
                            target_price,
                            excess_qty,
                            hot_parts_date,
                            reqs_count,
                            product_class,
                            description,
                            excess_filename,
                            ROW_NUMBER() OVER (
                                PARTITION BY manufacturer 
                                ORDER BY RANDOM()
                            ) as rn
                        FROM matches 
                        WHERE target_price > ?
                        AND manufacturer IN (
                            SELECT DISTINCT manufacturer 
                            FROM matches 
                            WHERE target_price > ?
                            ORDER BY RANDOM() 
                            LIMIT ?
                        )
                    )
                    SELECT 
                        mpn, manufacturer, target_price, excess_qty,
                        hot_parts_date, reqs_count, product_class, 
                        description, excess_filename
                    FROM ranked_parts 
                    WHERE rn <= 2  -- 2 parts per manufacturer max
                    ORDER BY RANDOM()
                    LIMIT ?
                """
                
                cursor = conn.cursor()
                cursor.execute(query, (min_price, min_price, max_manufacturers, count))
                
                results = []
                for row in cursor.fetchall():
                    results.append(dict(row))
                
                logger.info(f"Retrieved {len(results)} random parts")
                return results
                
        except Exception as e:
            logger.error(f"Failed to get random parts: {e}")
            return []
    
    def get_hot_parts_summary(self) -> pd.DataFrame:
        """Get summary of hot parts data.
        
        Returns:
            DataFrame with hot parts summary
        """
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM v_hot_parts_summary ORDER BY total_occurrences DESC"
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Failed to get hot parts summary: {e}")
            return pd.DataFrame()
    
    def get_excess_summary(self) -> pd.DataFrame:
        """Get summary of excess inventory data.
        
        Returns:
            DataFrame with excess inventory summary
        """
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM v_excess_summary ORDER BY total_available_qty DESC"
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Failed to get excess summary: {e}")
            return pd.DataFrame()
    
    def get_matches_summary(self) -> pd.DataFrame:
        """Get summary of matches data.
        
        Returns:
            DataFrame with matches summary
        """
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM v_matches_summary ORDER BY total_matches DESC"
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Failed to get matches summary: {e}")
            return pd.DataFrame()
    
    def export_to_excel(self, output_dir: str = "."):
        """Export database data to Excel files for compatibility.
        
        Args:
            output_dir: Directory to save Excel files
        """
        try:
            # Export hot parts data
            hot_parts_df = pd.read_sql_query(
                "SELECT mpn, date, reqs_count, manufacturer, product_class, description FROM hot_parts ORDER BY date DESC, mpn",
                self.get_connection()
            )
            hot_parts_df.to_excel(f"{output_dir}/Master_Hot_Parts_Data.xlsx", index=False)
            
            # Export matches data
            matches_df = pd.read_sql_query(
                """SELECT mpn, hot_parts_date, reqs_count, manufacturer, product_class, 
                          description, excess_filename, excess_qty, target_price 
                   FROM matches ORDER BY created_at DESC""",
                self.get_connection()
            )
            matches_df.to_excel(f"{output_dir}/Master_Matches_Data.xlsx", index=False)
            
            logger.info(f"Exported data to Excel files in {output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                for table in ['hot_parts', 'excess_inventory', 'matches', 'processing_log']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Get unique MPNs
                cursor.execute("SELECT COUNT(DISTINCT mpn) FROM hot_parts")
                stats['unique_hot_parts_mpns'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT mpn) FROM excess_inventory")
                stats['unique_excess_mpns'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT mpn) FROM matches")
                stats['unique_match_mpns'] = cursor.fetchone()[0]
                
                # Get date range
                cursor.execute("SELECT MIN(date), MAX(date) FROM hot_parts")
                date_range = cursor.fetchone()
                stats['hot_parts_date_range'] = f"{date_range[0]} to {date_range[1]}" if date_range[0] else "No data"
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {} 