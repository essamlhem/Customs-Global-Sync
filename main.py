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

def post_to_website(file_path):
    """رفع ملف CSV مضغوط للموقع"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    
    try:
        with open(file_path, 'rb') as f:
            # نرسل الملف تحت مفتاح 'file' كما هو مطلوب
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'} # المبرمج غالباً ما غير اسم الكوماند
            
            response = requests.post(
                SITE_URL, 
                headers=headers, 
                files=files, 
                data=data,
                timeout=300 
            )
            
            if response.status_code in [200, 201]:
                return "✅ تم الرفع بنجاح (CSV)"
            else:
                return f"❌ فشل: {response.status_code} - {response.text[:50]}"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

def main():
    print(f"🚀 بدء التحديث بصيغة CSV: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. حفظ كـ CSV (أخف وأسرع بكثير)
        file_name = "Across_MENA_Data.csv"
        # نستخدم utf-8-sig عشان يدعم العربي بدون مشاكل
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        file_size = os.path.getsize(file_name) / 1024
        print(f"💾 تم تجهيز CSV. الحجم: {file_size:.2f} KB")

        # 4. الرفع للموقع
        web_status = post_to_website(file_name)
        
        # 5. التقرير
        report = (
            f"Across MENA CSV Update\n"
            f"Status: {web_status}\n"
            f"Items: {len(df)}\n"
            f"Size: {file_size:.1f} KB"
        )
        
        # إرسال التقرير مع الملف للتليجرام (عشان تشيك عليه)
        from main import send_telegram # تأكد أن الدالة معرفة فوق
        send_telegram(report, file_name)
        print("🏁 انتهت العملية.")

    except Exception as e:
        print(f"❌ Main Error: {e}")

if __name__ == "__main__":
    main()
