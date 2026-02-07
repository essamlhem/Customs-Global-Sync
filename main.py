import os
import pandas as pd
import json
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"
REPORT_FILE = "Across_MENA_Final_Report.csv"

def git_push(count):
    os.system('git config --local user.email "action@github.com"')
    os.system('git config --local user.name "GitHub Action"')
    os.system(f'git add {CACHE_FILE} {REPORT_FILE}')
    os.system(f'git commit -m "تحديث: تم صيد {count} منتج بـ 6 صور"')
    os.system('git push')

def main():
    scraper = SupabaseScraper()
    if not os.path.exists("data.csv"): return

    df = pd.read_csv("data.csv")
    raw_data = df.to_dict(orient='records')

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

    final_list = []
    new_count = 0

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', index))
        
        # لا يتخطى إلا إذا وجد فعلاً 6 صور
        if item_id in cache and isinstance(cache[item_id], list) and len(cache[item_id]) >= 6:
            item['image_urls'] = cache[item_id]
            final_list.append(item)
            continue

        brand, model = str(item.get('brand', '')), str(item.get('model', ''))
        print(f"🔍 [{index+1}/{len(raw_data)}] جاري صيد 6 صور لـ: {brand} {model}")
        
        imgs = scraper.get_real_images(brand, model)
        cache[item_id] = imgs
        item['image_urls'] = imgs
        final_list.append(item)
        new_count += 1

        if new_count % 30 == 0:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)
            pd.DataFrame(final_list).to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
            git_push(new_count)

    pd.DataFrame(final_list).to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
    git_push("نهائي")

if __name__ == "__main__":
    main()
