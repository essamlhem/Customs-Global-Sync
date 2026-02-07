import pandas as pd
import requests
import os
import time
import json

# الإعدادات
UPLOAD_URL = "https://across-mena.com/customs/upload-batch/"
INPUT_FILE = "Across_MENA_Daily_Report.xlsx"
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"

def upload_row(row_data, row_num):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # إرسال سطر واحد فقط كـ Dictionary
        response = requests.post(UPLOAD_URL, json=row_data, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ السطر {row_num} تم رفعه بنجاح.")
            return True
        else:
            print(f"❌ فشل السطر {row_num}: كود {response.status_code}")
            return False
                
    except Exception as e:
        print(f"❌ خطأ تقني في السطر {row_num}: {e}")
        return False

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف {INPUT_FILE} غير موجود!")
        return

    print("📂 جاري معالجة الملف للرفع سطر بسطر...")
    df = pd.read_excel(INPUT_FILE)

    # تنظيف الأعمدة
    df.columns = [str(c).strip() for c in df.columns]
    for col in ['material', 'note', 'Material', 'Note']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # تحويل كل شيء لنصوص ومعالجة الفراغات
    df = df.fillna("").astype(str)

    # تحويل البيانات لقائمة من القواميس
    rows = df.to_dict(orient='records')
    total_rows = len(rows)
    print(f"📊 إجمالي الأسطر المطلوب رفعها: {total_rows}")

    success_count = 0
    for i, row in enumerate(rows):
        if upload_row(row, i + 1):
            success_count += 1
        
        # استراحة بسيطة جداً عشان ما نهجم على السيرفر
        time.sleep(0.1) 

    print(f"\n🚀 انتهت العملية! تم رفع {success_count} من أصل {total_rows}.")

if __name__ == "__main__":
    main()
