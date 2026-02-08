import pdfplumber
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import os

csv_file = 'customs_global_brain (6).xlsx'
pdf_file = 'الشروحات.pdf'

def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(text))

print("--- جاري تحميل الإكسل (أول 20 بند) ---")
try:
    df = pd.read_excel(csv_file).head(20)
except:
    df = pd.read_csv(csv_file).head(20)

# تحويل البنود لقائمة للبحث عنها
bands_to_find = df['band_syria'].astype(str).tolist()
descriptions = {}

print(f"جاري فحص الـ PDF كاملاً للبحث عن {len(bands_to_find)} بند...")

with pdfplumber.open(pdf_file) as pdf:
    # سنمر على كل الصفحات حتى نجد البنود المطلوبة
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            for band in bands_to_find[:]: # نأخذ نسخة من القائمة
                # سنبحث عن الكود بصيغته الأصلية (01013000) 
                # أو بصيغة منقطة (01.01) المنتشرة في الشروحات
                dot_code = f"{band[:2]}.{band[2:4]}"
                
                if band in text or dot_code in text:
                    print(f"✅ تم العثور على البند {band} في الصفحة {i+1}")
                    descriptions[band] = fix_arabic(text)
                    bands_to_find.remove(band) # نحذفه من القائمة عشان ما ندور عليه مرة تانية
        
        # إذا لقينا كل البنود نوقف البحث توفيراً للوقت
        if not bands_to_find:
            break
        
        if i % 100 == 0:
            print(f"تم فحص {i} صفحة...")

df['pdf_description'] = df['band_syria'].astype(str).map(descriptions)
df.to_excel('test_output_full_search.xlsx', index=False)
print("--- انتهت العملية! افحص ملف test_output_full_search.xlsx ---")
