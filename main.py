import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات من GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير والملف لتليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    # تنظيف الرسالة من الرموز التي قد تسبب مشاكل في تليجرام
    clean_message = message.replace("_", " ").replace("*", "")
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                requests.post(url + "sendDocument", 
                              data={'chat_id': CHAT_ID, 'caption': clean_message}, 
                              files={'document': f})
        else:
            requests.post(url + "sendMessage", 
                          data={'chat_id': CHAT_ID, 'text': clean_message})
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def post_to_website(file_path):
    """رفع ملف CSV للموقع مع معالجة الوقت"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    
    try:
        with open(file_path, 'rb') as f:
            # إرسال الملف بصيغة CSV لتقليل الحجم وتسريع المعالجة
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'}
            
            # وقت انتظار طويل (5 دقائق) لضمان انتهاء السيرفر من المعالجة
            response = requests.post(
                SITE_URL, 
                headers=headers, 
                files=files, 
                data=data,
                timeout=300 
            )
            
            print(f"🌐 Website Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح (CSV)"
            else:
                return f"❌ فشل السيرفر: {response.status_code}"
                
    except requests.exceptions.Timeout:
        return "⏳ وقت مستقطع (السيرفر بطيء)"
    except Exception as e:
        return f"❌ خطأ اتصال: {str(e)[:40]}"

def main():
    print(f"🚀 بدء التحديث بصيغة CSV: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات من السورس (Supabase)
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات وتحويلها لـ DataFrame
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. حفظ البيانات كـ CSV (أخف بـ 60% من الإكسل وأسرع في القراءة)
        # استخدام utf-8-sig لضمان دعم اللغة العربية في إكسل والموقع
        file_name = "Across_MENA_Data.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        file_size = os.path.getsize(file_name) / 1024
        print(f"💾 تم تجهيز CSV. الحجم: {file_size:.2f} KB | المواد: {len(df)}")

        # 4. محاولة الرفع للموقع (ملف واحد كامل)
        web_status = post_to_website(file_name)
        
        # 5. إرسال التقرير النهائي لتليجرام
        report = (
            f"Across MENA CSV Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Status: {web_status}\n"
            f"Items Count: {len(df)}\n"
            f"File Size: {file_size:.1f} KB"
        )
        
        send_telegram(report, file_name)
        print("🏁 تمت المهمة بنجاح.")

    except Exception as e:
        err_msg = f"❌ Main Error: {str(e)}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
