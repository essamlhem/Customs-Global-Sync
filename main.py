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
    """إرسال رسائل وتقارير لتليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                requests.post(url + "sendDocument", 
                              data={'chat_id': CHAT_ID, 'caption': message}, 
                              files={'document': f})
        else:
            requests.post(url + "sendMessage", 
                          data={'chat_id': CHAT_ID, 'text': message})
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def post_to_website(file_path):
    """رفع الملف للموقع بصيغة CSV"""
    if not SITE_URL or not SITE_TOKEN:
        return "⚠️ بيانات الموقع ناقصة"

    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # إرسال كـ CSV لضمان السرعة والتوافق الجديد مع السيرفر
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'}
            
            # انتظار حتى 10 دقائق للمعالجة
            response = requests.post(
                SITE_URL, 
                headers=headers, 
                files=files, 
                data=data,
                timeout=600 
            )
            
            if response.status_code in [200, 201]:
                return "✅ تم تحديث الموقع بنجاح"
            else:
                return f"❌ فشل تحديث الموقع: {response.status_code}"
    except Exception as e:
        return f"❌ خطأ اتصال بالموقع: {str(e)[:30]}"

def main():
    print(f"🚀 بدء التشغيل اليومي: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        # 1. جلب البيانات من Supabase
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. فحص إذا كانت البيانات فارغة (منطق عدم وجود تحديث)
        if not raw_data or len(raw_data) == 0:
            msg = "☕ صباح الخير عيسى. فحصت البيانات اليوم وما لقيت أي تحديثات جديدة في Supabase، لهيك ما رفعنا شي للموقع اليوم."
            send_telegram(msg)
            print("💤 لا يوجد تحديثات اليوم.")
            return

        # 3. إذا وجدت بيانات، ابدأ المعالجة
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 4. حفظ البيانات كاملة كـ CSV
        file_name = "Across_MENA_Full_Data.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        # 5. الرفع للموقع
        web_status = post_to_website(file_name)
        
        # 6. التقرير اليومي الكامل لتليجرام
        report = (
            f"📢 تقرير التحديث اليومي لـ Across MENA\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔹 الوضع: {web_status}\n"
            f"🔹 عدد المواد: {len(df)}\n"
            f"🔹 الصيغة: CSV الكاملة\n"
            f"🔹 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━"
        )
        
        send_telegram(report, file_name)
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_name):
            os.remove(file_name)
            
        print("🏁 تمت المهمة بنجاح.")

    except Exception as e:
        err_msg = f"❌ خطأ في النظام: {str(e)}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
