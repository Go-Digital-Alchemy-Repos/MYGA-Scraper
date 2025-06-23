#!/usr/bin/env python3
"""
AnnuityRateWatch Web Scraper
Scrapes table data from Life Innovators annuity pages and outputs as JSON
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
from typing import List, Dict, Optional
import argparse


class AnnuityRateWatchScraper:
    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.base_url = "https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm"
        
        # Set common headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def login(self) -> bool:
        """
        Authenticate with the AnnuityRateWatch website
        Returns True if login successful, False otherwise
        """
        try:
            # First, get the login page to extract any necessary form tokens
            login_url = "https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                print(f"Error accessing login page: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for login form
            login_form = soup.find('form') or soup.find('div', class_='login') or soup.find('div', id='login')
            
            if not login_form:
                print("Could not find login form on the page")
                return False
            
            # Prepare login data
            login_data = {
                'username': self.username,
                'userpass': self.password,
                'doLogin': ''  # Submit button value
            }
            
            # Look for any hidden inputs or CSRF tokens
            hidden_inputs = soup.find_all('input', type='hidden')
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value')
                if name and value:
                    login_data[name] = value
            
            # Try different common field names for username/password
            username_fields = ['username', 'user', 'email', 'login']
            password_fields = ['password', 'pass', 'pwd']
            
            # Find the actual form action URL
            form_action = login_form.get('action') if login_form.get('action') else login_url
            if not form_action.startswith('http'):
                base_domain = "https://members.annuityratewatch.com"
                form_action = base_domain + form_action if form_action.startswith('/') else base_domain + '/' + form_action
            
            # Submit login
            login_response = self.session.post(form_action, data=login_data, allow_redirects=True)
            
            # Check if login was successful by looking for indicators
            if login_response.status_code == 200:
                # Look for signs that we're logged in (absence of login form, presence of logout, etc.)
                soup = BeautifulSoup(login_response.content, 'html.parser')
                
                # If we still see a login form, authentication likely failed
                if soup.find('input', {'type': 'password'}) and 'login' in login_response.url.lower():
                    print("Login appears to have failed - still seeing login form")
                    return False
                
                print("Login successful!")
                return True
            else:
                print(f"Login failed with status code: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False

    def extract_table_data(self, html_content: str) -> List[Dict]:
        """
        Extract table data from HTML content
        Returns list of dictionaries representing table rows
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        
        all_data = []
        
        for table_idx, table in enumerate(tables):
            # Skip tables that look like navigation or layout tables
            if table.get('class') and any(cls in ['nav', 'menu', 'header', 'footer'] for cls in table.get('class')):
                continue
            
            # Look for data tables (usually have thead/tbody or multiple rows)
            rows = table.find_all('tr')
            if len(rows) < 2:  # Skip tables with only header or single row
                continue
            
            # Extract headers
            header_row = rows[0]
            headers = []
            
            # Try to find headers in th tags first, then td tags
            header_cells = header_row.find_all(['th', 'td'])
            for cell in header_cells:
                header_text = cell.get_text(strip=True)
                headers.append(header_text if header_text else f"Column_{len(headers) + 1}")
            
            if not headers:
                continue
            
            # Extract data rows
            data_rows = rows[1:] if len(rows) > 1 else []
            
            for row_idx, row in enumerate(data_rows):
                cells = row.find_all(['td', 'th'])
                if len(cells) == 0:
                    continue
                
                row_data = {
                    'table_index': table_idx,
                    'row_index': row_idx
                }
                
                for col_idx, cell in enumerate(cells):
                    header = headers[col_idx] if col_idx < len(headers) else f"Column_{col_idx + 1}"
                    cell_text = cell.get_text(strip=True)
                    
                    # Also capture any links in the cell
                    links = cell.find_all('a')
                    if links:
                        cell_links = [{'text': link.get_text(strip=True), 'href': link.get('href')} for link in links]
                        row_data[f"{header}_links"] = cell_links
                    
                    row_data[header] = cell_text
                
                all_data.append(row_data)
        
        return all_data

    def scrape_page(self, page_no: int) -> Optional[List[Dict]]:
        """
        Scrape a specific page number
        Returns list of table data or None if error
        """
        try:
            url = f"{self.base_url}?pageNo={page_no}"
            print(f"Scraping page {page_no}: {url}")
            
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"Error accessing page {page_no}: {response.status_code}")
                return None
            
            # Check if we got redirected to login (session expired)
            if 'login' in response.url.lower() or 'signin' in response.url.lower():
                print(f"Session expired on page {page_no}, attempting to re-login...")
                if self.login():
                    response = self.session.get(url)
                else:
                    print("Re-login failed")
                    return None
            
            table_data = self.extract_table_data(response.content)
            
            if table_data:
                print(f"Extracted {len(table_data)} rows from page {page_no}")
            else:
                print(f"No table data found on page {page_no}")
            
            return table_data
            
        except Exception as e:
            print(f"Error scraping page {page_no}: {str(e)}")
            return None

    def scrape_all_pages(self, start_page: int = 1, max_pages: int = None) -> List[Dict]:
        """
        Scrape all pages starting from start_page
        Returns combined list of all table data
        """
        if not self.login():
            print("Failed to login. Cannot proceed with scraping.")
            return []
        
        all_data = []
        current_page = start_page
        consecutive_empty_pages = 0
        max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
        
        while True:
            if max_pages and current_page > start_page + max_pages - 1:
                print(f"Reached maximum page limit: {max_pages}")
                break
            
            page_data = self.scrape_page(current_page)
            
            if page_data is None:
                print(f"Failed to scrape page {current_page}")
                consecutive_empty_pages += 1
            elif len(page_data) == 0:
                consecutive_empty_pages += 1
                print(f"Page {current_page} contains no data")
            else:
                # Add page number to each row
                for row in page_data:
                    row['page_number'] = current_page
                
                all_data.extend(page_data)
                consecutive_empty_pages = 0
            
            # Stop if we hit too many empty pages in a row
            if consecutive_empty_pages >= max_consecutive_empty:
                print(f"Stopping after {consecutive_empty_pages} consecutive empty/failed pages")
                break
            
            current_page += 1
            
            # Be polite to the server
            time.sleep(1)
        
        return all_data

    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save data to JSON file in output folder"""
        if filename is None:
            filename = f"output/annuity_data_{int(time.time())}.json"
        else:
            filename = f"output/{filename}"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Scrape AnnuityRateWatch table data')
    parser.add_argument('username', help='Username for AnnuityRateWatch')
    parser.add_argument('password', help='Password for AnnuityRateWatch')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number (default: 1)')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to scrape')
    parser.add_argument('--output', '-o', help='Output JSON filename')
    
    args = parser.parse_args()
    
    scraper = AnnuityRateWatchScraper(args.username, args.password)
    
    print("Starting AnnuityRateWatch scraper...")
    data = scraper.scrape_all_pages(args.start_page, args.max_pages)
    
    if data:
        print(f"\nScraping completed! Total rows extracted: {len(data)}")
        scraper.save_to_json(data, args.output)
        
        # Print sample of the data
        if len(data) > 0:
            print("\nSample of extracted data:")
            print(json.dumps(data[0], indent=2))
    else:
        print("No data was extracted.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python annuity_scraper.py <username> <password> [options]")
        print("Example: python annuity_scraper.py myuser mypass --start-page 1 --max-pages 5")
        sys.exit(1)
    
    main() 