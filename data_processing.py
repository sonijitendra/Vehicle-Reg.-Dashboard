"""
Data processing module for calculating YoY and QoQ growth metrics with SQL integration
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from database import VehicleDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleDataProcessor:
    """Class to handle vehicle registration data processing and analysis"""
    
    def __init__(self, data_path="data/vahan_vehicle_data.csv", use_database=True):
        self.data_path = data_path
        self.df = None
        self.processed_df = None
        self.use_database = use_database
        if self.use_database:
            self.db = VehicleDatabase()
        else:
            self.db = None
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            self.df = pd.read_csv(self.data_path)
            self.df['date'] = pd.to_datetime(self.df['date'])
            logger.info(f"Loaded {len(self.df)} records from {self.data_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def calculate_yoy_growth(self):
        """Calculate Year-over-Year growth for each manufacturer and category"""
        if self.df is None:
            logger.error("No data loaded. Call load_data() first.")
            return None
        
        # Group by manufacturer, category, year, quarter
        grouped = self.df.groupby(['manufacturer', 'vehicle_category', 'year', 'quarter'])['registrations'].sum().reset_index()
        
        # Calculate YoY growth
        grouped['prev_year'] = grouped['year'] - 1
        
        # Merge with previous year data
        yoy_data = grouped.merge(
            grouped[['manufacturer', 'vehicle_category', 'year', 'quarter', 'registrations']], 
            left_on=['manufacturer', 'vehicle_category', 'prev_year', 'quarter'],
            right_on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
            how='left',
            suffixes=('', '_prev_year')
        )
        
        # Calculate YoY percentage change
        yoy_data['yoy_growth'] = ((yoy_data['registrations'] - yoy_data['registrations_prev_year']) / 
                                 yoy_data['registrations_prev_year'] * 100).round(2)
        
        # Clean up columns
        yoy_data = yoy_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'registrations', 'yoy_growth']]
        
        return yoy_data
    
    def calculate_qoq_growth(self):
        """Calculate Quarter-over-Quarter growth for each manufacturer and category"""
        if self.df is None:
            logger.error("No data loaded. Call load_data() first.")
            return None
        
        # Group by manufacturer, category, year, quarter
        grouped = self.df.groupby(['manufacturer', 'vehicle_category', 'year', 'quarter'])['registrations'].sum().reset_index()
        
        # Sort by manufacturer, category, year, quarter
        grouped = grouped.sort_values(['manufacturer', 'vehicle_category', 'year', 'quarter'])
        
        # Calculate previous quarter values
        grouped['prev_quarter'] = grouped['quarter'] - 1
        grouped['prev_year_adj'] = grouped['year']
        
        # Handle Q1 (previous quarter is Q4 of previous year)
        mask_q1 = grouped['quarter'] == 1
        grouped.loc[mask_q1, 'prev_quarter'] = 4
        grouped.loc[mask_q1, 'prev_year_adj'] = grouped.loc[mask_q1, 'year'] - 1
        
        # Merge with previous quarter data
        qoq_data = grouped.merge(
            grouped[['manufacturer', 'vehicle_category', 'year', 'quarter', 'registrations']], 
            left_on=['manufacturer', 'vehicle_category', 'prev_year_adj', 'prev_quarter'],
            right_on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
            how='left',
            suffixes=('', '_prev_quarter')
        )
        
        # Calculate QoQ percentage change
        qoq_data['qoq_growth'] = ((qoq_data['registrations'] - qoq_data['registrations_prev_quarter']) / 
                                 qoq_data['registrations_prev_quarter'] * 100).round(2)
        
        # Clean up columns
        qoq_data = qoq_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'registrations', 'qoq_growth']]
        
        return qoq_data
    
    def calculate_category_totals(self):
        """Calculate total registrations by vehicle category"""
        if self.df is None:
            logger.error("No data loaded. Call load_data() first.")
            return None
        
        # Group by category, year, quarter
        category_totals = self.df.groupby(['vehicle_category', 'year', 'quarter'])['registrations'].sum().reset_index()
        
        return category_totals
    
    def get_top_performers(self, metric='registrations', n=5):
        """Get top performing manufacturers by specified metric"""
        if self.df is None:
            logger.error("No data loaded. Call load_data() first.")
            return None
        
        # Get latest period data
        latest_year = self.df['year'].max()
        latest_quarter = self.df[self.df['year'] == latest_year]['quarter'].max()
        
        latest_data = self.df[(self.df['year'] == latest_year) & (self.df['quarter'] == latest_quarter)]
        
        # Group by manufacturer and sum registrations
        top_performers = latest_data.groupby('manufacturer')['registrations'].sum().reset_index()
        top_performers = top_performers.sort_values('registrations', ascending=False).head(n)
        
        return top_performers
    
    def generate_insights(self, df=None):
        """Generate dynamic key investor insights from the (optionally filtered) data"""
        insights = []
        
        # Choose the working dataframe
        local_df = df if df is not None else getattr(self, 'df', None)
        if local_df is None or (hasattr(local_df, 'empty') and local_df.empty):
            return ["No data available for analysis."]
        
        try:
            # Compute YoY and QoQ on the working set
            # Expect columns: date or year/month, category, manufacturer, registrations
            working = local_df.copy()
            # Normalize period column if present
            if 'date' in working.columns:
                working['year'] = pd.to_datetime(working['date']).dt.year
                working['quarter'] = pd.to_datetime(working['date']).dt.to_period('Q').astype(str)
            elif 'year' in working.columns and 'quarter' in working.columns:
                working['quarter'] = working['year'].astype(str) + ' Q' + working['quarter'].astype(str)
            elif 'year_quarter' in working.columns:
                working[['year','quarter_num']] = working['year_quarter'].str.extract(r'(\d{4})-?Q?(\d)')
                working['year'] = working['year'].astype(int, errors='ignore')
                working['quarter'] = working['year'].astype(str) + ' Q' + working['quarter_num']
            
            # Aggregate at manufacturer level if present, else category
            level = 'manufacturer' if 'manufacturer' in working.columns else ('category' if 'category' in working.columns else None)
            if level:
                agg = working.groupby([level, 'year'], dropna=False)['registrations'].sum().reset_index()
                # Compute YoY %
                agg = agg.sort_values(['%s' % level, 'year'])
                agg['yoy_growth'] = agg.groupby(level)['registrations'].pct_change() * 100.0
                # Latest period
                latest_year = agg['year'].max()
                latest_slice = agg[agg['year'] == latest_year]
                
                # Top growers (YoY)
                top_yoy = latest_slice.sort_values('yoy_growth', ascending=False).dropna(subset=['yoy_growth']).head(3)
                if not top_yoy.empty:
                    names = ", ".join([f"{row[level]} ({row['yoy_growth']:.1f}%)" for _, row in top_yoy.iterrows()])
                    insights.append(f"Top YoY growers in {latest_year}: {names}.")
                
                # Market concentration (Herfindahl-lite using share^2)
                total_latest = latest_slice['registrations'].sum()
                latest_slice = latest_slice.assign(share=lambda d: d['registrations'] / total_latest if total_latest else 0)
                hhi_like = (latest_slice['share'] ** 2).sum()
                if hhi_like >= 0.20:
                    insights.append("Market looks concentrated in the latest year (high concentration index).")
                else:
                    insights.append("Market looks relatively competitive in the latest year (low concentration index).")
            
            # Overall trend (total registrations)
            by_year = working.groupby('year', dropna=False)['registrations'].sum().reset_index().sort_values('year')
            if len(by_year) >= 2:
                prev = by_year['registrations'].iloc[-2]
                curr = by_year['registrations'].iloc[-1]
                denom = prev if prev != 0 else 1
                overall_yoy = (curr - prev) / denom * 100.0
                insights.append(f"Overall YoY change latest year: {overall_yoy:.1f}%.")
            
            # Risk/volatility signal
            if 'quarter' in working.columns:
                by_q = working.groupby('quarter', dropna=False)['registrations'].sum().reset_index()
                if len(by_q) >= 4:
                    vol = by_q['registrations'].pct_change().abs().dropna().mean() * 100.0
                    if vol > 20:
                        insights.append("Quarterly growth is volatile (>20% avg absolute change). Consider risk in short-term projections.")
                    else:
                        insights.append("Quarterly growth is relatively stable (<20% avg absolute change).")
            
            # Ensure at least a couple of insights
            if not insights:
                insights.append("Growth is steady with no standout outliers in the selected view.")
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return ["Could not generate insights for the current selection."]

    
    def process_all_data(self):
        """Process all data and return comprehensive dataset with SQL integration"""
        if not self.load_data():
            return None
        
        if self.use_database and self.db:
            # Store data in database
            self.db.insert_registration_data(self.df)
            
            # Calculate growth metrics using SQL
            yoy_data = self.db.get_yoy_growth_data()
            qoq_data = self.db.get_qoq_growth_data()
            
            # Store growth metrics in database
            if not yoy_data.empty and not qoq_data.empty:
                # Merge YoY and QoQ data
                growth_metrics = pd.merge(
                    yoy_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'registrations', 'yoy_growth']],
                    qoq_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'qoq_growth']],
                    on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
                    how='outer'
                )
                self.db.insert_growth_metrics(growth_metrics)
            
            # Merge all data for return
            processed = self.df.copy()
            
            if not yoy_data.empty:
                processed = pd.merge(
                    processed,
                    yoy_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'yoy_growth']],
                    on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
                    how='left'
                )
            
            if not qoq_data.empty:
                processed = pd.merge(
                    processed,
                    qoq_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'qoq_growth']],
                    on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
                    how='left'
                )
        else:
            # Fallback to in-memory processing
            yoy_data = self.calculate_yoy_growth()
            qoq_data = self.calculate_qoq_growth()
            
            # Merge all data
            processed = self.df.copy()
            
            if yoy_data is not None and not yoy_data.empty:
                processed = pd.merge(
                    processed,
                    yoy_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'yoy_growth']],
                    on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
                    how='left'
                )
            
            if qoq_data is not None and not qoq_data.empty:
                processed = pd.merge(
                    processed,
                    qoq_data[['manufacturer', 'vehicle_category', 'year', 'quarter', 'qoq_growth']],
                    on=['manufacturer', 'vehicle_category', 'year', 'quarter'],
                    how='left'
                )
        
        self.processed_df = processed
        return processed

def main():
    """Main function for standalone execution"""
    processor = VehicleDataProcessor()
    processed_data = processor.process_all_data()
    
    if processed_data is not None:
        print(f"Processed {len(processed_data)} records")
        print("\nSample insights:")
        insights = processor.generate_insights()
        for insight in insights:
            print(f"- {insight}")
    else:
        print("Failed to process data")

if __name__ == "__main__":
    main()
