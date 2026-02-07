import pandas as pd
import requests
import os
import time

UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
BATCH_SIZE = 500 

def upload_to_backend(df_batch, batch_num):
    temp_filename = f"batch_{batch_num}.csv"
    df_batch.to_csv(temp_filename, index=False, encoding='utf-8-sig')
    try:
        with open(temp_filename, 'rb') as f:
            files = {'file': (temp_filename, f, 'text/csv')}
            print(f"🚀 جاري رفع الدفعة {batch_num}...")
            response = requests.post(UPLOAD_URL, files=files, timeout=30)
            if response.status_code in [200, 201]:
                print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
            else:
                print(f"❌ خطأ بالرفع للدفعة {batch_num}: كود {response.status_code}")
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")
    finally:
        if os.path.exists(temp_filename): os.remove(temp_filename)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return
    df = pd.read_excel(INPUT_FILE)
    df.columns = [c.lower().strip() for c in df.columns]
    # حذف الأعمدة المطلوبة
    for col in ['material', 'note']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"🗑️ تم حذف عمود: {col}")
    
    total_rows = len(df)
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        upload_to_backend(batch_df, (i // BATCH_SIZE) + 1)
        time.sleep(1)

if __name__ == "__main__":
    main()
