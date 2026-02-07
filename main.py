import pandas as pd
import requests
import os
import time

# الإعدادات الأساسية
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
BATCH_SIZE = 500 

# 🔑 التوكن اللي بعته أنت
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"

def upload_to_backend(df_batch, batch_num):
    temp_filename = f"batch_{batch_num}.csv"
    # تحويل الباتش لملف CSV مؤقت
    df_batch.to_csv(temp_filename, index=False, encoding='utf-8-sig')
    
    # تجهيز الهيدر مع التوكن
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    try:
        with open(temp_filename, 'rb') as f:
            files = {'file': (temp_filename, f, 'text/csv')}
            print(f"🚀 جاري رفع الدفعة رقم {batch_num}...")
            
            # إرسال الطلب مع التوكن
            response = requests.post(UPLOAD_URL, files=files, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"✅ الدفعة {batch_num} وصلت بنجاح!")
            else:
                print(f"❌ خطأ بالرفع للدفعة {batch_num}: كود {response.status_code}")
                print(f"رد السيرفر: {response.text}")
    except Exception as e:
        print(f"❌ فشل الاتصال بالسيرفر: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود! تأكد من رفعه على GitHub بنفس الاسم.")
        return

    print(f"📂 جاري قراءة الملف وتجهيزه...")
    df = pd.read_excel(INPUT_FILE)

    # تنظيف الأعمدة (حذف material و note)
    df.columns = [c.lower().strip() for c in df.columns]
    columns_to_remove = ['material', 'note']
    
    for col in columns_to_remove:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"🗑️ تم حذف عمود: {col}")

    total_rows = len(df)
    print(f"📊 إجمالي الأسطر الجاهزة للرفع: {total_rows}")
    
    # تقسيم الرفع لباتشات
    for i in range(0, total_rows, BATCH_SIZE):
        batch_df = df.iloc[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        upload_to_backend(batch_df, batch_num)
        time.sleep(1) # استراحة ثانية بين الرفعات

if __name__ == "__main__":
    main()
