#!/usr/bin/env python3
"""
Debug version of the scraper to see what's on the page
"""

from annuity_scraper import AnnuityRateWatchScraper
from bs4 import BeautifulSoup
import json

def debug_page():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    print("🔍 Debug mode - examining page content...")
    
    # Create scraper instance
    scraper = AnnuityRateWatchScraper(username, password)
    
    # Login first
    if not scraper.login():
        print("❌ Login failed")
        return
    
    # Get the first page
    url = f"{scraper.base_url}?pageNo=1"
    print(f"📄 Fetching: {url}")
    
    response = scraper.session.get(url)
    
    if response.status_code == 200:
        # Save raw HTML for inspection
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 Raw HTML saved to: debug_page.html")
        
        # Parse and analyze the content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"\n📊 Page Analysis:")
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"Page URL: {response.url}")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"🗂️  Tables found: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"  Table {i}: {len(rows)} rows")
            if table.get('class'):
                print(f"    Classes: {table.get('class')}")
            if table.get('id'):
                print(f"    ID: {table.get('id')}")
        
        # Look for other potential data containers
        divs_with_class = soup.find_all('div', class_=True)
        print(f"📦 Divs with classes: {len(divs_with_class)}")
        
        # Look for form elements that might contain data
        forms = soup.find_all('form')
        print(f"📝 Forms found: {len(forms)}")
        
        # Look for list items
        lists = soup.find_all(['ul', 'ol'])
        print(f"📋 Lists found: {len(lists)}")
        
        # Check for specific classes that might contain data
        data_containers = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(
            keyword in ' '.join(x).lower() 
            for keyword in ['data', 'table', 'grid', 'row', 'item', 'product', 'annuity', 'rate']
        ))
        print(f"🎯 Potential data containers: {len(data_containers)}")
        
        # Show some sample content
        print(f"\n📝 First 500 characters of body text:")
        body_text = soup.get_text()[:500] if soup.get_text() else "No text found"
        print(body_text)
        
        # Check for JavaScript/dynamic content indicators
        scripts = soup.find_all('script')
        print(f"\n🔧 JavaScript files: {len(scripts)}")
        
        # Look for AJAX or dynamic loading indicators
        js_keywords = ['ajax', 'fetch', 'xhr', 'load', 'dynamic']
        js_content = ' '.join([script.string or '' for script in scripts if script.string])
        found_keywords = [kw for kw in js_keywords if kw in js_content.lower()]
        if found_keywords:
            print(f"⚡ Possible dynamic content indicators: {found_keywords}")
        
        print(f"\n💡 Recommendations:")
        if len(tables) == 0:
            print("- No HTML tables found - data might be in divs or loaded dynamically")
        if len(data_containers) > 0:
            print("- Found potential data containers - might need custom extraction")
        if found_keywords:
            print("- Page uses JavaScript - might need browser automation (Selenium)")
        
    else:
        print(f"❌ Failed to fetch page: {response.status_code}")

if __name__ == "__main__":
    debug_page() 