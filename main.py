import os
import requests
import pandas as pd
from datetime import datetime
import time
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات من GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير لتليجرام"""
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
    """رفع ملف صغير (Chunk) للموقع"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'command': 'import_customs_excel'}
            
            response = requests.post(
                SITE_URL, 
                headers=headers, 
                files=files, 
                data=data,
                timeout=120 # وقت كافٍ لملف صغير
            )
            
            if response.status_code in [200, 201]:
                return "✅ نجاح"
            else:
                return f"❌ فشل ({response.status_code})"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

def main():
    print(f"🚀 بدء التحديث بنظام الدفعات: {datetime.now().strftime('%H:%M:%S')}")
    try:
        # 1. جلب البيانات
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. تقسيم البيانات (كل دفعة 1000 مادة)
        chunk_size = 1000
        total_rows = len(df)
        chunks = [df[i:i + chunk_size] for i in range(0, total_rows, chunk_size)]
        
        print(f"📦 إجمالي المواد: {total_rows} | عدد الدفعات: {len(chunks)}")

        success_count = 0
        for idx, chunk_df in enumerate(chunks):
            chunk_file = f"chunk_{idx+1}.xlsx"
            # حفظ الدفعة كملف إكسل مؤقت
            chunk_df.to_excel(chunk_file, index=False, engine='openpyxl')
            
            print(f"📤 رفع الدفعة {idx+1}/{len(chunks)}...")
            status = post_to_website(chunk_file)
            
            if "✅" in status:
                success_count += 1
                print(f"✅ الدفعة {idx+1} اكتملت.")
            else:
                print(f"❌ الدفعة {idx+1} فشلت: {status}")
            
            # حذف الملف المؤقت فوراً
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
            
            # انتظار بسيط بين الدفعات لراحة السيرفر
            time.sleep(2)

        # 4. التقرير النهائي
        final_result = "✅ الكل تم بنجاح" if success_count == len(chunks) else f"⚠️ تم رفع {success_count}/{len(chunks)}"
        
        report = (
            f"Across MENA Batch Update\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"Final Status: {final_result}\n"
            f"Total Items: {total_rows}\n"
            f"Chunks Processed: {len(chunks)}"
        )
        
        send_telegram(report)
        print("🏁 انتهت العملية.")

    except Exception as e:
        err = f"❌ Main Error: {str(e)}"
        print(err)
        send_telegram(err)

if __name__ == "__main__":
    main()
