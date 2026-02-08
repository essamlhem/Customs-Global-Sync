import pandas as pd
import json
import os

def fix_arabic(text):
    if not text or not isinstance(text, str):
        return ""
    # عكس النص لتصحيح التخزين المعكوس في الـ JSON
    return text[::-1]

def build_brain():
    # 1. إعداد المسارات
    excel_file = 'customs_global_brain (6).xlsx'
    json_file = 'customs_logic (4).json'
    output_file = 'master_data.csv'

    print("📂 جاري تحميل البيانات...")

    # 2. قراءة ملف الإكسل
    if not os.path.exists(excel_file):
        print(f"❌ خطأ: ملف الإكسل {excel_file} غير موجود!")
        return
    df = pd.read_excel(excel_file)
    
    # تنظيف أسماء الأعمدة وفورمات الـ HS Code
    df.columns = [str(c).strip() for c in df.columns]
    # التأكد أن hs6_global نصي ومكون من 6 أرقام (مع الأصفار)
    if 'hs6_global' in df.columns:
        df['hs6_global'] = df['hs6_global'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)

    # 3. قراءة ملف الـ JSON وتصحيحه
    if not os.path.exists(json_file):
        print(f"❌ خطأ: ملف الـ JSON {json_file} غير موجود!")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        logic_data = json.load(f)
    
    # تصحيح العربي في القاموس (الـ Key هو الرمز، والـ Value هو الشرح)
    fixed_logic = {str(k).strip(): fix_arabic(v) for k, v in logic_data.items()}

    print("🧠 جاري دمج الشروحات مع البنود الجمركية...")

    # 4. عملية الربط (Matching)
    # سننشئ عموداً جديداً اسمه 'detailed_description'
    def get_description(hs_code):
        # نحاول البحث بالرمز المكون من 6 أرقام أو أول 4 أرقام إذا لم يوجد
        description = fixed_logic.get(hs_code, "")
        if not description and len(hs_code) >= 4:
            description = fixed_logic.get(hs_code[:4], "")
        return description

    df['detailed_description'] = df['hs6_global'].apply(get_description)

    # 5. اختيار الأعمدة المهمة للعقل فقط
    # سنحتفظ بالرمز، الاسم الأصلي، الشرح الجديد، السعر، ورابط الصورة
    essential_cols = ['hs6_global', 'name', 'detailed_description', 'priceFull', 'global_verification_link']
    # التأكد من وجود الأعمدة في الملف
    existing_cols = [c for c in essential_cols if c in df.columns]
    master_df = df[existing_cols]

    # 6. حفظ النتيجة
    master_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ تم بنجاح! 'عقل المودل' جاهز الآن في ملف: {output_file}")
    print(f"📊 إجمالي السجلات المدمجة: {len(master_df)}")

if __name__ == "__main__":
    build_brain()
