#!/usr/bin/env python3
"""
Selenium-based AnnuityRateWatch Scraper
Handles JavaScript-loaded content to extract table data
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from typing import List, Dict
from bs4 import BeautifulSoup


class SeleniumAnnuityRateWatchScraper:
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.driver = None
        self.headless = headless
        self.wait = None

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
            
            # Automatically download and setup ChromeDriver
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
            self.driver.get("https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm")
            
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
            
            # Wait for successful login - give it time to process
            time.sleep(3)
            
            # Check for login success indicators
            page_source = self.driver.page_source.lower()
            
            # Multiple ways to detect successful login
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
                pass  # Progress bars might not be present
            
            # Wait for tables to appear
            start_time = time.time()
            while time.time() - start_time < timeout:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                
                # Check if we found data tables (not just layout tables)
                data_tables = []
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 2:  # Header + at least 2 data rows
                        data_tables.append(table)
                
                if data_tables:
                    print(f"✅ Found {len(data_tables)} data tables!")
                    return True
                
                # Also check for specific content that indicates data has loaded
                page_source = self.driver.page_source
                if any(keyword in page_source.lower() for keyword in ['rate', 'annuity', 'company', 'yield']):
                    tables_html = self.driver.find_elements(By.TAG_NAME, "table")
                    if tables_html:
                        print("✅ Tables with data content found!")
                        return True
                
                time.sleep(1)
            
            print("⚠️ Timeout waiting for tables, but proceeding anyway...")
            return True
            
        except Exception as e:
            print(f"❌ Error waiting for tables: {str(e)}")
            return False

    def extract_table_data(self) -> List[Dict]:
        """Extract all table data from the current page"""
        try:
            print("📊 Extracting table data...")
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            all_data = []
            
            for table_idx, table in enumerate(tables):
                # Skip small tables (likely layout/navigation)
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                print(f"📋 Processing table {table_idx + 1} with {len(rows)} rows...")
                
                # Extract headers
                header_row = rows[0]
                headers = []
                for cell in header_row.find_all(['th', 'td']):
                    header_text = cell.get_text(strip=True)
                    headers.append(header_text if header_text else f"Column_{len(headers) + 1}")
                
                if not headers:
                    continue
                
                # Extract data rows
                for row_idx, row in enumerate(rows[1:]):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == 0:
                        continue
                    
                    row_data = {
                        'table_index': table_idx,
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
            
            print(f"✅ Extracted {len(all_data)} total rows from {len([t for t in tables if len(t.find_all('tr')) > 1])} tables")
            return all_data
            
        except Exception as e:
            print(f"❌ Error extracting table data: {str(e)}")
            return []

    def scrape_page(self, url: str = None) -> List[Dict]:
        """Scrape a specific page"""
        try:
            if url:
                print(f"🔄 Navigating to: {url}")
                self.driver.get(url)
            
            # Wait for content to load
            if not self.wait_for_tables():
                print("⚠️ Tables didn't load as expected, but continuing...")
            
            # Give it a bit more time for dynamic content
            time.sleep(3)
            
            # Extract data
            return self.extract_table_data()
            
        except Exception as e:
            print(f"❌ Error scraping page: {str(e)}")
            return []

    def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple pages"""
        all_data = []
        
        for i, url in enumerate(urls):
            print(f"\n📄 Scraping page {i + 1}/{len(urls)}: {url}")
            page_data = self.scrape_page(url)
            
            # Add page info to each row
            for row in page_data:
                row['scraped_page'] = i + 1
            
            all_data.extend(page_data)
            
            # Be polite - wait between pages
            if i < len(urls) - 1:
                time.sleep(2)
        
        return all_data

    def scrape_main_pages(self) -> List[Dict]:
        """Scrape the main annuity data pages"""
        urls_to_scrape = [
            "https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm",
            "https://members.annuityratewatch.com/lifeinnovators/instn/cd-spreadsheet.htm",
            "https://members.annuityratewatch.com/lifeinnovators/instn/top-cd-annuities.htm",
        ]
        
        return self.scrape_multiple_pages(urls_to_scrape)

    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save data to JSON file in output folder"""
        if filename is None:
            filename = f"output/annuity_data_{int(time.time())}.json"
        else:
            filename = f"output/{filename}"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔄 Browser closed")

    def run(self) -> List[Dict]:
        """Main method to run the scraper"""
        try:
            if not self.setup_driver():
                return []
            
            if not self.login():
                return []
            
            print("🚀 Starting table data extraction...")
            data = self.scrape_main_pages()
            
            return data
            
        finally:
            self.close()


def main():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    # Create scraper (set headless=False to see browser)
    scraper = SeleniumAnnuityRateWatchScraper(username, password, headless=True)
    
    print("🚀 Starting Selenium AnnuityRateWatch scraper...")
    data = scraper.run()
    
    if data:
        print(f"\n✅ Scraping completed! Total rows extracted: {len(data)}")
        scraper.save_to_json(data)
        
        # Show sample
        if len(data) > 0:
            print("\n📋 Sample of extracted data:")
            print(json.dumps(data[0], indent=2))
    else:
        print("❌ No data was extracted.")


if __name__ == "__main__":
    main() 