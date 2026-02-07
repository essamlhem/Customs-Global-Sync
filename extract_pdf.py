import pdfplumber
import json
import re
import os

def extract_logic():
    pdf_path = "الشروحات.pdf"
    if not os.path.exists(pdf_path):
        print("❌ ملف الشروحات.pdf غير موجود!")
        return

    extracted_data = {}
    print("⏳ جاري معالجة ملف PDF... قد يستغرق ذلك دقائق")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # البحث عن أرقام البنود مثل 01.01 أو 84.07
                # هذا النمط يبحث عن رقمين نقطة رقمين
                matches = re.finditer(r'(\d{2}\.\d{2})', text)
                
                parts = re.split(r'(\d{2}\.\d{2})', text)
                for i in range(1, len(parts), 2):
                    hs_code = parts[i].replace('.', '') # تحويل 01.01 لـ 0101
                    explanation = parts[i+1].strip()
                    
                    # إذا البند مكرر، بنضيف الشرح الجديد للشرح القديم
                    if hs_code in extracted_data:
                        extracted_data[hs_code] += " " + explanation[:300]
                    else:
                        extracted_data[hs_code] = explanation[:500] # نأخذ أول 500 حرف كخلاصة

    # حفظ النتيجة في ملف JSON مرتب
    with open("customs_logic.json", "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ تم بنجاح! استخراج {len(extracted_data)} بند جمركي مشروح.")

if __name__ == "__main__":
    extract_logic()
