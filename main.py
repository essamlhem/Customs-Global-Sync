import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات من GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = "https://across-mena.com/customs/upload-excel/"
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    if file_path:
        with open(file_path, 'rb') as f:
            requests.post(url + "sendDocument", data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'document': f})
    else:
        requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})

def post_to_website(file_path):
    """إرسال ملف الإكسل عبر POST طلب للموقع"""
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # 'file' هو اسم الحقل الذي يتوقعه السيرفر عادةً في طلبات الـ POST للملفات
            files = {'file': f}
            response = requests.post(SITE_URL, headers=headers, files=files)
            
            if response.status_code in [200, 201]:
                return f"✅ تم الرفع للموقع بنجاح (Status: {response.status_code})"
            else:
                return f"❌ فشل الرفع للموقع: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"❌ خطأ تقني في الإرسال للموقع: {str(e)}"

def main():
    try:
        # 1. جلب البيانات ومعالجتها
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 2. حفظ النسخة اليومية الأحدث
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        df.to_json('knowledge_base.json', orient='records', force_ascii=False)
        
        # 3. إرسال ملف الإكسل للموقع (الخطوة الجديدة)
        web_status = post_to_website(file_name)
        
        # 4. إرسال التقرير النهائي لك على تليجرام
        report = (
            f"🚀 **تحديث Across MENA اليومي**\n"
            f"📅 التاريخ: `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"🌍 حالة الموقع: {web_status}\n"
            f"📦 إجمالي البنود: `{len(df)}`"
        )
        send_telegram(report, file_name)

    except Exception as e:
        send_telegram(f"❌ خطأ عام: {str(e)}")

if __name__ == "__main__":
    main()
