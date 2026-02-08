import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الملفات
csv_file = 'customs_global_brain (6).xlsx - Sheet1.csv'
pdf_file = 'الشروحات.pdf'

def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(text))

# قراءة أول 20 بند للتجربة
df = pd.read_csv(csv_file).head(20)

descriptions = {}
print("جاري فحص أول 50 صفحة...")

with pdfplumber.open(pdf_file) as pdf:
    for i, page in enumerate(pdf.pages[:50]):
        text = page.extract_text()
        if text:
            for band in df['band_syria'].unique():
                str_band = str(band).strip()
                if str_band in text:
                    descriptions[band] = fix_arabic(text[:500]) # أول 500 حرف

df['pdf_description'] = df['band_syria'].map(descriptions)
# حفظ الملف باسم واضح
df.to_excel('test_output_50.xlsx', index=False)
print("تم إنشاء ملف test_output_50.xlsx")
