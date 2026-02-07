import pandas as pd
import requests
import os
import time
import json

# الإعدادات
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
BATCH_SIZE = 500  # جرب تصغرها لـ 100 لو استمر الخطأ 500
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"

def upload_to_backend(df_batch, batch_num):
    # تحويل البيانات لـ JSON Records
    json_data = df_batch.to_dict(orient='records')
    
    # تحويل أي قيم غير مدعومة (مثل التواريخ أو الأرقام الغريبة) لنصوص صافية
    clean_json = json.loads(json.dumps(json_data, default=str))

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"🚀 رفع الدفعة {batch_num}...")
        # طباعة عينة من البيانات المرسلة للتأكد (أول سطر فقط)
        print(f"📝 عينة من البيانات: {clean_json[0]}")
        
        response = requests.post(UPLOAD_URL, json=clean_json, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
        else:
            print(f"❌ خطأ {response.status_code}")
            print(f"💬 الرد: {response.text[:500]}") # طباعة أول 500 حرف من الخطأ
                
    except Exception as e:
        print(f"❌ فشل: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف مفقود!")
        return

    df = pd.read_excel(INPUT_FILE)

    # حذف material و note
    # ملاحظة: إذا الباك إيند بيطلب أعمدة معينة بالاسم، لازم تتطابق بالظبط
    df.columns = [str(c).strip() for c in df.columns] # خليهم مثل ما هن بدون lower
    
    cols_to_drop = []
    for c in ['material', 'note', 'Material', 'Note']:
        if c in df.columns: cols_to_drop.append(c)
    
    df.drop(columns=cols_to_drop, inplace=True)
    print(f"🗑️ تم تنظيف الأعمدة: {cols_to_drop}")

    # تحويل كل القيم لـ String عشان نتفادى خطأ الـ 500 في السيرفر
    df = df.astype(str).replace('nan', '')

    total_rows = len(df)
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        upload_to_backend(batch_df, (i // BATCH_SIZE) + 1)
        time.sleep(2)

if __name__ == "__main__":
    main()
