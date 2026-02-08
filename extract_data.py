import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. تحميل ملف الإكسل (أول 10 أسطر للتجربة)
df_excel = pd.read_csv('customs_global_brain (6).xlsx - Sheet1.csv').head(10)

# وظيفة لتصحيح النص العربي المقلوب
def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(text))

# 2. فتح الـ PDF واستخراج النصوص (أول 50 صفحة للتجربة)
pdf_path = 'الشروحات.pdf'
extracted_data = {}

print("جاري فحص الـ PDF... انتظر قليلاً")

with pdfplumber.open(pdf_path) as pdf:
    # سنجرب أول 50 صفحة لنرى إذا سنجد تطابق للبنود العشرة الأولى
    for i in range(50):
        page_text = pdf.pages[i].extract_text()
        if page_text:
            # تصحيح النص المستخرج من الصفحة
            clean_text = fix_arabic(page_text)
            
            # البحث عن كل بند من الإكسل داخل نص الصفحة
            for band in df_excel['band_syria']:
                # تحويل البند لنص للبحث عنه
                str_band = str(band).strip()
                if str_band in page_text: # البحث في النص الأصلي قبل التشكيل أحياناً أدق
                    extracted_data[str_band] = clean_text

# 3. ربط الشروحات بملف الإكسل
df_excel['pdf_description'] = df_excel['band_syria'].astype(str).map(extracted_data)

# 4. حفظ النتيجة لتفحصها
df_excel.to_excel('test_result.xlsx', index=False)
print("تم الانتهاء! افحص ملف test_result.xlsx")
