#!/usr/bin/env python3
"""
Paginated Selenium-based AnnuityRateWatch Scraper
Loops through all pages to get complete dataset
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
import time
import re
from typing import List, Dict
from bs4 import BeautifulSoup


class PaginatedSeleniumAnnuityRateWatchScraper:
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.driver = None
        self.headless = headless
        self.wait = None
        self.base_url = "https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm"

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Chrome WebDriver setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up WebDriver: {str(e)}")
            return False

    def login(self) -> bool:
        """Login to the website"""
        try:
            print("🔑 Logging in...")
            
            # Navigate to the login page
            self.driver.get(f"{self.base_url}?pageNo=1")
            
            # Wait for and fill username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Fill password
            password_field = self.driver.find_element(By.ID, "userpass")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "doLogin")
            login_button.click()
            
            # Wait for successful login and page content to load
            time.sleep(10)
            
            # Check for login success indicators
            page_source = self.driver.page_source.lower()
            
            login_success = (
                self.username.lower() in page_source or
                "caleb" in page_source or
                "account" in page_source or
                "collection" in page_source
            )
            
            if login_success:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed - could not find account indicators")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False

    def get_total_pages(self) -> int:
        """Extract total number of pages from the pagination info"""
        try:
            # Look for pagination text like "Page 1 of 36"
            page_source = self.driver.page_source
            
            # Try different patterns for pagination
            patterns = [
                r'Page \d+ of (\d+)',
                r'page \d+ of (\d+)',
                r'showing \d+-\d+ out of \d+ records',
                r'(\d+) records',
                r'(\d+) total'
            ]
            
            total_pages = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    if 'page' in pattern.lower():
                        total_pages = int(matches[0])
                        print(f"📄 Found pagination: Total pages = {total_pages}")
                        break
                    elif 'records' in pattern.lower():
                        # Estimate pages based on records (typically 50 per page)
                        total_records = int(matches[0])
                        total_pages = (total_records + 49) // 50  # Round up
                        print(f"📊 Found {total_records} records, estimating {total_pages} pages")
                        break
            
            # If we couldn't find pagination info, default to trying a reasonable number
            if total_pages == 0:
                print("⚠️ Could not determine total pages, defaulting to 40")
                total_pages = 40
            
            return total_pages
            
        except Exception as e:
            print(f"❌ Error getting total pages: {str(e)}")
            return 40  # Default fallback

    def wait_for_tables(self, timeout: int = 30) -> bool:
        """Wait for tables to load on the page"""
        try:
            print("⏳ Waiting for tables to load...")
            
            # Wait for any progress bars to complete
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".progress-bar"))
                )
            except:
                pass
            
            # Wait for tables to appear
            start_time = time.time()
            while time.time() - start_time < timeout:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                
                # Check if we found data tables
                data_tables = []
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 2:
                        data_tables.append(table)
                
                if data_tables:
                    return True
                
                time.sleep(1)
            
            print("⚠️ Timeout waiting for tables, but proceeding anyway...")
            return True
            
        except Exception as e:
            print(f"❌ Error waiting for tables: {str(e)}")
            return False

    def extract_table_data(self, page_num: int) -> List[Dict]:
        """Extract data from the main product table only"""
        try:
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            
            # Find the main data table (should be the largest one with the most columns)
            main_table = None
            max_columns = 0
            
            print(f"📊 Found {len(tables)} tables on page {page_num}")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Count columns in the first row
                first_row = rows[0]
                columns = len(first_row.find_all(['th', 'td']))
                
                print(f"  Table {table_idx}: {len(rows)} rows, {columns} columns")
                
                # Look for tables with many columns (main data table should have 10+ columns)
                if columns > max_columns and columns >= 10:
                    max_columns = columns
                    main_table = table
                    print(f"  ⭐ New main table candidate: {columns} columns")
            
            if not main_table:
                print("⚠️ Could not find main data table, using largest table")
                # Fallback: use the table with the most rows
                max_rows = 0
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > max_rows:
                        max_rows = len(rows)
                        main_table = table
            
            if not main_table:
                print("❌ No suitable table found")
                return []
            
            # Extract data from the main table only
            rows = main_table.find_all('tr')
            print(f"🎯 Extracting from main table: {len(rows)} rows, {max_columns} columns")
            
            # Extract headers
            header_row = rows[0]
            headers = []
            for cell in header_row.find_all(['th', 'td']):
                header_text = cell.get_text(strip=True)
                headers.append(header_text if header_text else f"Column_{len(headers) + 1}")
            
            print(f"📋 Headers: {headers[:5]}..." if len(headers) > 5 else f"📋 Headers: {headers}")
            
            all_data = []
            
            # Extract data rows
            for row_idx, row in enumerate(rows[1:]):
                cells = row.find_all(['td', 'th'])
                if len(cells) == 0:
                    continue
                
                row_data = {
                    'page_number': page_num,
                    'row_index': row_idx,
                    'source_url': self.driver.current_url
                }
                
                for col_idx, cell in enumerate(cells):
                    header = headers[col_idx] if col_idx < len(headers) else f"Column_{col_idx + 1}"
                    cell_text = cell.get_text(strip=True)
                    row_data[header] = cell_text
                    
                    # Capture links
                    links = cell.find_all('a')
                    if links:
                        row_data[f"{header}_links"] = [
                            {'text': link.get_text(strip=True), 'href': link.get('href')}
                            for link in links
                        ]
                
                all_data.append(row_data)
            
            # Map generic column names to proper headers
            mapped_data = self.map_column_headers(all_data)
            
            return mapped_data
            
        except Exception as e:
            print(f"❌ Error extracting table data: {str(e)}")
            return []

    def map_column_headers(self, data: List[Dict]) -> List[Dict]:
        """Map generic column names to proper header names and filter out grouping rows"""
        
        # Define proper column mapping based on the website structure
        # Note: Column_1 (Group_By) is skipped as it's just table structure metadata
        column_mapping = {
            # 'Column_1': 'Group_By',  # Skip - just empty table structure
            'Column_2': 'Company_Product_Name', 
            'Column_3': 'AM_Best',
            'Column_4': 'Max_Issue_Age',
            'Column_5': 'Min_Premium',
            'Column_6': 'SC_Years',
            'Column_7': 'Free_Withdrawal_Yr1_Yr2',
            'Column_8': 'Last_Change',
            'Column_9': 'Premium_Bonus',
            'Column_10': 'Current_Rate',
            'Column_11': 'Base_Rate',
            'Column_12': 'Years',
            'Column_13': 'GTD_Yield_Rate',
            'Column_14': 'Commission'
        }
        
        # Filter and map each row
        mapped_data = []
        for row in data:
            # Skip grouping rows by checking if key product fields are missing
            if self.is_grouping_row(row):
                continue
                
            mapped_row = {}
            
            # Skip metadata fields - we only want the actual product data
            # (page_number, row_index, source_url are just scraping artifacts)
            
            # Map column names and clean up text formatting
            for old_key, new_key in column_mapping.items():
                if old_key in row:
                    value = row[old_key]
                    
                    # Clean up common formatting issues
                    if isinstance(value, str):
                        # Replace newline-separated fractions with clean format
                        value = value.replace('\n/\n', ' / ')
                        value = value.replace('\n/', ' /')
                        value = value.replace('/\n', '/ ')
                    
                    mapped_row[new_key] = value
                
                # Skip link fields - we don't need the URLs, just the text content
            
            mapped_data.append(mapped_row)
        
        return mapped_data

    def remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicate rows based on product data (excluding page_number and row_index)"""
        
        seen_products = set()
        unique_data = []
        duplicates_removed = 0
        
        for row in data:
            # Create a signature for this product based on key fields (excluding metadata)
            product_signature = {}
            
            # Include all fields for comparison (since metadata is already excluded from final output)
            for key, value in row.items():
                # Skip link fields as they contain URLs which may vary
                if key.endswith('_links'):
                    continue
                    
                # Convert to string and normalize for comparison
                if isinstance(value, str):
                    product_signature[key] = value.strip()
                else:
                    product_signature[key] = value
            
            # Create a hashable signature
            signature_str = str(sorted(product_signature.items()))
            
            if signature_str not in seen_products:
                seen_products.add(signature_str)
                unique_data.append(row)
            else:
                duplicates_removed += 1
        
        if duplicates_removed > 0:
            print(f"🧹 Removed {duplicates_removed} duplicate products")
            print(f"📊 Unique products: {len(unique_data)}")
        
        return unique_data

    def is_grouping_row(self, row: Dict) -> bool:
        """Check if a row is a grouping/section header by looking for missing product data"""
        
        # Key fields that real product rows should have
        required_fields = [
            'Column_2',  # Company_Product_Name
            'Column_3',  # AM_Best  
            'Column_4',  # Max_Issue_Age
            'Column_10', # Current_Rate
        ]
        
        # Count how many required fields have actual data
        filled_fields = 0
        for field in required_fields:
            value = row.get(field, '').strip()
            if value and value not in ['', '-', 'N/A', 'NR']:
                filled_fields += 1
        
        # If less than 2 key fields are filled, it's likely a grouping row
        # Real product rows should have at least company name + one other key field
        if filled_fields < 2:
            return True
            
        # Additional check: if only Group_By (Column_1) has content and nothing else
        group_by = row.get('Column_1', '').strip()
        if group_by and filled_fields == 0:
            return True
            
        return False

    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape a specific page number"""
        try:
            url = f"{self.base_url}?pageNo={page_num}"
            print(f"🔄 Scraping page {page_num}: {url}")
            
            self.driver.get(url)
            
            # Wait for content to load
            if not self.wait_for_tables():
                print("⚠️ Tables didn't load as expected, but continuing...")
            
            # Give it time for dynamic content
            time.sleep(2)
            
            # Extract data
            data = self.extract_table_data(page_num)
            print(f"📊 Extracted {len(data)} rows from page {page_num}")
            
            return data
            
        except Exception as e:
            print(f"❌ Error scraping page {page_num}: {str(e)}")
            return []

    def scrape_all_pages(self, max_pages: int = None) -> List[Dict]:
        """Scrape all pages with intelligent end detection"""
        all_data = []
        page_num = 1
        consecutive_empty_pages = 0
        last_page_data_signature = None
        
        print(f"🚀 Starting to scrape pages with intelligent end detection...")
        if max_pages:
            print(f"📊 Maximum pages limit: {max_pages}")
        
        while True:
            try:
                print(f"🔄 Scraping page {page_num}...")
                page_data = self.scrape_page(page_num)
                
                if page_data:
                    # Create a signature of this page's data for duplicate detection
                    page_signature = self.create_page_signature(page_data)
                    
                    # Check if this page has the same data as the previous page
                    if last_page_data_signature and page_signature == last_page_data_signature:
                        print(f"🔄 Page {page_num} has identical data to previous page - reached end!")
                        break
                    
                    all_data.extend(page_data)
                    consecutive_empty_pages = 0  # Reset counter
                    last_page_data_signature = page_signature
                    
                    print(f"✅ Page {page_num}: {len(page_data)} rows (Total so far: {len(all_data)})")
                    
                else:
                    consecutive_empty_pages += 1
                    print(f"⚠️ Page {page_num}: No data found (empty pages: {consecutive_empty_pages})")
                    
                    # Stop if we get 3 consecutive empty pages
                    if consecutive_empty_pages >= 3:
                        print(f"🛑 Found {consecutive_empty_pages} consecutive empty pages - reached end!")
                        break
                
                # Check if we've hit the optional max_pages limit
                if max_pages and page_num >= max_pages:
                    print(f"📊 Reached maximum pages limit ({max_pages})")
                    break
                
                # Be polite to the server
                time.sleep(1)
                page_num += 1
                
            except Exception as e:
                print(f"❌ Error on page {page_num}: {str(e)}")
                consecutive_empty_pages += 1
                
                # If we get too many errors, probably reached the end
                if consecutive_empty_pages >= 3:
                    print(f"🛑 Too many consecutive errors - likely reached end!")
                    break
                    
                page_num += 1
                continue
        
        print(f"\n📊 Completed scraping {page_num-1} pages")
        
        # Remove duplicates after scraping all pages
        print(f"🧹 Removing duplicates from {len(all_data)} total rows...")
        unique_data = self.remove_duplicates(all_data)
        
        return unique_data

    def create_page_signature(self, page_data: List[Dict]) -> str:
        """Create a signature for a page's data to detect identical pages"""
        if not page_data:
            return "empty"
        
        # Use the first few and last few products to create a signature
        signature_products = []
        
        # First 3 products
        for i in range(min(3, len(page_data))):
            product = page_data[i]
            company = product.get('Company_Product_Name', '')
            rate = product.get('Current_Rate', '')
            signature_products.append(f"{company}:{rate}")
        
        # Last 3 products (if different from first)
        if len(page_data) > 6:
            for i in range(max(3, len(page_data)-3), len(page_data)):
                product = page_data[i]
                company = product.get('Company_Product_Name', '')
                rate = product.get('Current_Rate', '')
                signature_products.append(f"{company}:{rate}")
        
        return "|".join(signature_products)

    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save data to JSON file in output folder"""
        if filename is None:
            filename = f"output/complete_annuity_data_{int(time.time())}.json"
        else:
            filename = f"output/{filename}"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")

    def save_to_csv(self, data: List[Dict], filename: str = None):
        """Save data to CSV file in output folder with proper column order"""
        if not data:
            print("⚠️ No data to save to CSV")
            return
            
        if filename is None:
            filename = f"output/complete_annuity_data_{int(time.time())}.csv"
        else:
            filename = f"output/{filename}"
        
        try:
            # Define the preferred column order based on the table structure
            preferred_order = [
                'Carrier_Product_Name',
                'AM_Best',
                'Max_Issue_Age', 
                'Min_Premium',
                'SC_Years',
                'Free_Withdrawal_Yr1_Yr2',
                'Last_Change',
                'Premium_Bonus',
                'Current_Rate',
                'Base_Rate',
                'Years_Rate_GTD',
                'GTD_Yield_Surrender',
                'Commission'
            ]
            
            # Get all unique column names from the data
            all_columns = set()
            for row in data:
                all_columns.update(row.keys())
            
            # Start with preferred order, then add any additional columns
            columns = []
            for col in preferred_order:
                if col in all_columns:
                    columns.append(col)
                    all_columns.remove(col)
            
            # Add any remaining columns (sorted alphabetically)
            columns.extend(sorted(list(all_columns)))
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"💾 Data saved to {filename} with {len(columns)} columns")
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔄 Browser closed")

    def run(self, max_pages: int = None) -> List[Dict]:
        """Main method to run the scraper"""
        try:
            if not self.setup_driver():
                return []
            
            if not self.login():
                return []
            
            print("🚀 Starting complete pagination scraping...")
            data = self.scrape_all_pages(max_pages)
            
            return data
            
        finally:
            self.close()


def main():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    # Create scraper (set headless=False to see browser)
    scraper = PaginatedSeleniumAnnuityRateWatchScraper(username, password, headless=True)
    
    print("🚀 Starting Complete Paginated AnnuityRateWatch scraper...")
    
    # Scrape all pages (or set max_pages=5 for testing)
    data = scraper.run(max_pages=None)  # None = scrape all pages
    
    if data:
        print(f"\n✅ Scraping completed! Total rows extracted: {len(data)}")
        
        # Save in both formats
        scraper.save_to_json(data)
        scraper.save_to_csv(data)
        
        # Show sample
        if len(data) > 0:
            print("\n📋 Sample of extracted data:")
            print(json.dumps(data[0], indent=2))
            
            # Show some stats
            pages_scraped = len(set([row.get('page_number', 0) for row in data]))
            print(f"\n📊 Statistics:")
            print(f"   Total rows: {len(data)}")
            print(f"   Pages scraped: {pages_scraped}")
            print(f"   Average rows per page: {len(data) // pages_scraped if pages_scraped > 0 else 0}")
    else:
        print("❌ No data was extracted.")


if __name__ == "__main__":
    main() 