import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# إعدادات الأمان
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ACROSS_MENA_TOKEN = os.getenv("SITE_TOKEN")
ACROSS_MENA_API_URL = "https://across-mena.com/api/update-data"

def send_telegram_notification(message):
    """إرسال إشعار مختصر لتليجرام"""
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
    except Exception as e:
        print(f"Telegram Notification Error: {e}")

def sync_with_website(clean_data_list):
    """مزامنة الداتا مع الموقع"""
    if not ACROSS_MENA_TOKEN:
        return False, "⚠️ بانتظار توكن الموقع"
    
    headers = {"Authorization": f"Bearer {ACROSS_MENA_TOKEN}", "Content-Type": "application/json"}
    try:
        response = requests.post(ACROSS_MENA_API_URL, json=clean_data_list, headers=headers)
        if response.status_code in [200, 201]:
            return True, "✅ تم التحديث بنجاح"
        else:
            return False, f"⚠️ فشل المزامنة (كود {response.status_code})"
    except:
        return False, "❌ خطأ في الاتصال بالموقع"

def main():
    try:
        # 1. المعالجة
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        processor = DataProcessor()
        df_clean = processor.process_data(raw_data)
        
        # 2. تحديث الذاكرة
        df_clean.to_json('knowledge_base.json', orient='records', force_ascii=False)
        df_clean.to_excel("customs_ai_ready.xlsx", index=False)
        
        # 3. المزامنة
        web_status, status_msg = sync_with_website(df_clean.to_dict(orient='records'))
        
        # 4. إرسال الإشعار الصباحي فقط
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        report = (
            f"☀️ **تقرير Across MENA الصباحي**\n\n"
            f"📅 التاريخ: `{now}`\n"
            f"📊 حالة الموقع: {status_msg}\n"
            f"📦 عدد البنود المحدثة: {len(df_clean)}\n"
            f"🛠️ تم تحديث الذاكرة والملفات بنجاح."
        )
        send_telegram_notification(report)
        
    except Exception as e:
        send_telegram_notification(f"❌ حدث خطأ في النظام الصباحي:\n`{str(e)}`")

if __name__ == "__main__":
    main()
