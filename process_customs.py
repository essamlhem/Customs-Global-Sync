import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# تعديل اسم الملف للاسم الصحيح اللي عندك
csv_file = 'customs_global_brain (6).xlsx'
pdf_file = 'الشروحات.pdf'

def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(text))

print("--- جاري محاولة قراءة ملف الإكسل ---")
try:
    # قراءة ملف الإكسل مباشرة (Excel وليس CSV)
    df = pd.read_excel(csv_file).head(20)
    print("تمت قراءة الملف بنجاح")
except Exception as e:
    print(f"حدث خطأ أثناء القراءة: {e}")
    # محاولة قراءته كـ CSV في حال كان الامتداد مخادعاً
    df = pd.read_csv(csv_file).head(20)

descriptions = {}
print("جاري فحص أول 50 صفحة من الـ PDF...")

with pdfplumber.open(pdf_file) as pdf:
    for i, page in enumerate(pdf.pages[:50]):
        text = page.extract_text()
        if text:
            for band in df['band_syria'].unique():
                str_band = str(band).strip()
                if str_band in text:
                    descriptions[band] = fix_arabic(text[:500])

df['pdf_description'] = df['band_syria'].map(descriptions)
df.to_excel('test_output_50.xlsx', index=False)
print("تم إنشاء ملف النتيجة بنجاح")
