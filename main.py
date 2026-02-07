import os
import pandas as pd
import json
import time
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def git_push_progress(count):
    """حفظ التقدم ورفعه إلى GitHub"""
    try:
        os.system('git config --local user.email "action@github.com"')
        os.system('git config --local user.name "GitHub Action"')
        os.system(f'git add {CACHE_FILE} Across_MENA_Final_Report.csv')
        os.system(f'git commit -m "تحديث: تم صيد {count} صورة جديدة"')
        os.system('git push')
        print(f"☁️ [GitHub] تم رفع التقدم بنجاح!")
    except Exception as e:
        print(f"⚠️ فشل الرفع: {e}")

def main():
    # استدعاء السكرابر الجديد
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    if not os.path.exists(csv_file):
        print("❌ ملف data.csv غير موجود!")
        return

    # قراءة البيانات
    df_input = pd.read_csv(csv_file)
    raw_data = df_input.to_dict(orient='records')

    # تحميل الكاش (لو موجود)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                image_cache = json.load(f)
        except:
            image_cache = {}
    else:
        image_cache = {}

    final_list = []
    new_items_processed = 0

    for index, item in enumerate(raw_data):
        # نستخدم الـ ID أو رقم السطر كمرجع
        item_id = str(item.get('id', index))
        
        # إذا كان المنتج مسجل سابقاً وفيه صور (أكثر من 0)، نتخطاه
        if item_id in image_cache and isinstance(image_cache[item_id], list) and len(image_cache[item_id]) > 0:
            item['image_urls'] = image_cache[item_id]
            final_list.append(item)
            continue

        brand = str(item.get('brand', '')).replace('nan', '')
        model = str(item.get('model', '')).replace('nan', '')
        
        print(f"🔍 [{index+1}/{len(raw_data)}] جاري صيد صور لـ: {brand} {model}")
        
        # طلب الـ 6 صور من السكرابر الجديد
        found_images = scraper.get_real_images(brand, model)
        
        # حفظ النتائج في الكاش وفي القائمة النهائية
        image_cache[item_id] = found_images
        item['image_urls'] = found_images
        final_list.append(item)
        
        new_items_processed += 1

        # رفع التقدم كل 30 منتج (قللت العدد عشان تضمن الحفظ أسرع)
        if new_items_processed % 30 == 0:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(image_cache, f, ensure_ascii=False, indent=4)
            
            pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
            git_push_progress(new_items_processed)
            print(f"💾 تم حفظ {new_items_processed} مادة بنجاح...")

    # الحفظ النهائي عند اكتمال الدورة
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_cache, f, ensure_ascii=False, indent=4)
    pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
    git_push_progress("الكل")
    print("🏁 اكتملت المهمة بنجاح!")

if __name__ == "__main__":
    main()
