import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def main():
    print(f"🚀 بدء معالجة البيانات: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    scraper = SupabaseScraper()
    image_cache = load_cache()
    
    # جلب البيانات (استخدام الاسم الصحيح للدالة)
    raw_data = scraper.fetch_raw_data()
    
    if not raw_data:
        print("⚠️ لم يتم جلب أي مواد. توقف التشغيل.")
        return

    final_list = []
    new_images_count = 0
    total_items = len(raw_data)

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', index))
        
        if item_id in image_cache and len(image_cache[item_id]) > 0:
            item_images = image_cache[item_id]
        else:
            brand = item.get('brand', '')
            model = item.get('model', '')
            print(f"🔍 [{index+1}/{total_items}] سحب صور لـ: {brand} {model}")
            item_images = scraper.get_real_images(brand, model)
            image_cache[item_id] = item_images
            new_images_count += 1
            if new_images_count % 20 == 0:
                save_cache(image_cache)
                time.sleep(1)

        item['image_urls'] = item_images
        final_list.append(item)

    save_cache(image_cache)
    df = pd.DataFrame(final_list)
    cols_to_drop = ['material', 'note', 'band-material', 'band_material', 'image_search_link']
    df_final = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    file_name = "Across_MENA_Report.csv"
    df_final.to_csv(file_name, index=False, encoding='utf-8-sig')

    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if bot_token and chat_id:
        msg = f"✅ تحديث مكتمل\n📦 المواد: {len(df_final)}\n📸 صور جديدة: {new_images_count}"
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': msg})
        with open(file_name, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", data={'chat_id': chat_id}, files={'document': f})

if __name__ == "__main__":
    main()
