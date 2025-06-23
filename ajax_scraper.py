#!/usr/bin/env python3
"""
Enhanced AnnuityRateWatch AJAX Scraper
Makes direct AJAX calls to get the actual product data
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Optional


class AjaxAnnuityRateWatchScraper:
    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.base_url = "https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm"
        self.ajax_url = "https://members.annuityratewatch.com/serverCall.cfc"
        
        # Variables extracted from the page
        self.thelistID = None
        self.theOrgListID = None  
        self.theOrgTabID = None
        self.theUserID = None
        
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
        """Authenticate with the AnnuityRateWatch website"""
        try:
            # Get the login page
            response = self.session.get(self.base_url)
            
            if response.status_code != 200:
                print(f"Error accessing login page: {response.status_code}")
                return False
            
            # Submit login with correct field names
            login_data = {
                'username': self.username,
                'userpass': self.password,
                'doLogin': ''
            }
            
            login_response = self.session.post(self.base_url, data=login_data, allow_redirects=True)
            
            if login_response.status_code == 200:
                # Check if we're logged in by looking for account info
                if self.username.lower() in login_response.text.lower() or 'log out' in login_response.text.lower():
                    print("✅ Login successful!")
                    
                    # Extract the necessary IDs from the page
                    self.extract_page_variables(login_response.text)
                    return True
                else:
                    print("❌ Login appears to have failed")
                    return False
            else:
                print(f"❌ Login failed with status code: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False

    def extract_page_variables(self, html_content: str):
        """Extract JavaScript variables needed for AJAX calls"""
        try:
            # Look for thelistID, theOrgListID, etc. in the JavaScript
            list_id_match = re.search(r'thelistID\s*=\s*["\']?(\d+)["\']?', html_content)
            if list_id_match:
                self.thelistID = list_id_match.group(1)
                print(f"📋 Found thelistID: {self.thelistID}")
            
            org_list_id_match = re.search(r'theOrgListID\s*=\s*["\']?(\d+)["\']?', html_content)
            if org_list_id_match:
                self.theOrgListID = org_list_id_match.group(1)
                print(f"📋 Found theOrgListID: {self.theOrgListID}")
            
            org_tab_id_match = re.search(r'theOrgTabID\s*=\s*["\']?(\d+)["\']?', html_content)
            if org_tab_id_match:
                self.theOrgTabID = org_tab_id_match.group(1)
                print(f"📋 Found theOrgTabID: {self.theOrgTabID}")
            
            user_id_match = re.search(r'theUserID\s*=\s*["\']?(\d+)["\']?', html_content)
            if user_id_match:
                self.theUserID = user_id_match.group(1)
                print(f"👤 Found theUserID: {self.theUserID}")
            
            # If we can't find them in JS variables, try other patterns
            if not self.thelistID:
                # Sometimes they're in data attributes or other places
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for data attributes
                for elem in soup.find_all(attrs={"data-list-id": True}):
                    self.thelistID = elem.get("data-list-id")
                    break
                    
                # Look for any numbers that might be IDs in the script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for patterns like list_id: 123
                        list_id_pattern = re.search(r'list_id["\']?\s*:\s*["\']?(\d+)', script.string)
                        if list_id_pattern:
                            self.thelistID = list_id_pattern.group(1)
                            break
            
        except Exception as e:
            print(f"⚠️ Error extracting page variables: {str(e)}")

    def make_ajax_call(self, method: str, additional_data: Dict = None) -> Optional[Dict]:
        """Make an AJAX call to the list manager"""
        try:
            # Base data for all AJAX calls
            data = {
                'orgKey': 'lifeinnovators',
                'method': method,
            }
            
            # Add list IDs if available
            if self.thelistID:
                data['list_id'] = self.thelistID
            if self.theOrgListID:
                data['orgList_id'] = self.theOrgListID
            if self.theOrgTabID:
                data['orgTab_id'] = self.theOrgTabID
            if self.theUserID:
                data['user_id'] = self.theUserID
                
            # Add any additional data
            if additional_data:
                data.update(additional_data)
            
            print(f"🔄 Making AJAX call: {method}")
            print(f"📤 Data: {data}")
            
            # Set AJAX headers
            ajax_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': self.base_url
            }
            
            response = self.session.get(
                self.ajax_url,
                params=data,
                headers=ajax_headers
            )
            
            if response.status_code == 200:
                print(f"✅ AJAX call successful")
                
                # Try to parse as JSON
                try:
                    return response.json()
                except:
                    # If not JSON, return the text
                    return {"raw_response": response.text}
            else:
                print(f"❌ AJAX call failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error making AJAX call: {str(e)}")
            return None

    def load_products(self, page_no: int = 1) -> Optional[List[Dict]]:
        """Load product data using AJAX calls"""
        try:
            # Step 1: Load the list
            print(f"📋 Step 1: Loading list...")
            list_result = self.make_ajax_call('listLoad')
            
            if not list_result:
                print("❌ Failed to load list")
                return None
            
            # Step 2: Update rates
            print(f"💰 Step 2: Updating rates...")
            rates_result = self.make_ajax_call('listUpdateRates')
            
            # Step 3: Filter products (if needed)
            print(f"🔍 Step 3: Filtering products...")
            filter_result = self.make_ajax_call('listFilterProducts')
            
            # Step 4: Load the actual products
            print(f"📊 Step 4: Loading products...")
            products_result = self.make_ajax_call('listLoadProducts')
            
            if products_result:
                print(f"✅ Successfully loaded product data")
                return self.parse_product_data(products_result)
            else:
                print("❌ Failed to load products")
                return None
                
        except Exception as e:
            print(f"❌ Error loading products: {str(e)}")
            return None

    def parse_product_data(self, ajax_response: Dict) -> List[Dict]:
        """Parse the AJAX response to extract product data"""
        try:
            products = []
            
            # The response might be HTML, JSON, or mixed
            if "raw_response" in ajax_response:
                html_content = ajax_response["raw_response"]
                
                # Try to parse as HTML and extract data
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for tables in the response
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) < 2:
                        continue
                    
                    # Extract headers
                    header_row = rows[0]
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    
                    # Extract data rows
                    for row_idx, row in enumerate(rows[1:]):
                        cells = row.find_all(['td', 'th'])
                        if len(cells) == 0:
                            continue
                        
                        product_data = {}
                        for col_idx, cell in enumerate(cells):
                            header = headers[col_idx] if col_idx < len(headers) else f"Column_{col_idx + 1}"
                            cell_text = cell.get_text(strip=True)
                            product_data[header] = cell_text
                            
                            # Also capture links
                            links = cell.find_all('a')
                            if links:
                                product_data[f"{header}_links"] = [
                                    {'text': link.get_text(strip=True), 'href': link.get('href')}
                                    for link in links
                                ]
                        
                        products.append(product_data)
                
                # If no tables found, try to extract JSON from the response
                if not products:
                    # Look for JSON patterns in the response
                    json_pattern = re.search(r'\{.*\}', html_content, re.DOTALL)
                    if json_pattern:
                        try:
                            json_data = json.loads(json_pattern.group(0))
                            if isinstance(json_data, dict) and 'data' in json_data:
                                products = json_data['data']
                            elif isinstance(json_data, list):
                                products = json_data
                        except:
                            pass
            
            else:
                # Direct JSON response
                if isinstance(ajax_response, dict):
                    if 'data' in ajax_response:
                        products = ajax_response['data']
                    elif 'products' in ajax_response:
                        products = ajax_response['products']
                    else:
                        products = [ajax_response]
                elif isinstance(ajax_response, list):
                    products = ajax_response
            
            print(f"📊 Parsed {len(products)} products from AJAX response")
            return products
            
        except Exception as e:
            print(f"❌ Error parsing product data: {str(e)}")
            return []

    def scrape_all_products(self) -> List[Dict]:
        """Main method to scrape all products"""
        if not self.login():
            print("❌ Failed to login. Cannot proceed with scraping.")
            return []
        
        print(f"🚀 Starting AJAX-based product scraping...")
        
        # Try to load products using AJAX
        products = self.load_products()
        
        if products:
            print(f"✅ Successfully scraped {len(products)} products")
            return products
        else:
            print("❌ No products were scraped")
            return []

    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save data to JSON file in output folder"""
        if filename is None:
            filename = f"output/ajax_annuity_data_{int(time.time())}.json"
        else:
            filename = f"output/{filename}"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {str(e)}")


def main():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    scraper = AjaxAnnuityRateWatchScraper(username, password)
    
    print("🚀 Starting AJAX AnnuityRateWatch scraper...")
    data = scraper.scrape_all_products()
    
    if data:
        print(f"\n✅ Scraping completed! Total products extracted: {len(data)}")
        scraper.save_to_json(data)
        
        # Print sample of the data
        if len(data) > 0:
            print("\n📋 Sample of extracted data:")
            print(json.dumps(data[0], indent=2))
    else:
        print("❌ No data was extracted.")


if __name__ == "__main__":
    main() 