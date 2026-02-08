import pandas as pd
import json
import os
import sys
import glob

def fix_arabic(text):
    if not text or not isinstance(text, str):
        return ""
    return text[::-1]

def build_brain():
    # 1. البحث التلقائي عن الملفات لتجنب أخطاء الأسماء
    excel_files = glob.glob("customs_global_brain*.xlsx")
    json_files = glob.glob("customs_logic*.json")
    
    output_file = 'master_data.csv'

    print("--- Start Process ---")

    if not excel_files:
        print("❌ Error: No Excel file found starting with 'customs_global_brain'!")
        sys.exit(1)
    
    if not json_files:
        print("❌ Error: No JSON file found starting with 'customs_logic'!")
        sys.exit(1)

    excel_file = excel_files[0]
    json_file = json_files[0]
    
    print(f"📂 Using Excel: {excel_file}")
    print(f"📂 Using JSON: {json_file}")

    # 2. قراءة ملف الإكسل
    try:
        df = pd.read_excel(excel_file)
        df.columns = df.columns.astype(str).str.strip()
        print(f"✅ Excel Loaded. Rows: {len(df)}")
    except Exception as e:
        print(f"❌ Excel Load Error: {e}")
        sys.exit(1)

    # 3. تحديد عمود الرمز الجمركي
    target_col = 'hs6_global'
    if target_col not in df.columns:
        potential_cols = [c for c in df.columns if 'hs' in c.lower()]
        if potential_cols:
            target_col = potential_cols[0]
            print(f"⚠️ Using column '{target_col}' for HS Codes.")
        else:
            print("❌ Error: HS Code column not found!")
            sys.exit(1)

    df[target_col] = df[target_col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)

    # 4. قراءة وتصحيح الـ JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
        fixed_logic = {str(k).strip(): fix_arabic(v) for k, v in raw_json.items()}
        print(f"✅ JSON Loaded. Items: {len(fixed_logic)}")
    except Exception as e:
        print(f"❌ JSON Load Error: {e}")
        sys.exit(1)

    # 5. الدمج
    print("🧠 Merging data...")
    df['detailed_description'] = df[target_col].apply(lambda x: fixed_logic.get(x) or fixed_logic.get(x[:4]) or "No description")

    # 6. الحفظ
    try:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"🎉 Success! {output_file} created.")
    except Exception as e:
        print(f"❌ Save Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_brain()
