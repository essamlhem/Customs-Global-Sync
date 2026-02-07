import os
import pandas as pd
import hashlib
import requests
from Scraper import SupabaseScraper

# ⚠️ إعدادات التلغرام الخاصة بك
TELEGRAM_TOKEN = "7504938628:AAGm5lwvdJ1bqiqBKFafXUXxR8pbWQZjWnw"
TELEGRAM_CHAT_ID = "460803708"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        print("❌ فشل إرسال رسالة تلغرام")

def main():
    scraper = SupabaseScraper()
    df_new = scraper.fetch_all_as_dataframe()
    
    if df_new is not None:
        file_name = "Across_MENA_Full_Data.csv"
        hash_file = "data_hash.txt"
        
        # 1. إنشاء بصمة فريدة للبيانات الحالية للمقارنة
        # نستخدم JSON String لضمان أن المقارنة دقيقة للمحتوى
        current_hash = hashlib.md5(df_new.to_json().encode('utf-8')).hexdigest()
        
        # 2. قراءة البصمة القديمة (إذا وجدت)
        last_hash = ""
        if os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                last_hash = f.read().strip()

        # 3. المقارنة واتخاذ الإجراء
        if current_hash == last_hash:
            # لا يوجد أي تغيير
            status_msg = "📅 تقرير الصباح: تم فحص الموقع بنجاح. لا توجد أي تعديلات أو بيانات جديدة اليوم. الحالة: مستقرة ✅"
            print("✅ لا توجد تعديلات.")
        else:
            # هناك بيانات جديدة أو تعديلات
            print("⚠️ تم رصد تحديث!")
            # حفظ الملف الجديد بصيغة CSV شاملة
            df_new.to_csv(file_name, index=False, encoding='utf-8-sig')
            
            # تحديث ملف البصمة
            with open(hash_file, "w") as f:
                f.write(current_hash)
            
            status_msg = f"🔔 تنبيه يا عيسى: تم رصد تحديث جديد في البيانات!\n📦 إجمالي المنتجات حالياً: {len(df_new)}\n📁 تم تحديث الملف الشامل Across_MENA_Full_Data.csv بنجاح."

        # 4. إرسال التقرير النهائي لعيسى
        send_telegram_msg(status_msg)
    else:
        send_telegram_msg("⚠️ خطأ صباحي: السكريبت لم يتمكن من الوصول لبيانات الموقع. يرجى التأكد من الـ API Key.")

if __name__ == "__main__":
    main()
