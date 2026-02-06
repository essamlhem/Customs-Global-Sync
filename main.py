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
    print(f"🚀 بدء التشغيل: {datetime.now()}")
    scraper = SupabaseScraper()
    image_cache = load_cache()
    
    # مناداة الدالة الصحيحة لتجنب AttributeError
    raw_data = scraper.fetch_raw_data()
    
    if not raw_data:
        print("⚠️ لم يتم جلب مواد. احتمال الـ Quota انتهت لليوم.")
        return

    final_list = []
    new_count = 0
    total = len(raw_data)

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', index))
        
        if item_id in image_cache and len(image_cache[item_id]) > 0:
            imgs = image_cache[item_id]
        else:
            print(f"🔍 [{index+1}/{total}] جاري البحث عن صور...")
            imgs = scraper.get_real_images(item.get('brand', ''), item.get('model', ''))
            image_cache[item_id] = imgs
            new_count += 1
            if new_count % 20 == 0:
                save_cache(image_cache)
                time.sleep(1)

        item['image_urls'] = imgs
        final_list.append(item)

    save_cache(image_cache)
    
    df = pd.DataFrame(final_list)
    file_name = "Across_MENA_Final_Report.csv"
    df.to_csv(file_name, index=False, encoding='utf-8-sig')

    # إرسال تليجرام
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if bot_token and chat_id:
        msg = f"✅ اكتمل التحديث\n📦 المواد: {len(df)}\n📸 صور جديدة: {new_count}"
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': msg})
        with open(file_name, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", data={'chat_id': chat_id}, files={'document': f})

if __name__ == "__main__":
    main()
