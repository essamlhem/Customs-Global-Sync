import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات - تأكد من مطابقتها للأسماء في GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير والملف لتليجرام بنص نظيف"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    # تنظيف النص من الرموز التي قد تعطل تليجرام
    clean_message = message.replace("_", " ").replace("*", "")
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                r = requests.post(url + "sendDocument", 
                                  data={'chat_id': CHAT_ID, 'caption': clean_message}, 
                                  files={'document': f})
        else:
            r = requests.post(url + "sendMessage", 
                              data={'chat_id': CHAT_ID, 'text': clean_message})
        print(f"📡 Telegram Response: {r.status_code}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def post_to_website(file_path):
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # إرسال الملف والأمر في طلب POST واحد
            files = {
                'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            # هذا هو الاحتمال الأكبر لنجاح الطلب بناءً على الخطأ السابق
            data = {'command': 'import_customs_excel'}
            
            response = requests.post(SITE_URL, headers=headers, files=files, data=data)
            
            print(f"🌐 Website Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح"
            else:
                # نرسل جزءاً من رد السيرفر لنعرف إذا كان لا يزال يرفض الأمر
                return f"❌ فشل: {response.status_code} ({response.text[:30]})"
    except Exception as e:
        return f"❌ خطأ تقني: {e}"

def main():
    print(f"🚀 بدء التحديث اليومي: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات وتحويلها لإكسل
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. حفظ ملف الإكسل
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        print(f"💾 تم تجهيز الملف. العدد: {len(df)}")

        # 4. الرفع للموقع (المرحلة الحاسمة)
        web_status = post_to_website(file_name)
        
        # 5. تجهيز تقرير تليجرام
        report = (
            f"Across MENA Daily Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Site Status: {web_status}\n"
            f"Items Count: {len(df)}"
        )
        
        # 6. الإرسال النهائي
        send_telegram(report, file_name)
        print("🏁 العملية اكتملت.")

    except Exception as e:
        err = f"Main Error: {str(e)}"
        print(f"❌ {err}")
        send_telegram(err)

if __name__ == "__main__":
    main()
