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
    """رفع الملف للموقع مع انتظار طويل للمعالجة"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'command': 'import_customs_excel'}
            
            # ننتظر السيرفر حتى 5 دقائق (300 ثانية)
            response = requests.post(
                SITE_URL, 
                headers=headers, 
                files=files, 
                data=data,
                timeout=300 
            )
            
            print(f"🌐 Website Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح"
            else:
                return f"❌ فشل السيرفر: {response.status_code}"
                
    except requests.exceptions.Timeout:
        return "⏳ وقت مستقطع (السيرفر بطيء)"
    except Exception as e:
        return f"❌ خطأ اتصال: {str(e)[:30]}"

def main():
    print(f"🚀 بدء التحديث السريع: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات من السورس (Supabase)
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات (تنظيف وترتيب)
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # --- [تحسين الأداء لسرعة السيرفر] ---
        # حذف الأعمدة الفارغة تماماً (التي لا تحتوي على أي داتا) لتقليل حجم المعالجة
        initial_cols = len(df.columns)
        df = df.dropna(how='all', axis=1)
        
        # توحيد التنسيق لنصوص صافية لتسريع قراءة السيرفر للبيانات
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).replace('nan', '')

        file_name = "Across_MENA_Daily_Report.xlsx"
        
        # حفظ الملف بمحرك سريع وبدون تنسيقات معقدة
        df.to_excel(file_name, index=False, engine='openpyxl')
        
        file_size = os.path.getsize(file_name) / 1024
        print(f"💾 تم تجهيز ملف 'خفيف'. الحجم: {file_size:.2f} KB | الأعمدة: {len(df.columns)}")

        # 4. الرفع للموقع (المرحلة الحرجة)
        web_status = post_to_website(file_name)
        
        # 5. إرسال التقرير النهائي لتليجرام
        report = (
            f"Across MENA Speed Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Status: {web_status}\n"
            f"Processed: {len(df)} items\n"
            f"File Size: {file_size:.1f} KB"
        )
        
        send_telegram(report, file_name)
        print("🏁 تمت المهمة بنجاح.")

    except Exception as e:
        error_msg = f"❌ Main Error: {str(e)}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
