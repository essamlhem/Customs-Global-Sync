import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعداد المسارات (تأكد من مطابقة الأسماء تماماً)
csv_file = 'customs_global_brain (6).xlsx - Sheet1.csv'
pdf_file = 'الشروحات.pdf'

def fix_arabic(text):
    if not text: return ""
    # إعادة تشكيل النص ليكون مقروءاً في الإكسل
    return get_display(reshape(text))

# 2. قراءة ملف الإكسل (سنأخذ أول 20 بند للتجربة)
print("جاري قراءة ملف الإكسل...")
df = pd.read_csv(csv_file).head(20)

# 3. استخراج النصوص من الـ PDF
descriptions = {}
print("جاري استخراج الشروحات من الـ PDF (أول 50 صفحة)...")

with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages[:50]: # تجربة على أول 50 صفحة فقط
        text = page.extract_text()
        if text:
            for index, row in df.iterrows():
                band_code = str(row['band_syria']).strip()
                # البحث عن رقم البند داخل نص الصفحة
                if band_code in text:
                    # نأخذ النص ونصلحه لغوياً
                    descriptions[band_code] = fix_arabic(text[:500]) # نأخذ أول 500 حرف كشرح مبدئي

# 4. دمج الشروحات مع الإكسل
df['الشرح_المستخرج'] = df['band_syria'].astype(str).map(descriptions)

# 5. حفظ النتيجة في ملف إكسل جديد
df.to_excel('final_result.xlsx', index=False)
print("تمت العملية بنجاح! الملف الناتج: final_result.xlsx")
