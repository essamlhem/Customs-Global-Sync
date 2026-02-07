import pandas as pd
import requests
import os
import time
import json

# الإعدادات
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
BATCH_SIZE = 500 
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"

def upload_to_backend(df_batch, batch_num):
    # تحويل الدفعة إلى تنسيق JSON كما يطلبه السيرفر
    # records تجعل البيانات على شكل قائمة كائنات [{col1:val1}, {col2:val2}]
    json_data = df_batch.to_dict(orient='records')
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🚀 جاري رفع الدفعة رقم {batch_num} بصيغة JSON...")
        # إرسال البيانات كـ JSON body وليس كملف
        response = requests.post(UPLOAD_URL, json=json_data, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code} في الدفعة {batch_num}")
            print(f"💬 رد السيرفر: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل تقني: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return

    print("📂 جاري معالجة الملف وتحويله لـ JSON...")
    df = pd.read_excel(INPUT_FILE)

    # توحيد أسماء الأعمدة وحذف المطلوبة (material, note)
    df.columns = [str(c).lower().strip() for c in df.columns]
    for col in ['material', 'note']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"🗑️ حذف عمود: {col}")

    # معالجة القيم الفارغة (NaN) لأن JSON لا يقبلها
    df = df.fillna("")

    total_rows = len(df)
    print(f"📊 الإجمالي: {total_rows} سطر.")
    
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        upload_to_backend(batch_df, (i // BATCH_SIZE) + 1)
        time.sleep(2)

if __name__ == "__main__":
    main()
