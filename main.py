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
    # تنظيف الرسالة من الرموز التي تسبب خطأ في تليجرام
    clean_message = message.replace("_", " ").replace("*", "")
    try:
        if file_path and os.path.exists(file_path):
            r = requests.post(url + "sendDocument", 
                              data={'chat_id': CHAT_ID, 'caption': clean_message}, 
                              files={'document': open(file_path, 'rb')})
        else:
            r = requests.post(url + "sendMessage", 
                              data={'chat_id': CHAT_ID, 'text': clean_message})
        print(f"📡 Telegram Sync: {r.status_code}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def post_to_website(file_path):
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # تم تعديل الأمر ليتوافق مع طلب السيرفر بدقة
            files = {'file': f}
            data = {'command': 'importcustomsexcel'} # بدون _ وبدون s
            r = requests.post(SITE_URL, headers=headers, files=files, data=data)
            print(f"🌐 Website Sync: {r.status_code} - {r.text}")
            return "✅ تم الرفع" if r.status_code in [200, 201] else f"❌ فشل: {r.status_code}"
    except Exception as e:
        return f"❌ خطأ تقني: {e}"

def main():
    print(f"🚀 بدء التشغيل: {datetime.now()}")
    try:
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        
        # خطوة الرفع للموقع
        web_status = post_to_website(file_name)
        
        # تجهيز رسالة بسيطة لتجنب أخطاء التنسيق
        report = (
            f"Across MENA Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Site Status: {web_status}\n"
            f"Items Count: {len(df)}"
        )
        
        send_telegram(report, file_name)
        print("🏁 Done.")
    except Exception as e:
        print(f"❌ Main Error: {e}")
        send_telegram(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
