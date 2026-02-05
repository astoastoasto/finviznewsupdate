import os
import json
import gspread
import requests
import re
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials

# 1. ดึงข้อมูลจาก Finviz
url = "https://finviz.com/news.ashx?v=3"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
pattern = r"\b([A-Z]{1,5})\s*([+-]?\d{1,3}\.\d{1,2}%)"
matches = re.findall(pattern, soup.get_text())
final_output = [["Ticker", "Change"]]
for m in matches:
    final_output.append([m[0], m[1]])

# 2. เชื่อมต่อ Google Sheets ผ่าน Secrets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
gc = gspread.authorize(creds)

# 3. บันทึก (ใช้ไฟล์ชื่อ Finviz_News_Update ตามที่ตกลงกันไว้)
sh = gc.open("Finviz_News_Update")
worksheet = sh.get_worksheet(0)
worksheet.clear()
worksheet.update(values=final_output, range_name='A1')

print(f"Update Successful: {len(final_output)-1} items found.")
