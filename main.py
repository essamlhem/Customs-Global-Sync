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
    temp_filename = f"batch_{batch_num}.csv"
    # حفظ بدون index وبترميز utf-8 عشان الباك إيند يفهم الحروف العربي
    df_batch.to_csv(temp_filename, index=False, encoding='utf-8')
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
        # شلنا الـ Content-Type لأن مكتبة requests بتضيفه تلقائياً مع الملفات
    }
    
    try:
        with open(temp_filename, 'rb') as f:
            # تأكدنا إن اسم الحقل 'file' والملف بصيغة csv
            files = {
                'file': (temp_filename, f, 'text/csv')
            }
            print(f"🚀 جاري رفع الدفعة رقم {batch_num}...")
            
            response = requests.post(UPLOAD_URL, files=files, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
            else:
                print(f"❌ خطأ {response.status_code} في الدفعة {batch_num}")
                # طبع الرد عشان نعرف شو السيرفر بدو بالظبط
                print(f"💬 رد السيرفر: {response.text}")
                
    except Exception as e:
        print(f"❌ فشل تقني: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return

    print("📂 جاري معالجة الملف...")
    df = pd.read_excel(INPUT_FILE)

    # توحيد أسماء الأعمدة وحذف المطلوب
    df.columns = [str(c).lower().strip() for c in df.columns]
    for col in ['material', 'note']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"🗑️ حذف عمود: {col}")

    total_rows = len(df)
    print(f"📊 الإجمالي: {total_rows} سطر.")
    
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        upload_to_backend(batch_df, (i // BATCH_SIZE) + 1)
        time.sleep(2) # زدنا وقت الراحة شوي عشان السيرفر يلحق يعالج

if __name__ == "__main__":
    main()
