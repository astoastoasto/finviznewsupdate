import os
import requests
import re
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzr-xHBKsUOpfJmp1zM1IPRxx_16dGiPIFAv1Nf4uVIKEWe1sYEPDxDk_oCVVWeFJa9/exec"

def update_news():
    print("[1/2] Fetching news from Finviz...")
    url = "https://finviz.com/news.ashx?v=3"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ปรับ pattern ให้ตรวจจับเครื่องหมาย + หรือ - นำหน้าตัวเลขได้แม่นยำขึ้น
        pattern = r"\b([A-Z]{1,5})\s*([+-]\d{1,3}\.\d{1,2}%)"
        matches = re.findall(pattern, soup.get_text())
        
        # --- จุดแก้ไข: กรองข้อมูลที่ว่างหรือมีแต่ space ทิ้งตั้งแต่ต้นทาง ---
        new_data = []
        for m in matches:
            ticker = m[0].strip()
            change = m[1].strip()
            # ต้องมีทั้ง Ticker และ Change และไม่ใช่ค่าว่างถึงจะเอาใส่ List
            if ticker and change:
                new_data.append([ticker, change])
        
        # ถ้ากรองแล้วไม่เหลือข้อมูล (Empty List) ให้จบการทำงานทันที ไม่ต้องส่ง Request
        if not new_data:
            print("[SKIP] No valid stock news found. Process ended without sending.")
            return

        print(f"[OK] Found {len(new_data)} valid news items.")

        # [2/2] ส่งข้อมูลไปยัง Google Apps Script
        print("[2/2] Sending data to Google Apps Script...")
        
        # ส่งแบบ JSON
        post_response = requests.post(WEBAPP_URL, json=new_data, timeout=20)
        
        if post_response.status_code == 200:
            # พิมพ์ Response จาก GAS ออกมาดูว่า Success หรือ Skipped
            print(f"[SUCCESS] Server Response: {post_response.text}")
        else:
            print(f"[ERROR] Server returned code: {post_response.status_code}")
            print(f"Response content: {post_response.text}")

    except Exception as e:
        print(f"[CRITICAL ERROR] {str(e)}")

if __name__ == "__main__":
    update_news()
