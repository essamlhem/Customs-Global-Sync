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

def send_telegram(message, file_path=None):
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
    headers = {"Authorization": f"Token {SITE_TOKEN}"}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            data = {'command': 'import_customs_excel'}
            response = requests.post(SITE_URL, headers=headers, files=files, data=data, timeout=600)
            return "✅ تم الرفع بنجاح" if response.status_code in [200, 201] else f"❌ فشل: {response.status_code}"
    except Exception as e:
        return f"❌ خطأ اتصال: {str(e)[:30]}"

def main():
    try:
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        if not raw_data:
            send_telegram("☕ صباح الخير عيسى. لا يوجد تحديثات.")
            return

        df = DataProcessor().process_data(raw_data)
        
        # --- [ تعديلات الأعمدة والطلبات الخاصة ] ---
        
        # 1. إضافة عمود المرجع (HS Code Link)
        # الموقع اللي بعتته بيستخدم الـ HS Code في الرابط للبحث
        # الرابط المباشر بكون بهاد الشكل: https://globaltradehelpdesk.org/ar/resources/search-hs-code?code=123456
        if 'hs_code' in df.columns:
            df['HS_Reference_Link'] = df['hs_code'].apply(
                lambda x: f"https://globaltradehelpdesk.org/ar/resources/search-hs-code?code={str(x).replace('.', '')}" if pd.notnull(x) else ""
            )

        # 2. حذف الأعمدة اللي طلبتها (الماتريال والـ Note)
        cols_to_drop = ['material', 'note', 'band-material', 'band_material'] 
        existing_drops = [c for c in cols_to_drop if c in df.columns]
        df = df.drop(columns=existing_drops)
        
        # 3. حفظ كـ CSV
        file_name = "Across_MENA_With_Reference.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        # 4. الرفع للموقع والتقرير
        web_status = post_to_website(file_name)
        report = (
            f"📢 تقرير التحديث (نسخة المرجع)\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔹 الوضع: {web_status}\n"
            f"🔹 المواد: {len(df)}\n"
            f"🔹 تم إضافة مرجع: Global Trade Helpdesk\n"
            f"🔹 تم حذف: Material & Note"
        )
        
        send_telegram(report, file_name)
        if os.path.exists(file_name): os.remove(file_name)

    except Exception as e:
        send_telegram(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    main()
