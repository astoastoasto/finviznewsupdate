import os
import requests
import re
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# นำ Web App URL ที่ได้จากการ Deploy ใน Google Apps Script มาวางที่นี่
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyJQCQQ5owXbuejdEVdC--DvWZUPMKLEgGKvWxZjKhYmLuPlqpsDUNsTPeYIgHFQIJ-/exec"

def update_news():
    print("[1/2] Fetching news from Finviz...")
    url = "https://finviz.com/news.ashx?v=3"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ค้นหา Ticker และ %Change (เช่น NVDA +7.87%)
        pattern = r"\b([A-Z]{1,5})\s*([+-]?\d{1,3}\.\d{1,2}%)"
        matches = re.findall(pattern, soup.get_text())
        
        # กรองข้อมูลให้อยู่ในรูปแบบ List of Lists: [[Ticker, Change], ...]
        # โดยไม่ใส่หัวข้อ "Ticker", "Change" เข้าไปในข้อมูลดิบ
        new_data = [[m[0], m[1]] for m in matches]
        
        if not new_data:
            print("[SKIP] No stock news found on Finviz. Process ended.")
            return

        print(f"[OK] Found {len(new_data)} news items.")

        # [2/2] ส่งข้อมูลไปยัง Google Apps Script
        print("[2/2] Sending data to Google Apps Script...")
        
        # ส่งแบบ POST พร้อมข้อมูล JSON
        post_response = requests.post(WEBAPP_URL, json=new_data, timeout=20)
        
        if post_response.status_code == 200:
            print(f"[SUCCESS] Server Response: {post_response.text}")
        else:
            print(f"[ERROR] Server returned code: {post_response.status_code}")
            print(f"Response content: {post_response.text}")

    except Exception as e:
        print(f"[CRITICAL ERROR] {str(e)}")

if __name__ == "__main__":
    update_news()
