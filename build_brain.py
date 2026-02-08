import pandas as pd
import json
import os
import sys

def fix_arabic(text):
    if not text or not isinstance(text, str):
        return ""
    # عكس النص لتصحيح التخزين المعكوس في الـ JSON
    return text[::-1]

def build_brain():
    # أسماء الملفات كما هي في المستودع
    excel_file = 'customs_global_brain (6).xlsx'
    json_file = 'customs_logic (4).json'
    output_file = 'master_data.csv'

    print("--- Start Process ---")

    # 1. التأكد من وجود الملفات
    if not os.path.exists(excel_file):
        print(f"❌ Error: {excel_file} not found!")
        sys.exit(1)
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found!")
        sys.exit(1)

    # 2. قراءة ملف الإكسل
    try:
        # قراءة الملف مع تنظيف أسماء الأعمدة فوراً
        df = pd.read_excel(excel_file)
        df.columns = df.columns.astype(str).str.strip()
        print(f"✅ Excel Loaded. Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"❌ Excel Load Error: {e}")
        sys.exit(1)

    # 3. معالجة الرمز الجمركي (HS Code)
    # سنبحث عن العمود حتى لو اختلف اسمه قليلاً
    target_col = 'hs6_global'
    if target_col not in df.columns:
        # محاولة البحث عن عمود يشبهه
        potential_cols = [c for c in df.columns if 'hs' in c.lower()]
        if potential_cols:
            target_col = potential_cols[0]
            print(f"⚠️ Column 'hs6_global' not found, using '{target_col}' instead.")
        else:
            print(f"❌ Error: No HS Code column found!")
            sys.exit(1)

    # تنظيف الرموز وضمان 6 أرقام
    df[target_col] = df[target_col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)

    # 4. قراءة الـ JSON وتصليحه
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
        
        # تصليح العربي في الشروحات
        fixed_logic = {str(k).strip(): fix_arabic(v) for k, v in raw_json.items()}
        print(f"✅ JSON Loaded and Arabic fixed for {len(fixed_logic)} items.")
    except Exception as e:
        print(f"❌ JSON Load Error: {e}")
        sys.exit(1)

    # 5. عملية الدمج (Merging)
    print("🧠 Merging data...")
    def get_desc(code):
        # البحث بالـ 6 أرقام ثم الـ 4 أرقام كخطة بديلة
        res = fixed_logic.get(code)
        if not res and len(code) >= 4:
            res = fixed_logic.get(code[:4])
        return res if res else "No description available"

    df['detailed_description'] = df[target_col].apply(get_desc)

    # 6. حفظ الملف النهائي
    try:
        # حفظ الملف بترميز يدعم العربي (utf-8-sig)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"🎉 Success! {output_file} created with {len(df)} rows.")
    except Exception as e:
        print(f"❌ Save Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_brain()
