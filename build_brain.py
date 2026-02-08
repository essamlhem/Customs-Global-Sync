import pandas as pd
import json
import os

def fix_arabic(text):
    if not text or not isinstance(text, str):
        return ""
    return text[::-1]

def build_brain():
    # تأكد أن هذه الأسماء مطابقة تماماً للملفات في المستودع
    excel_file = 'customs_global_brain (6).xlsx'
    json_file = 'customs_logic (4).json'
    output_file = 'master_data.csv'

    print(f"🔍 فحص وجود الملفات...")
    if not os.path.exists(excel_file):
        print(f"❌ خطأ: ملف الإكسل '{excel_file}' غير موجود في المجلد!")
        return
    if not os.path.exists(json_file):
        print(f"❌ خطأ: ملف الـ JSON '{json_file}' غير موجود في المجلد!")
        return

    # 1. قراءة الإكسل
    try:
        df = pd.read_excel(excel_file)
        df.columns = [str(c).strip() for c in df.columns]
        print(f"✅ تم تحميل الإكسل بنجاح. عدد الأسطر: {len(df)}")
    except Exception as e:
        print(f"❌ فشل في قراءة الإكسل: {e}")
        return

    # 2. معالجة الرمز الجمركي
    col_name = 'hs6_global'
    if col_name not in df.columns:
        print(f"❌ لم أجد عمود '{col_name}'. الأعمدة المتاحة هي: {df.columns.tolist()}")
        return
    
    df[col_name] = df[col_name].astype(str).str.split('.').str[0].str.zfill(6)

    # 3. قراءة الـ JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            logic_data = json.load(f)
        fixed_logic = {str(k).strip(): fix_arabic(v) for k, v in logic_data.items()}
        print(f"✅ تم تحميل الـ JSON وتصليح {len(fixed_logic)} شرح.")
    except Exception as e:
        print(f"❌ فشل في قراءة الـ JSON: {e}")
        return

    # 4. الدمج
    print("🧠 جاري دمج البيانات...")
    df['detailed_description'] = df[col_name].apply(lambda x: fixed_logic.get(x) or fixed_logic.get(x[:4]) or "لا يوجد شرح")

    # 5. حفظ الملف
    try:
        # سنحفظ كل الأعمدة عشان ما نضيع بيانات
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        if os.path.exists(output_file):
            print(f"🎉 تم إنشاء الملف بنجاح: {output_file} (الحجم: {os.path.getsize(output_file)} bytes)")
        else:
            print(f"❌ فشل إنشاء الملف لسبب غير معروف.")
    except Exception as e:
        print(f"❌ خطأ أثناء حفظ الـ CSV: {e}")

if __name__ == "__main__":
    build_brain()
