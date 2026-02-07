import pandas as pd
import requests
import os
import time

# --- الإعدادات المحدثة ---
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "customs_global_brain (6).xlsx" # تم تعديل اسم الملف هنا
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"
BATCH_SIZE = 500 

def upload_to_backend(df_batch, batch_num):
    # تحويل الدفعة لقائمة كائنات (Records)
    records = df_batch.to_dict(orient='records')
    
    # تغليف البيانات في حقل "items" كما طلب السيرفر
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
            print(f"❌ خطأ {response.status_code} في الدفعة {batch_num}")
            print(f"💬 رد السيرفر: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود في المستودع!")
        return

    print(f"📂 جاري قراءة الملف وتوفيق الأعمدة...")
    # قراءة ملف الإكسل
    df = pd.read_excel(INPUT_FILE)

    # 🔄 خريطة تحويل الأسمدة (Mapping) لتطابق الداتابيز
    column_mapping = {
        "id": "source_id",
        "clearanceFeeExport": "clearance_fee_export",
        "priceImport": "price_import",
        "clearanceFee": "clearance_fee",
        "priceFull": "price_full",
        "type": "item_type",
        "priceExport": "price_export",
        "last_updated": "updated_from_file_at",
        "global_verification_link": "image_urls" # أو أي حقل إضافي تراه مناسباً
    }

    # تنفيذ إعادة التسمية
    df.rename(columns=column_mapping, inplace=True)

    # تنظيف الفراغات من الأسماء
    df.columns = [str(c).strip() for c in df.columns]

    # معالجة القيم الفارغة (NaN) وتحويلها لنصوص فارغة لضمان قبول السيرفر
    df = df.fillna("")

    total_rows = len(df)
    print(f"📊 إجمالي البيانات الجاهزة: {total_rows} سطر.")
    
    # الرفع بنظام الباتشات (المجموعات)
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        
        # استراحة بسيطة لتفادي ضغط السيرفر
        time.sleep(1.5)

if __name__ == "__main__":
    main()
