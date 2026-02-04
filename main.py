import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_to_telegram_with_file(message, file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            payload = {'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}
            files = {'document': f}
            requests.post(url, data=payload, files=files)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def main():
    try:
        # جلب ومعالجة البيانات
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # حفظ الملفين
        excel_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(excel_name, index=False)
        df.to_json('knowledge_base.json', orient='records', force_ascii=False)
        
        # إحصائيات الصور
        total = len(df)
        with_img = df[df['image_search_link'] != ""].shape[0]
        
        # رسالة التقرير
        report_msg = (
            f"☀️ **تقرير Across MENA للمطابقة**\n"
            f"📅 التاريخ: `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"✅ إجمالي المواد: `{total}`\n"
            f"🖼️ مواد بروابط صور: `{with_img}`\n"
            f"⚠️ مواد مفقودة: `{total - with_img}`\n\n"
            f"📌 افتح ملف الإكسل المرفق لمراجعة دقة الصور عبر الروابط."
        )
        
        # تنفيذ الإرسال
        send_to_telegram_with_file(report_msg, excel_name)
        
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': f"❌ خطأ في السيستم: {str(e)}"})

if __name__ == "__main__":
    main()
