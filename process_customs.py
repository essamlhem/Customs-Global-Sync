import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import re

# 1. إعداد المسارات
csv_file = 'customs_global_brain (6).xlsx - Sheet1.csv'
pdf_file = 'الشروحات.pdf'

def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(text))

# 2. قراءة الإكسل (أول 20 بند للتجربة)
print("--- جاري تحميل البيانات ---")
df = pd.read_csv(csv_file).head(20)

# 3. استخراج النصوص
descriptions = {}
print("--- جاري فحص أول 100 صفحة من الـ PDF ---")

with pdfplumber.open(pdf_file) as pdf:
    for i, page in enumerate(pdf.pages[:100]): # زدنا الصفحات لـ 100 للتجربة
        text = page.extract_text()
        if text:
            for index, row in df.iterrows():
                band_code = str(row['band_syria']).strip()
                
                # احتمالات كتابة الكود: 01013000 أو 0101.30.00 أو 01.01
                # سنبحث عن أول 4 أرقام لأنها الأهم في الشروحات
                short_code = band_code[:4] 
                formatted_code = f"{short_code[:2]}.{short_code[2:]}"
                
                if band_code in text or formatted_code in text:
                    print(f"تم العثور على البند {band_code} في الصفحة {i+1}")
                    # حفظ النص كاملاً مؤقتاً
                    descriptions[row['band_syria']] = fix_arabic(text)

# 4. الربط والحفظ
df['pdf_description'] = df['band_syria'].map(descriptions)
df.to_excel('final_result.xlsx', index=False)
print("--- تم إنشاء الملف بنجاح: final_result.xlsx ---")
