import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات - تأكد من وجودها في GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير والملف لتليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
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
    """إرسال الملف مع وضع الأمر في الرابط (Query Params)"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    # تعديل الرابط ليشمل الأمر المطلوب مباشرة
    final_url = f"{SITE_URL}?command=importcustomsexcel"
    
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # نرسل الملف تحت اسم الحقل 'file' مع تحديد نوع البيانات
            files = {
                'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            # تنفيذ طلب الـ POST
            response = requests.post(final_url, headers=headers, files=files)
            
            print(f"🌐 Website Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح"
            else:
                # نأخذ أول 30 حرف من الرد لنفهم سبب الرفض
                return f"❌ فشل: {response.status_code} ({response.text[:30]})"
    except Exception as e:
        return f"❌ خطأ تقني: {e}"

def main():
    print(f"🚀 بدء التحديث اليومي: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات من السورس
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات وتحضيرها
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. حفظ ملف الإكسل النهائي
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        print(f"💾 تم تجهيز الملف. العدد الإجمالي: {len(df)}")

        # 4. محاولة الرفع للموقع (POST)
        web_status = post_to_website(file_name)
        
        # 5. رسالة تليجرام
        report = (
            f"Across MENA Daily Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Site Status: {web_status}\n"
            f"Items Count: {len(df)}"
        )
        
        send_telegram(report, file_name)
        print("🏁 تمت المهمة.")

    except Exception as e:
        err = f"Main Error: {str(e)}"
        print(f"❌ {err}")
        send_telegram(err)

if __name__ == "__main__":
    main()
