import os
import json
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_to_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    if file_path:
        with open(file_path, 'rb') as f:
            requests.post(url + "sendDocument", data={'chat_id': CHAT_ID, 'caption': message}, files={'document': f})
    else:
        requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message})

def main():
    try:
        # 1. جلب البيانات
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة وتنظيف البيانات (من الملف المنفصل)
        processor = DataProcessor()
        df_clean = processor.process_data(raw_data)
        
        # 3. حفظ النتائج
        output_file = "customs_ai_ready.xlsx"
        df_clean.to_excel(output_file, index=False)
        
        with open("knowledge_base.json", "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False)
            
        # 4. إرسال التقرير
        sync_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        send_to_telegram(f"✅ نظام Across MENA المطور:\nتمت المزامنة والمعالجة بنجاح.\n⏰ {sync_time}", output_file)
        
    except Exception as e:
        send_to_telegram(f"❌ خطأ في النظام: {str(e)}")

if __name__ == "__main__":
    main()
