import pdfplumber
import json
import re
import os

def extract_comprehensive_logic():
    # تأكد أن اسم الملف يطابق الملف المرفوع في جيت هب
    pdf_path = "الشروحات.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ خطأ: ملف {pdf_path} غير موجود!")
        return

    extracted_data = {}
    current_heading = None
    
    print("⏳ بدأت معالجة الـ PDF... يرجى الانتظار، الملف ضخم (1200+ صفحة)")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue

                # البحث عن أرقام البنود (4 أرقام مثل 01.01) في بداية السطر
                heading_match = re.search(r'^(\d{2}\.\d{2})', line)
                
                if heading_match:
                    # تحويل الرقم من 01.01 إلى 0101 لسهولة الربط لاحقاً
                    current_heading = heading_match.group(1).replace('.', '')
                    
                    if current_heading not in extracted_data:
                        extracted_data[current_heading] = {
                            "heading_number": heading_match.group(1),
                            "full_content": [line]
                        }
                    else:
                        extracted_data[current_heading]["full_content"].append(line)
                
                # إذا كان السطر هو تفاصيل تابعة للبند الحالي
                elif current_heading:
                    extracted_data[current_heading]["full_content"].append(line)

    # دمج الأسطر لتكوين نص واحد شامل لكل بند
    final_logic = {}
    for code, info in extracted_data.items():
        final_logic[code] = " ".join(info["full_content"])

    # حفظ النتيجة النهائية في ملف JSON
    with open("customs_logic.json", "w", encoding="utf-8") as f:
        json.dump(final_logic, f, ensure_ascii=False, indent=4)
    
    print(f"✅ تم الانتهاء بنجاح! تم استخراج {len(final_logic)} بند جمركي مشروح.")

if __name__ == "__main__":
    extract_comprehensive_logic()
