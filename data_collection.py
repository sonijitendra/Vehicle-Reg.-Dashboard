"""
Data collection module for fetching vehicle registration data from Vahan Dashboard
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime, timedelta
import time
import logging
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleDataCollector:
    """Class to handle vehicle registration data collection"""
    
    def __init__(self):
        self.base_url = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_vahan_data(self, start_date=None, end_date=None):
        """
        Fetch data from Vahan dashboard using web scraping
        Falls back to sample data if scraping fails
        """
        logger.info("Starting data collection from Vahan dashboard...")
        
        try:
            # Try to scrape real data first
            scraped_data = self.scrape_vahan_website()
            if scraped_data is not None and not scraped_data.empty:
                logger.info("Successfully scraped data from Vahan website")
                return scraped_data
            else:
                logger.warning("Web scraping failed or returned empty data. Using enhanced sample data.")
                return self.generate_sample_data()
                
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            logger.warning("Falling back to sample data generation.")
            return self.generate_sample_data()
    
    def scrape_vahan_website(self):
        """
        Attempt to scrape data from the Vahan website
        This is a placeholder implementation due to CAPTCHA and security restrictions
        """
        try:
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Try to access the Vahan dashboard
            response = requests.get(self.base_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for data tables or relevant content
                # Note: The actual implementation would need to handle JavaScript rendering,
                # CAPTCHA challenges, and dynamic content loading
                
                # For demonstration, we'll parse any tables found
                tables = soup.find_all('table')
                if tables:
                    logger.info(f"Found {len(tables)} tables on the page")
                    # Parse table data here
                    # This would need to be customized based on actual website structure
                    return self.parse_vahan_tables(tables)
                else:
                    logger.warning("No data tables found on the page")
                    return None
            else:
                logger.warning(f"Failed to access website. Status code: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error while scraping: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error during web scraping: {str(e)}")
            return None
    
    def parse_vahan_tables(self, tables):
        """
        Parse HTML tables from Vahan website
        This would need to be customized based on actual table structure
        """
        try:
            data = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # Ensure we have enough columns
                        # Extract data based on expected format
                        # This is a placeholder structure
                        row_data = {
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'year': datetime.now().year,
                            'quarter': (datetime.now().month - 1) // 3 + 1,
                            'vehicle_category': 'Unknown',
                            'manufacturer': 'Unknown',
                            'registrations': 0
                        }
                        data.append(row_data)
            
            if data:
                return pd.DataFrame(data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error parsing tables: {str(e)}")
            return None
    
    def scrape_with_selenium(self):
        """
        Alternative scraping method using Selenium for JavaScript-heavy pages
        Note: Requires ChromeDriver installation
        """
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # Note: This would require ChromeDriver to be installed
            # driver = webdriver.Chrome(options=chrome_options)
            # driver.get(self.base_url)
            
            # Wait for page to load and handle dynamic content
            # wait = WebDriverWait(driver, 10)
            # elements = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Extract data from the page
            # page_source = driver.page_source
            # soup = BeautifulSoup(page_source, 'html.parser')
            
            # driver.quit()
            
            logger.warning("Selenium scraping not implemented - requires ChromeDriver setup")
            return None
            
        except Exception as e:
            logger.error(f"Error in Selenium scraping: {str(e)}")
            return None
    
    def generate_sample_data(self):
        """
        Generate realistic sample data for testing
        This simulates the structure of actual Vahan data
        """
        import numpy as np
        from datetime import datetime, timedelta
        
        # Define base data structure
        manufacturers_2w = ['Hero MotoCorp', 'Honda', 'TVS Motor', 'Bajaj Auto', 'Royal Enfield']
        manufacturers_3w = ['Bajaj Auto', 'Mahindra', 'Piaggio', 'Force Motors', 'Atul Auto']
        manufacturers_4w = ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Honda Cars']
        
        data = []
        
        # Generate data for the last 3 years, quarterly
        base_date = datetime(2022, 1, 1)
        
        for year in range(2022, 2025):
            for quarter in range(1, 5):
                quarter_start = datetime(year, (quarter-1)*3 + 1, 1)
                
                # Generate 2-Wheeler data
                for manufacturer in manufacturers_2w:
                    base_registrations = np.random.randint(15000, 50000)
                    # Add growth trends
                    growth_factor = 1 + (year - 2022) * 0.1 + np.random.uniform(-0.15, 0.25)
                    registrations = int(base_registrations * growth_factor)
                    
                    data.append({
                        'date': quarter_start.strftime('%Y-%m-%d'),
                        'year': year,
                        'quarter': quarter,
                        'vehicle_category': '2W',
                        'manufacturer': manufacturer,
                        'registrations': registrations
                    })
                
                # Generate 3-Wheeler data
                for manufacturer in manufacturers_3w:
                    base_registrations = np.random.randint(2000, 8000)
                    growth_factor = 1 + (year - 2022) * 0.08 + np.random.uniform(-0.2, 0.3)
                    registrations = int(base_registrations * growth_factor)
                    
                    data.append({
                        'date': quarter_start.strftime('%Y-%m-%d'),
                        'year': year,
                        'quarter': quarter,
                        'vehicle_category': '3W',
                        'manufacturer': manufacturer,
                        'registrations': registrations
                    })
                
                # Generate 4-Wheeler data
                for manufacturer in manufacturers_4w:
                    base_registrations = np.random.randint(8000, 25000)
                    growth_factor = 1 + (year - 2022) * 0.12 + np.random.uniform(-0.18, 0.22)
                    registrations = int(base_registrations * growth_factor)
                    
                    data.append({
                        'date': quarter_start.strftime('%Y-%m-%d'),
                        'year': year,
                        'quarter': quarter,
                        'vehicle_category': '4W',
                        'manufacturer': manufacturer,
                        'registrations': registrations
                    })
        
        return pd.DataFrame(data)
    
    def save_data_to_csv(self, df, filename="vehicle_registrations.csv"):
        """Save dataframe to CSV file"""
        if df is not None:
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False)
            logger.info(f"Data saved to {filepath}")
            return filepath
        return None
    
    def collect_and_save(self):
        """Main method to collect and save data"""
        logger.info("Starting data collection process...")
        
        # Fetch data
        df = self.fetch_vahan_data()
        
        if df is not None:
            # Save to CSV
            filepath = self.save_data_to_csv(df, "vahan_vehicle_data.csv")
            logger.info(f"Data collection completed. Saved {len(df)} records.")
            return filepath
        else:
            logger.error("Data collection failed.")
            return None

def main():
    """Main function for standalone execution"""
    collector = VehicleDataCollector()
    collector.collect_and_save()

if __name__ == "__main__":
    main()
