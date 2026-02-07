import pandas as pd
import requests
import os
import time

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
        # إرسال سطر واحد
        response = requests.post(UPLOAD_URL, json=row_data, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ السطر {row_num}: تم الرفع.")
            return True
        else:
            # 🔍 أهم سطر: طباعة الرد عشان نعرف شو العمود اللي ناقص
            print(f"❌ السطر {row_num}: خطأ {response.status_code} | الرد: {response.text}")
            return False
                
    except Exception as e:
        print(f"❌ السطر {row_num}: خطأ تقني {e}")
        return False

def main():
    if not os.path.exists(INPUT_FILE):
        print("❌ ملف الإكسل غير موجود!")
        return

    # قراءة الملف (بدون تحويل الأعمدة لـ lowercase عشان ما نغير أسماء الحقول المطلوبة)
    df = pd.read_excel(INPUT_FILE)

    # تنظيف المسافات من أسماء الأعمدة فقط
    df.columns = [str(c).strip() for c in df.columns]

    # حذف الأعمدة اللي طلبتها (بندور عليها بكل الحالات)
    for target in ['material', 'note', 'Material', 'Note']:
        if target in df.columns:
            df.drop(columns=[target], inplace=True)
            print(f"🗑️ تم حذف: {target}")

    # معالجة القيم الفارغة (مهمة جداً للباك إيند)
    df = df.fillna("")

    rows = df.to_dict(orient='records')
    print(f"📊 بدء رفع {len(rows)} سطر...")

    for i, row in enumerate(rows[:20]): # جرب أول 20 سطر بس عشان نفهم العلة
        upload_row(row, i + 1)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
