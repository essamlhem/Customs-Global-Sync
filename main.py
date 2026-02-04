import os
import requests
import pandas as pd
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor
from Brain import AcrossMENABrain

# الإعدادات - يتم سحبها من GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    """إرسال التقرير والملف إلى تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if file_path:
            with open(file_path, 'rb') as f:
                requests.post(url + "sendDocument", 
                              data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, 
                              files={'document': f})
        else:
            requests.post(url + "sendMessage", 
                          data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})
    except Exception as e:
        print(f"Telegram Error: {e}")

def post_to_website(file_path):
    """إرسال ملف الإكسل للموقع مع الأمر المطلوب"""
    # نستخدم "Token" لأن المبرمج وضحه في السكريبت الخاص به
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            # الحقول المطلوبة للسيرفر بناءً على الخطأ السابق
            files = {'file': f}
            data = {'command': 'importcustomsexcel'} # هذا السطر لحل مشكلة Unknown command
            
            response = requests.post(SITE_URL, headers=headers, files=files, data=data)
            
            if response.status_code in [200, 201]:
                return f"✅ تم الرفع للموقع بنجاح"
            else:
                # نرجع تفاصيل الخطأ إذا فشل مرة أخرى
                return f"❌ فشل الرفع: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"❌ خطأ تقني في الربط: {str(e)}"

def main():
    try:
        # 1. جلب البيانات من Supabase
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        # 2. معالجة البيانات (تنظيف، HS Code، روابط صور)
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # 3. حفظ الملفات (Excel و JSON للذاكرة)
        file_name = "Across_MENA_Daily_Report.xlsx"
        df.to_excel(file_name, index=False)
        df.to_json('knowledge_base.json', orient='records', force_ascii=False)
        
        # 4. تحليل البيانات عبر الـ Brain (اختياري للتقرير)
        brain = AcrossMENABrain()
        stats = brain.get_stats()
        
        # 5. محاولة الرفع للموقع (POST)
        web_status = post_to_website(file_name)
        
        # 6. تجهيز رسالة التقرير النهائي
        report = (
            f"🚀 **تحديث Across MENA الذكي**\n"
            f"📅 التاريخ: `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"🌐 **حالة الموقع:** {web_status}\n"
            f"📦 **إجمالي المواد:** `{len(df)}` بند\n"
            f"🧠 **أهم التصنيفات:**\n"
        )
        
        # إضافة أهم تصنيفين من الـ Brain للتقرير
        if isinstance(stats, dict):
            sorted_cats = sorted(stats['categories_breakdown'].items(), key=lambda x: x[1], reverse=True)[:2]
            for cat, count in sorted_cats:
                report += f"• {cat}: `{count}` بند\n"
        
        report += "\n👇 الملف المرفق يحتوي على كافة البيانات المحدثة."
        
        # 7. الإرسال لتليجرام
        send_telegram(report, file_name)

    except Exception as e:
        send_telegram(f"❌ خطأ عام في النظام: {str(e)}")

if __name__ == "__main__":
    main()
