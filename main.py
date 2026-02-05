import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

# ملف الذاكرة لحفظ الروابط المسحوبة سابقاً
CACHE_FILE = "images_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def main():
    print(f"🚀 بدء المعالجة: {datetime.now().strftime('%H:%M')}")
    try:
        # 1. تحميل الذاكرة وجلب البيانات
        image_cache = load_cache()
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        if not raw_data:
            print("⚠️ لا توجد بيانات في Supabase")
            return

        final_list = []
        new_search_count = 0

        # 2. معالجة الصور لكل منتج
        for item in raw_data:
            # نستخدم الـ HS Code أو الموديل كمفتاح فريد في الذاكرة
            item_id = str(item.get('hs_code', item.get('model', '')))
            
            if item_id in image_cache and len(image_cache[item_id]) > 0:
                images_list = image_cache[item_id]
            else:
                # سحب 6 صور حقيقية للمنتجات الجديدة فقط
                brand = item.get('brand', '')
                model = item.get('model', '')
                print(f"🔍 سحب صور لـ: {brand} {model}")
                
                images_list = scraper.get_real_images(brand, model)
                image_cache[item_id] = images_list
                new_search_count += 1
                
                # تأخير بسيط جداً لمنع الحظر (كل 10 منتجات)
                if new_search_count % 10 == 0:
                    time.sleep(1)

            # إضافة المصفوفة لعمود 'image' بشكل JSON نصي [link1, link2...]
            item['image'] = json.dumps(images_list, ensure_ascii=False)
            final_list.append(item)

        # 3. حفظ الذاكرة المحدثة
        if new_search_count > 0:
            save_cache(image_cache)
            print(f"✅ تم تحديث {new_search_count} منتج جديد.")

        # 4. تحويل لـ DataFrame وتنظيف الأعمدة
        df = pd.DataFrame(final_list)
        
        # حذف الأعمدة الممنوعة (الماتريال، النوت، وأي روابط قديمة)
        cols_to_drop = [
            'material', 'note', 'band-material', 'band_material', 
            'image_search_link', 'image_links'
        ]
        df_final = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

        # 5. تصدير الملف النهائي CSV
        file_name = "Across_MENA_Full_Report.csv"
        df_final.to_csv(file_name, index=False, encoding='utf-8-sig')

        # 6. إرسال التقرير والملف لتليجرام
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")
        
        report_msg = (
            f"📢 تقرير Across MENA اليومي\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔹 عدد المواد: {len(df_final)}\n"
            f"🔹 تحديث صور: {new_search_count} منتج جديد\n"
            f"🔹 الوضع: تم دمج الـ HS Code مع مصفوفة الصور"
        )
        
        # إرسال النص
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                      data={'chat_id': chat_id, 'text': report_msg})
        
        # إرسال ملف الـ CSV
        with open(file_name, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", 
                          data={'chat_id': chat_id}, files={'document': f})

    except Exception as e:
        print(f"❌ خطأ في النظام: {e}")

if __name__ == "__main__":
    main()
