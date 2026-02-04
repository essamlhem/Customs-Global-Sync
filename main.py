import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor
from Brain import AcrossMENABrain

# إعدادات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير مع طباعة النتيجة للتتبع"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ خطأ: BOT_TOKEN أو CHAT_ID مفقود!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                r = requests.post(url + "sendDocument", 
                                  data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, 
                                  files={'document': f})
        else:
            r = requests.post(url + "sendMessage", 
                              data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
        
        print(f"📡 Telegram Sync: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Telegram Exception: {str(e)}")

def post_to_website(file_path):
    """إرسال الملف للموقع مع الأمر المطلوب"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع مفقودة (URL/Token)"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'command': 'importcustomsexcel'}
            r = requests.post(SITE_URL, headers=headers, files=files, data=data)
            print(f"🌐 Website Sync: {r.status_code} - {r.text}")
            
            if r.status_code in [200, 201]:
                return "✅ تم الرفع للموقع بنجاح"
            return f"❌ فشل الرفع: {r.status_code}"
    except Exception as e:
        return f"❌ خطأ تقني بالربط: {str(e)}"

def main():
    print(f"🚀 بدء التشغيل: {datetime.now()}")
    try:
        # 1. جلب ومعالجة
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 2. حفظ
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        df.to_json('knowledge_base.json', orient='records', force_ascii=False)
        print(f"💾 تم حفظ الملفات. إجمالي المواد: {len(df)}")

        # 3. الرفع للموقع
        web_status = post_to_website(file_name)
        
        # 4. تجهيز التقرير
        brain = AcrossMENABrain()
        stats = brain.get_stats()
        
        report = (
            f"🚀 **تحديث Across MENA**\n"
            f"📅 التاريخ: `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"🌐 **حالة الموقع:** {web_status}\n"
            f"📦 **المواد:** `{len(df)}` بند\n"
        )
        
        if isinstance(stats, dict):
            sorted_cats = sorted(stats['categories_breakdown'].items(), key=lambda x: x[1], reverse=True)[:2]
            for cat, count in sorted_cats:
                report += f"• {cat}: `{count}`\n"
        
        # 5. الإرسال
        send_telegram(report, file_name)
        print("🏁 تمت المهمة بنجاح.")

    except Exception as e:
        error_msg = f"❌ خطأ عام: {str(e)}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
