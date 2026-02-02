import requests
import pandas as pd
import os
import json
from datetime import datetime

# استلام المفاتيح من الـ Secrets (تأكد إنك ضفتهم بالإعدادات بنفس الأسماء)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

def send_telegram(message=None, file_path=None, caption=None):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            requests.post(url + "sendDocument", data={'chat_id': CHAT_ID, 'caption': caption}, files={'document': f})
    elif message:
        requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message})

def run_sync():
    api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
    headers = {'apikey': SUPABASE_KEY.strip(), 'Authorization': f'Bearer {SUPABASE_KEY.strip()}'}
    
    try:
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            new_data = res.json()
            sync_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            file_json = "knowledge_base.json"
            
            # منطق المقارنة الذكي
            is_updated = True
            if os.path.exists(file_json):
                with open(file_json, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    if len(old_data) == len(new_data):
                        is_updated = False

            if is_updated:
                # تجهيز ملف الإكسل
                df = pd.DataFrame(new_data)
                excel_file = "customs_data.xlsx"
                df.to_excel(excel_file, index=False)
                
                # حفظ النسخة الجديدة للمقارنة القادمة
                with open(file_json, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False)

                send_telegram(message=f"🚀 تم تشغيل النظام بنجاح!\n📦 عدد السجلات: {len(new_data)}")
                send_telegram(file_path=excel_file, caption=f"📊 ملف البيانات | {sync_time}")
            else:
                send_telegram(message=f"✅ فحص دوري: لا يوجد تحديثات جديدة.\n📦 عدد المنتجات: {len(new_data)}\n⏰ {sync_time}")
    except Exception as e:
        send_telegram(message=f"❌ خطأ فني: {str(e)}")

if __name__ == "__main__":
    run_sync()
