#!/usr/bin/env python3
"""
Debug version of AJAX scraper to see what responses we're getting
"""

from ajax_scraper import AjaxAnnuityRateWatchScraper
import json
import time

def debug_ajax_responses():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    scraper = AjaxAnnuityRateWatchScraper(username, password)
    
    print("🔍 Debug AJAX mode...")
    
    if not scraper.login():
        print("❌ Login failed")
        return
    
    # Make each AJAX call and save the response
    ajax_methods = ['listLoad', 'listUpdateRates', 'listFilterProducts', 'listLoadProducts']
    
    for method in ajax_methods:
        print(f"\n🔄 Testing AJAX method: {method}")
        response = scraper.make_ajax_call(method)
        
        if response:
            # Save to file
            filename = f"ajax_response_{method}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2, ensure_ascii=False)
                print(f"💾 Response saved to: {filename}")
                
                # Show preview of response
                if "raw_response" in response:
                    raw = response["raw_response"]
                    print(f"📄 Raw response type: {type(raw)}")
                    print(f"📄 Raw response length: {len(raw) if raw else 0}")
                    print(f"📄 First 200 chars: {raw[:200] if raw else 'Empty'}")
                    
                    # Save raw HTML separately if it looks like HTML
                    if raw and ('<' in raw or '{' in raw):
                        html_filename = f"ajax_response_{method}.html"
                        with open(html_filename, 'w', encoding='utf-8') as f:
                            f.write(raw)
                        print(f"💾 Raw HTML saved to: {html_filename}")
                else:
                    print(f"📊 JSON response: {json.dumps(response, indent=2)[:300]}...")
                    
            except Exception as e:
                print(f"❌ Error saving response: {str(e)}")
        else:
            print(f"❌ No response for {method}")
    
    print(f"\n🔍 All AJAX responses saved for analysis")

if __name__ == "__main__":
    debug_ajax_responses() 