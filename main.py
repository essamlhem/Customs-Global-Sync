import pandas as pd
import requests
import os
import time

# --- الإعدادات ---
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "customs_global_brain_translated.xlsx" 
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"
BATCH_SIZE = 500 

def upload_to_backend(df_batch, batch_num):
    # تحويل الدفعة لقاموس (Records)
    records = df_batch.to_dict(orient='records')
    payload = {"items": records}
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 جاري تحديث الدفعة {batch_num} (إضافة الأعمدة الإنجليزية)...")
        # استخدام timeout عالي لضمان المعالجة
        response = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=120)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} تم تحديثها بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code} | الرد: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل الاتصال أثناء التحديث: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return

    print(f"📂 جاري تجهيز البيانات لتعبئة name_en و item_type_en...")
    df = pd.read_excel(INPUT_FILE)

    # 1. تنظيف أسماء الأعمدة
    df.columns = [str(c).strip() for c in df.columns]

    # 2. التأكد من وجود الأعمدة المطلوبة
    cols_to_fix = ['band', 'name_en', 'item_type_en']
    for col in cols_to_fix:
        if col not in df.columns:
            print(f"⚠️ تحذير: العمود {col} غير موجود بالملف!")

    # 3. إصلاح الأصفار للأعمدة الأساسية (مشان السيرفر يعرف يطابق البيانات)
    for col in ['band', 'band_syria']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(8)

    # 4. معالجة القيم الفارغة (تحويلها لنصوص فاضية بدل Null)
    df = df.fillna("")

    total_rows = len(df)
    
    # 5. البدء بالرفع بنظام المجموعات
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        time.sleep(2) # استراحة للسيرفر

    print("\n🎉 انتهت عملية تعبئة البيانات الناقصة بنجاح يا أستاذ عيسى.")

if __name__ == "__main__":
    main()
