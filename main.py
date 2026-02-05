import os
import requests
import pandas as pd
import json # لإضافة تنسيق المصفوفة (Array)
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

# الإعدادات
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SITE_URL = os.getenv("SITE_URL")
SITE_TOKEN = os.getenv("SITE_TOKEN")

def send_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                requests.post(url + "sendDocument", data={'chat_id': CHAT_ID, 'caption': message}, files={'document': f})
        else:
            requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message})
    except Exception as e: print(f"❌ Telegram Error: {e}")

def post_to_website(file_path):
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'}
            response = requests.post(SITE_URL, headers=headers, files=files, data=data, timeout=600)
            return "✅ تم الرفع بنجاح" if response.status_code in [200, 201] else f"❌ فشل: {response.status_code}"
    except Exception as e: return f"❌ خطأ اتصال: {str(e)[:30]}"

def main():
    print(f"🚀 بدء التحديث (نظام مصفوفة الصور): {datetime.now().strftime('%H:%M')}")
    try:
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        if not raw_data:
            send_telegram("☕ صباح الخير عيسى. لا توجد تحديثات اليوم.")
            return

        processor = DataProcessor()
        df = processor.process_data(raw_data)

        # --- [ تعديل الصور لتصبح مصفوفة ] ---
        
        # إذا كان الـ Processor بيعطينا لستة روابط صور في عمود 'image_links'
        if 'image_links' in df.columns:
            # نأخذ أول 6 صور فقط ونحولها لنص بتنسيق مصفوفة JSON [link1, link2, ...]
            df['image'] = df['image_links'].apply(
                lambda x: json.dumps(x[:6]) if isinstance(x, list) else json.dumps([])
            )
        else:
            # إذا ما في روابط صور جاهزة، بنعمل عمود فاضي بتنسيق مصفوفة
            df['image'] = "[]"

        # --- [ تنظيف الملف للموقع ] ---

        # حذف الأعمدة اللي ما بدو إياها المدير (المرجع، الماتريال، النوت)
        cols_to_drop = [
            'material', 'note', 'band-material', 'band_material', 
            'HS_Reference_Link', 'image_search_link', 'image_links'
        ] 
        existing_drops = [c for c in cols_to_drop if c in df.columns]
        df_site = df.drop(columns=existing_drops)

        # حفظ كـ CSV للموقع
        file_name = "Across_MENA_Array_Images.csv"
        df_site.to_csv(file_name, index=False, encoding='utf-8-sig')

        # الرفع والتقرير
        web_status = post_to_website(file_name)
        report = (
            f"📢 تحديث Across MENA (تنسيق المصفوفة)\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔹 الوضع: {web_status}\n"
            f"🔹 المواد: {len(df_site)}\n"
            f"🔹 الصور: تم دمج 6 روابط في مصفوفة واحدة داخل عمود image\n"
            f"🔹 المرجع: محذوف بناءً على طلب المدير"
        )
        
        send_telegram(report, file_name)
        if os.path.exists(file_name): os.remove(file_name)

    except Exception as e:
        send_telegram(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    main()
