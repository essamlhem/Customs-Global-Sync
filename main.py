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
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'}
            response = requests.post(SITE_URL, headers=headers, files=files, data=data, timeout=600)
            return "✅ تم التحديث بنجاح" if response.status_code in [200, 201] else f"❌ فشل: {response.status_code}"
    except Exception as e: return f"❌ خطأ اتصال: {str(e)[:30]}"

def main():
    print(f"🚀 بدء الفحص اليومي: {datetime.now().strftime('%H:%M')}")
    try:
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # إذا كانت البيانات فارغة أو لا يوجد تحديث (حسب منطق السكرابر عندك)
        if not raw_data or len(raw_data) == 0:
            send_telegram("☕ صباح الخير عيسى. فحصت السوبابيس اليوم وما لقيت أي تحديثات جديدة، لهيك ما رفعنا شي عالموقع.")
            return

        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # حفظ الملف CSV
        file_name = "Across_MENA_Full_Data.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        # الرفع للموقع
        web_status = post_to_website(file_name)
        
        # التقرير اليومي
        report = (
            f"📢 تقرير التحديث اليومي\n"
            f"الوضع: {web_status}\n"
            f"عدد المواد المرفوعة: {len(df)}\n"
            f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"
        )
        send_telegram(report, file_name)

    except Exception as e:
        send_telegram(f"❌ خطأ في النظام: {str(e)}")

if __name__ == "__main__":
    main()
