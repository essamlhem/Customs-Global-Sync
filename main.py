import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                requests.post(url + "sendDocument", data={'chat_id': CHAT_ID, 'caption': message}, files={'document': f})
        else:
            requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message})
    except Exception as e: print(f"Telegram Error: {e}")

def post_to_website(file_path):
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # رجعنا لصيغة Excel لأن السيرفر أعطى 400 على الـ CSV
            files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {'command': 'import_customs_excel'}
            response = requests.post(SITE_URL, headers=headers, files=files, data=data, timeout=300)
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح"
            else:
                return f"❌ فشل: {response.status_code} ({response.text[:30]})"
    except Exception as e: return f"❌ خطأ: {str(e)[:30]}"

def main():
    try:
        scraper = SupabaseScraper()
        df = DataProcessor().process_data(scraper.fetch_raw_data())
        
        # تحسين: حذف الأعمدة الفارغة تماماً لتقليل الحجم
        df = df.dropna(how='all', axis=1)

        file_name = "Across_MENA_Update.xlsx"
        # حفظ بأعلى ضغط ممكن للإكسل
        df.to_excel(file_name, index=False, engine='openpyxl')
        
        file_size = os.path.getsize(file_name) / 1024
        web_status = post_to_website(file_name)
        
        report = f"Across MENA Update\nStatus: {web_status}\nItems: {len(df)}\nSize: {file_size:.1f} KB"
        send_telegram(report, file_name)
    except Exception as e: send_telegram(f"Error: {e}")

if __name__ == "__main__":
    main()
