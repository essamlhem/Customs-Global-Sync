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
    records = df_batch.to_dict(orient='records')
    payload = {"items": records}
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 رفع الدفعة {batch_num} ({len(records)} سطر)...")
        response = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code} | الرد: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return

    print(f"📂 جاري معالجة الملف وإصلاح الأصفار على اليسار...")
    df = pd.read_excel(INPUT_FILE)

    # 1. تنظيف أسماء الأعمدة من المسافات
    df.columns = [str(c).strip() for c in df.columns]

    # 2. إصلاح الأعمدة بإضافة أصفار على اليسار (Padding)
    # band و band_syria لازم يكونوا 8 خانات (إذا 7 حط صفر)
    # hs6_global لازم يكون 6 خانات (إذا 5 حط صفر)
    
    for col in ['band', 'band_syria']:
        if col in df.columns:
            # تحويل لنص، تعبئة الخانات لـ 8 بوضع أصفار يساراً
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(8)

    if 'hs6_global' in df.columns:
        # تحويل لنص، تعبئة الخانات لـ 6 بوضع أصفار يساراً
        df['hs6_global'] = df['hs6_global'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)

    # 3. معالجة القيم الفارغة (التي أصبحت "nan" بعد التحويل)
    df = df.replace(['nan', 'None'], "")
    df = df.fillna("")

    total_rows = len(df)
    print(f"📊 عينة بعد الإصلاح (أول 3 أسطر):")
    # طباعة عينة للتأكد من الأصفار في الـ Logs
    print(df[['band', 'band_syria', 'hs6_global']].head(3))
    
    # 4. الرفع بنظام المجموعات
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        time.sleep(1.5)

if __name__ == "__main__":
    main()
