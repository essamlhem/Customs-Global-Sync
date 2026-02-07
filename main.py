import os
import pandas as pd
import json
import time
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def git_push_progress(count):
    """رفع الملفات لـ GitHub أثناء التشغيل"""
    try:
        os.system('git config --local user.email "action@github.com"')
        os.system('git config --local user.name "GitHub Action"')
        os.system(f'git add {CACHE_FILE} Across_MENA_Final_Report.csv')
        os.system(f'git commit -m "حفظ تلقائي: {count} صورة جديدة"')
        os.system('git push')
        print(f"☁️ تم الرفع لـ GitHub بنجاح.")
    except:
        print("⚠️ فشل الرفع التلقائي.")

def main():
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    if not os.path.exists(csv_file):
        print("❌ data.csv غير موجود")
        return

    df_input = pd.read_csv(csv_file)
    raw_data = df_input.to_dict(orient='records')

    # تحميل الكاش
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            image_cache = json.load(f)
    else:
        image_cache = {}

    final_list = []
    new_images_count = 0

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', index))
        
        # تخطي إذا كان موجوداً
        if item_id in image_cache and image_cache[item_id]:
            item['image_urls'] = image_cache[item_id]
            final_list.append(item)
            continue

        brand = str(item.get('brand', ''))
        model = str(item.get('model', ''))
        print(f"🔍 [{index+1}/{len(raw_data)}] سحب: {brand} {model}")
        
        imgs = scraper.get_real_images(brand, model)
        image_cache[item_id] = imgs
        item['image_urls'] = imgs
        new_images_count += 1
        final_list.append(item)

        # الحفظ والرفع كل 50 مادة جديدة
        if new_images_count % 50 == 0:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(image_cache, f, ensure_ascii=False, indent=4)
            pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
            git_push_progress(new_images_count)

    # الحفظ النهائي
    pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
    print("🏁 انتهى العمل بنجاح.")

if __name__ == "__main__":
    main()
