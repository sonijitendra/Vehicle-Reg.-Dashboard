"""
Database module for SQLite integration and data storage
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleDatabase:
    """Class to handle SQLite database operations for vehicle registration data"""
    
    def __init__(self, db_path="data/vehicle_registrations.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create main registration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    quarter INTEGER NOT NULL,
                    vehicle_category TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    registrations INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create growth metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS growth_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manufacturer TEXT NOT NULL,
                    vehicle_category TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    quarter INTEGER NOT NULL,
                    registrations INTEGER,
                    yoy_growth REAL,
                    qoq_growth REAL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_registration_date 
                ON vehicle_registrations(year, quarter)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_registration_manufacturer 
                ON vehicle_registrations(manufacturer)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_registration_category 
                ON vehicle_registrations(vehicle_category)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_registration_data(self, df):
        """Insert registration data from DataFrame"""
        try:
            with self.get_connection() as conn:
                # Clear existing data
                conn.execute("DELETE FROM vehicle_registrations")
                
                # Insert new data
                df.to_sql('vehicle_registrations', conn, if_exists='append', index=False)
                
                rows_inserted = len(df)
                logger.info(f"Inserted {rows_inserted} registration records")
                return rows_inserted
                
        except Exception as e:
            logger.error(f"Error inserting registration data: {str(e)}")
            return 0
    
    def insert_growth_metrics(self, df):
        """Insert growth metrics from DataFrame"""
        try:
            with self.get_connection() as conn:
                # Clear existing data
                conn.execute("DELETE FROM growth_metrics")
                
                # Insert new data
                df.to_sql('growth_metrics', conn, if_exists='append', index=False)
                
                rows_inserted = len(df)
                logger.info(f"Inserted {rows_inserted} growth metric records")
                return rows_inserted
                
        except Exception as e:
            logger.error(f"Error inserting growth metrics: {str(e)}")
            return 0
    
    def get_vehicle_counts_by_category(self, start_year=None, end_year=None):
        """Get vehicle counts by category using SQL"""
        query = '''
            SELECT 
                vehicle_category,
                SUM(registrations) as registrations,
                COUNT(DISTINCT manufacturer) as manufacturer_count
            FROM vehicle_registrations
        '''
        
        params = []
        if start_year and end_year:
            query += " WHERE year BETWEEN ? AND ?"
            params = [start_year, end_year]
        
        query += " GROUP BY vehicle_category ORDER BY registrations DESC"
        
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            logger.error(f"Error getting vehicle counts by category: {str(e)}")
            return pd.DataFrame()
    
    def get_manufacturer_wise_counts(self, start_year=None, end_year=None):
        """Get manufacturer-wise counts using SQL"""
        query = '''
            SELECT 
                manufacturer,
                vehicle_category,
                SUM(registrations) as registrations,
                AVG(registrations) as avg_registrations
            FROM vehicle_registrations
        '''
        
        params = []
        if start_year and end_year:
            query += " WHERE year BETWEEN ? AND ?"
            params = [start_year, end_year]
        
        query += " GROUP BY manufacturer, vehicle_category ORDER BY registrations DESC"
        
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            logger.error(f"Error getting manufacturer counts: {str(e)}")
            return pd.DataFrame()
    
    def get_yoy_growth_data(self):
        """Get YoY growth data using SQL"""
        query = '''
            WITH yearly_data AS (
                SELECT 
                    manufacturer,
                    vehicle_category,
                    year,
                    quarter,
                    SUM(registrations) as registrations
                FROM vehicle_registrations
                GROUP BY manufacturer, vehicle_category, year, quarter
            ),
            yoy_calculations AS (
                SELECT 
                    current.manufacturer,
                    current.vehicle_category,
                    current.year,
                    current.quarter,
                    current.registrations,
                    previous.registrations as prev_year_registrations,
                    CASE 
                        WHEN previous.registrations > 0 THEN
                            ROUND(((current.registrations - previous.registrations) * 100.0 / previous.registrations), 2)
                        ELSE NULL
                    END as yoy_growth
                FROM yearly_data current
                LEFT JOIN yearly_data previous ON 
                    current.manufacturer = previous.manufacturer 
                    AND current.vehicle_category = previous.vehicle_category
                    AND current.year = previous.year + 1
                    AND current.quarter = previous.quarter
            )
            SELECT * FROM yoy_calculations
            WHERE yoy_growth IS NOT NULL
            ORDER BY year DESC, quarter DESC, yoy_growth DESC
        '''
        
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting YoY growth data: {str(e)}")
            return pd.DataFrame()
    
    def get_qoq_growth_data(self):
        """Get QoQ growth data using SQL"""
        query = '''
            WITH quarterly_data AS (
                SELECT 
                    manufacturer,
                    vehicle_category,
                    year,
                    quarter,
                    SUM(registrations) as registrations
                FROM vehicle_registrations
                GROUP BY manufacturer, vehicle_category, year, quarter
            ),
            qoq_calculations AS (
                SELECT 
                    current.manufacturer,
                    current.vehicle_category,
                    current.year,
                    current.quarter,
                    current.registrations,
                    previous.registrations as prev_quarter_registrations,
                    CASE 
                        WHEN previous.registrations > 0 THEN
                            ROUND(((current.registrations - previous.registrations) * 100.0 / previous.registrations), 2)
                        ELSE NULL
                    END as qoq_growth
                FROM quarterly_data current
                LEFT JOIN quarterly_data previous ON 
                    current.manufacturer = previous.manufacturer 
                    AND current.vehicle_category = previous.vehicle_category
                    AND (
                        (current.year = previous.year AND current.quarter = previous.quarter + 1) OR
                        (current.year = previous.year + 1 AND current.quarter = 1 AND previous.quarter = 4)
                    )
            )
            SELECT * FROM qoq_calculations
            WHERE qoq_growth IS NOT NULL
            ORDER BY year DESC, quarter DESC, qoq_growth DESC
        '''
        
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting QoQ growth data: {str(e)}")
            return pd.DataFrame()
    
    def get_top_performers(self, metric='registrations', limit=10):
        """Get top performing manufacturers by specified metric"""
        if metric == 'yoy_growth':
            query = '''
                SELECT 
                    manufacturer,
                    vehicle_category,
                    AVG(yoy_growth) as avg_yoy_growth,
                    MAX(yoy_growth) as max_yoy_growth
                FROM growth_metrics
                WHERE yoy_growth IS NOT NULL
                GROUP BY manufacturer, vehicle_category
                ORDER BY avg_yoy_growth DESC
                LIMIT ?
            '''
        elif metric == 'qoq_growth':
            query = '''
                SELECT 
                    manufacturer,
                    vehicle_category,
                    AVG(qoq_growth) as avg_qoq_growth,
                    MAX(qoq_growth) as max_qoq_growth
                FROM growth_metrics
                WHERE qoq_growth IS NOT NULL
                GROUP BY manufacturer, vehicle_category
                ORDER BY avg_qoq_growth DESC
                LIMIT ?
            '''
        else:  # registrations
            query = '''
                SELECT 
                    manufacturer,
                    SUM(registrations) as registrations,
                    COUNT(DISTINCT vehicle_category) as categories_served
                FROM vehicle_registrations
                GROUP BY manufacturer
                ORDER BY registrations DESC
                LIMIT ?
            '''
        
        try:
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn, params=[limit])
        except Exception as e:
            logger.error(f"Error getting top performers: {str(e)}")
            return pd.DataFrame()
    
    def get_summary_statistics(self):
        """Get summary statistics using SQL"""
        query = '''
            SELECT 
                COUNT(*) as total_records,
                SUM(registrations) as registrations,
                COUNT(DISTINCT manufacturer) as unique_manufacturers,
                COUNT(DISTINCT vehicle_category) as unique_categories,
                MIN(year) as earliest_year,
                MAX(year) as latest_year
            FROM vehicle_registrations
        '''
        
        try:
            with self.get_connection() as conn:
                result = pd.read_sql_query(query, conn)
                return result.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error getting summary statistics: {str(e)}")
            return {}
    
    def export_to_csv(self, table_name, output_path):
        """Export table data to CSV"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                df.to_csv(output_path, index=False)
                logger.info(f"Exported {table_name} to {output_path}")
                return True
        except Exception as e:
            logger.error(f"Error exporting {table_name}: {str(e)}")
            return False

def main():
    """Main function for standalone testing"""
    db = VehicleDatabase()
    
    # Load sample data if exists
    if os.path.exists("data/vahan_vehicle_data.csv"):
        df = pd.read_csv("data/vahan_vehicle_data.csv")
        db.insert_registration_data(df)
        
        # Get some statistics
        stats = db.get_summary_statistics()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test queries
        print("\nTop 5 manufacturers by total registrations:")
        top_manufacturers = db.get_top_performers(limit=5)
        print(top_manufacturers)
    else:
        print("No sample data found. Run data_collection.py first.")

if __name__ == "__main__":
    main()