import pdfplumber
import pandas as pd
import re

# أسماء الملفات عندك
excel_file = 'customs_global_brain (6).xlsx'
pdf_file = 'الشروحات.pdf'

print("جاري تشغيل المعالجة الشاملة لـ 5718 بند... طول بالك شوي")

# قراءة الملف كامل
df = pd.read_excel(excel_file)
df['band_syria'] = df['band_syria'].astype(str).str.zfill(8) # توحيد التنسيق لـ 8 أرقام

descriptions = {}

with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            # البحث عن الأكواد بصيغة 01.01 أو 0101
            for index, row in df.iterrows():
                code = row['band_syria']
                short_code = f"{code[:2]}.{code[2:4]}"
                
                if short_code in text or code[:4] in text:
                    if code not in descriptions: # نأخذ أول وصف نلاقيه
                        descriptions[code] = text[:1000] # نأخذ أول 1000 حرف من الصفحة

# ربط النتائج وحفظ الملف
df['pdf_description'] = df['band_syria'].map(descriptions)
df.to_excel('Full_Customs_Final_5718.xlsx', index=False)
print("مبروك يا عيسى! الملف صار جاهز باسم Full_Customs_Final_5718.xlsx")
