import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def git_push_progress(count):
    """وظيفة لرفع التقدم لـ GitHub تلقائياً"""
    try:
        os.system('git config --local user.email "action@github.com"')
        os.system('git config --local user.name "GitHub Action"')
        os.system(f'git add {CACHE_FILE} data.csv Across_MENA_Final_Report.csv')
        os.system(f'git commit -m "حفظ تلقائي: تم إنجاز {count} صورة جديدة"')
        os.system('git push')
        print(f"☁️ [GitHub] تم رفع التقدم بنجاح (إجمالي الصور الجديدة: {count})")
    except Exception as e:
        print(f"⚠️ فشل الرفع لـ GitHub: {e}")

def main():
    print(f"🚀 بدء التشغيل: {datetime.now()}")
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    if not os.path.exists(csv_file):
        print("❌ ملف data.csv غير موجود!")
        return
    
    try:
        df_input = pd.read_csv(csv_file)
        raw_data = df_input.to_dict(orient='records')
        print(f"✅ تم تحميل {len(raw_data)} مادة.")
    except Exception as e:
        print(f"❌ خطأ في قراءة CSV: {e}")
        return

    # تحميل الكاش (المواد المنجزة سابقاً)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            image_cache = json.load(f)
        print(f"📦 تم العثور على كاش يحتوي على {len(image_cache)} مادة.")
    else:
        image_cache = {}

    final_list = []
    new_images_count = 0
    total_items = len(raw_data)

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', f"{item.get('brand')}_{item.get('model')}"))
        
        # تخطي إذا كان موجوداً مسبقاً
        if item_id in image_cache and image_cache[item_id]:
            item['image_urls'] = image_cache[item_id]
            final_list.append(item)
            continue
        
        brand = str(item.get('brand', ''))
        model = str(item.get('model', ''))
        print(f"🔍 [{index+1}/{total_items}] سحب صور لـ: {brand} {model}")
        
        try:
            imgs = scraper.get_real_images(brand, model)
            image_cache[item_id] = imgs
            item['image_urls'] = imgs
            new_images_count += 1
            final_list.append(item)

            # الحفظ المحلي والرفع لـ GitHub كل 50 صورة
            if new_images_count > 0 and new_images_count % 50 == 0:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(image_cache, f, ensure_ascii=False, indent=4)
                
                # حفظ التقرير المؤقت لضمان وجود الأعمدة
                pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
                
                print(f"💾 حفظ مؤقت محلي لـ {new_images_count} صورة.")
                git_push_progress(new_images_count) # الرفع لـ GitHub
                time.sleep(2) # تأخير لتجنب أي تعليق في الـ Push

        except Exception as e:
            print(f"⚠️ خطأ أثناء معالجة المادة {item_id}: {e}")
            continue

    # حفظ النتائج النهائية عند اكتمال الدورة
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_cache, f, ensure_ascii=False, indent=4)

    df_final = pd.DataFrame(final_list)
    df_final.to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
    git_push_progress(new_images_count)

    print(f"🏁 انتهت الدورة. المنجز الكلي: {len(image_cache)}")

if __name__ == "__main__":
    main()
