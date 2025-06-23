#!/usr/bin/env python3
"""
Debug Selenium scraper to troubleshoot login issues
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_selenium_login():
    print("🔍 Debug Selenium login process...")
    
    # Setup Chrome with visible browser for debugging
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🔄 Navigating to login page...")
        driver.get("https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm")
        
        print("📄 Page title:", driver.title)
        print("📄 Current URL:", driver.current_url)
        
        # Take screenshot before login
        driver.save_screenshot("before_login.png")
        print("📸 Screenshot saved: before_login.png")
        
        # Check if we can find the login form
        try:
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            print("✅ Found username field")
        except Exception as e:
            print(f"❌ Could not find username field: {e}")
            # Save page source for debugging
            with open("login_page_source.html", "w") as f:
                f.write(driver.page_source)
            print("💾 Page source saved to login_page_source.html")
            return
        
        # Fill in credentials
        print("✏️ Filling username...")
        username_field.clear()
        username_field.send_keys("calebshump")
        
        print("✏️ Filling password...")
        password_field = driver.find_element(By.ID, "userpass")
        password_field.clear()
        password_field.send_keys("TacoTuesday")
        
        # Take screenshot before clicking login
        driver.save_screenshot("before_login_click.png")
        print("📸 Screenshot saved: before_login_click.png")
        
        print("🔑 Clicking login button...")
        login_button = driver.find_element(By.NAME, "doLogin")
        login_button.click()
        
        # Wait a bit for the page to process
        time.sleep(5)
        
        print("📄 After login - Page title:", driver.title)
        print("📄 After login - Current URL:", driver.current_url)
        
        # Take screenshot after login
        driver.save_screenshot("after_login.png")
        print("📸 Screenshot saved: after_login.png")
        
        # Save page source after login
        with open("after_login_source.html", "w") as f:
            f.write(driver.page_source)
        print("💾 After login page source saved to after_login_source.html")
        
        # Check for various login success indicators
        page_source = driver.page_source.lower()
        
        print("\n🔍 Checking for login success indicators:")
        print(f"  - Contains 'caleb': {'caleb' in page_source}")
        print(f"  - Contains 'shumpert': {'shumpert' in page_source}")
        print(f"  - Contains 'log out': {'log out' in page_source}")
        print(f"  - Contains 'logout': {'logout' in page_source}")
        print(f"  - Contains 'account': {'account' in page_source}")
        print(f"  - Contains 'collection': {'collection' in page_source}")
        
        # Try to find specific elements
        try:
            logout_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Log out")
            print("✅ Found 'Log out' link")
        except:
            print("❌ Could not find 'Log out' link")
        
        try:
            account_element = driver.find_element(By.PARTIAL_LINK_TEXT, "Account")
            print("✅ Found 'Account' link")
        except:
            print("❌ Could not find 'Account' link")
        
        # Look for the user's name
        try:
            user_element = driver.find_element(By.PARTIAL_LINK_TEXT, "Caleb")
            print("✅ Found user name 'Caleb'")
        except:
            print("❌ Could not find user name 'Caleb'")
        
        # Check if we're still on a login page
        if "login" in driver.current_url.lower() or "signin" in driver.current_url.lower():
            print("⚠️ Still appears to be on login page")
        else:
            print("✅ Appears to have navigated away from login page")
        
        # Wait longer to see if content loads
        print("⏳ Waiting 10 seconds for content to load...")
        time.sleep(10)
        
        # Check for tables after waiting
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"🗂️ Tables found after waiting: {len(tables)}")
        
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 2:
                print(f"  Table {i}: {len(rows)} rows (potential data table)")
        
        # Final screenshot
        driver.save_screenshot("final_state.png")
        print("📸 Final screenshot saved: final_state.png")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        driver.save_screenshot("error_state.png")
        
    finally:
        print("🔄 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    debug_selenium_login() 