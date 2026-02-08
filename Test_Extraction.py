import pdfplumber
import re
import json

def fix_arabic_visual(text):
    """
    دالة ذكية للتعامل مع النصوص العربية المستخرجة من PDF.
    سنقوم بعكس النص فقط إذا كان مستخرجاً بشكل مقلوب (LTR بدلاً من RTL).
    """
    if not text: return ""
    # في أغلب ملفات الـ PDF العربية، النص يحتاج لإعادة ترتيب الكلمات أو الحروف
    # سنقوم بعكس السطر بالكامل كتجربة أولية
    return text[::-1]

def run_test_sample(pdf_path, pages_count=20):
    sample_data = {}
    # نمط للبحث عن رقم البند (مثل 01.01) في بداية السطر أو وسطه
    code_pattern = re.compile(r'(\d{2}\.\d{2})')

    print(f"🧐 فحص أول {pages_count} صفحات من الملف...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i in range(pages_count):
                page = pdf.pages[i]
                text = page.extract_text()
                if not text: continue

                lines = text.split('\n')
                current_code = None
                
                for line in lines:
                    match = code_pattern.search(line)
                    if match:
                        current_code = match.group(1).replace('.', '')
                        sample_data[current_code] = ""
                    
                    if current_code:
                        sample_data[current_code] += line + " "

        # تنظيف وعكس النص في العينة
        final_sample = {}
        for code, raw_text in sample_data.items():
            # تنظيف المسافات
            clean_text = re.sub(r'\s+', ' ', raw_text).strip()
            # هنا نقوم بالعكس للتجربة
            final_sample[code] = fix_arabic_visual(clean_text)

        with open('test_sample.json', 'w', encoding='utf-8') as f:
            json.dump(final_sample, f, ensure_ascii=False, indent=4)
        
        print(f"✅ انتهى الفحص! تم استخراج {len(final_sample)} بند من أول {pages_count} صفحة.")
        print("📁 الملف جاهز للمعاينة: test_sample.json")

    except Exception as e:
        print(f"❌ خطأ أثناء الفحص: {e}")

# تشغيل العينة
pdf_file = "الشروحات.pdf"
run_test_sample(pdf_file)
