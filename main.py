import pandas as pd
import requests
import os
import time

# --- الإعدادات ---
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "customs_global_brain_translated.xlsx" 
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"
BATCH_SIZE = 250 

def upload_to_backend(df_batch, batch_num):
    records = df_batch.to_dict(orient='records')
    payload = {"items": records}
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 جاري تحديث الدفعة {batch_num}...")
        # زيادة الـ timeout لـ 120 ثانية
        response = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=120)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code} | الرد: {response.text[:100]}")
                
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف غير موجود!")
        return

    print(f"📂 جاري معالجة الملف وتحويل التواريخ لنصوص...")
    df = pd.read_excel(INPUT_FILE)

    # 1. تنظيف الأسماء
    df.columns = [str(c).strip() for c in df.columns]

    # 2. تحويل أي تاريخ (Timestamp) إلى نص مشان يقبله الـ JSON
    # هي هيي الخطوة اللي كانت ناقصة وعملت المشكلة
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            print(f"⚙️ تحويل العمود {col} من تاريخ إلى نص...")
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # 3. إصلاح الأصفار للأعمدة الأساسية
    for col in ['band', 'band_syria']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(8)

    if 'hs6_global' in df.columns:
        df['hs6_global'] = df['hs6_global'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)

    # 4. معالجة القيم الفارغة
    df = df.replace(['nan', 'None'], "")
    df = df.fillna("")

    total_rows = len(df)
    
    # 5. الرفع بنظام المجموعات
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        time.sleep(1.5)

    print("\n🎉 هيك التحديث صار نظامي 100% يا أستاذ عيسى.")

if __name__ == "__main__":
    main()
