import pandas as pd
import requests
import time
import os

# إعدادات
FILE_PATH = "customs_global_brain_translated.xlsx"
URL = "https://across-mena.com/customs/upload-batch/"
TOKEN = "OJLEh-Zb-o9DbQWt9J3cu7wJBWGUJvSeCkUPGa5H6"
BATCH_SIZE = 500   # عدد الصفوف بكل دفعة
DELAY = 1          # ثانية بين كل دفعة

# قراءة الملف
df = pd.read_excel(FILE_PATH)

total_rows = len(df)
total_batches = (total_rows // BATCH_SIZE) + 1

print(f"Total rows: {total_rows}")
print(f"Total batches: {total_batches}")

headers = {
    "Authorization": f"Token {TOKEN}"
}

for i in range(0, total_rows, BATCH_SIZE):

    batch_number = (i // BATCH_SIZE) + 1

    # تقسيم البيانات
    batch_df = df.iloc[i:i+BATCH_SIZE]

    # حفظ دفعة مؤقتة
    temp_file = f"batch_{batch_number}.xlsx"
    batch_df.to_excel(temp_file, index=False)

    print(f"Uploading batch {batch_number}...")

    with open(temp_file, "rb") as f:
        files = {"file": f}
        response = requests.post(URL, headers=headers, files=files)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    # حذف الملف المؤقت
    os.remove(temp_file)

    # انتظار
    time.sleep(DELAY)

print("Upload completed.")
