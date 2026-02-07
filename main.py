import pandas as pd
import requests
import os
import time

# الإعدادات
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
BATCH_SIZE = 500 
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"

def upload_to_backend(df_batch, batch_num):
    # تحويل الدفعة لقائمة كائنات
    records = df_batch.to_dict(orient='records')
    
    # 🔑 هاد هو التعديل السحري: تغليف البيانات بكلمة items
    payload = {
        "items": records
    }
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 جاري رفع الدفعة {batch_num} (تحتوي على {len(records)} بند)...")
        response = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} وصلت وتفككت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code}")
            print(f"💬 رد السيرفر: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل تقني: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} مفقود!")
        return

    print("📂 جاري تجهيز البيانات بنظام الـ Items...")
    df = pd.read_excel(INPUT_FILE)

    # تنظيف الأعمدة (حذف material و note)
    df.columns = [str(c).lower().strip() for c in df.columns]
    for col in ['material', 'note']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"🗑️ حذف عمود: {col}")

    # معالجة الفراغات لضمان قبول السيرفر
    df = df.fillna("")

    total_rows = len(df)
    print(f"📊 إجمالي الأسطر: {total_rows}")
    
    # الرفع على دفعات
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        upload_to_backend(batch_df, (i // BATCH_SIZE) + 1)
        time.sleep(1.5)

if __name__ == "__main__":
    main()
