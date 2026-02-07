import pandas as pd
import requests
import os
import time

# --- الإعدادات ---
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "customs_global_brain (6).xlsx" 
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"
BATCH_SIZE = 500 

def upload_to_backend(df_batch, batch_num):
    # تحويل الدفعة لقائمة كائنات كما هي تماماً في الملف
    records = df_batch.to_dict(orient='records')
    
    # تغليف البيانات في حقل items حسب طلب السيرفر
    payload = {"items": records}
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 رفع الدفعة {batch_num} ({len(records)} سطر)...")
        response = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} اكتملت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code} | الرد: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود! تأكد من رفعه بنفس الاسم.")
        return

    print(f"📂 جاري قراءة الملف ورفعه بأسماء الأعمدة الأصلية...")
    # قراءة الملف
    df = pd.read_excel(INPUT_FILE)

    # تنظيف أسماء الأعمدة من أي مسافات مخفية فقط (بدون تغيير الأسماء)
    df.columns = [str(c).strip() for c in df.columns]

    # معالجة القيم الفارغة (مهمة جداً لنجاح الـ JSON)
    df = df.fillna("")

    total_rows = len(df)
    print(f"📊 إجمالي الأسطر الجاهزة: {total_rows}")
    
    # الرفع بنظام المجموعات (Batches)
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        
        # استراحة بسيطة للسيرفر
        time.sleep(1.5)

if __name__ == "__main__":
    main()
