import json
import pandas as pd

class AcrossMENABrain:
    def __init__(self, data_file='knowledge_base.json'):
        self.data_file = data_file
        self.data = self.load_memory()

    def load_memory(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def search(self, query):
        if not self.data:
            return "عذراً عيسى، الذاكرة فارغة حالياً."

        # البحث في الوصف أو التصنيف
        results = [
            item for item in self.data 
            if query.lower() in str(item.get('material', '')).lower() 
            or query.lower() in str(item.get('category', '')).lower()
        ]
        
        return results[:5] # إعادة أول 5 نتائج فقط لضمان السرعة

    def format_answer(self, results):
        if not results:
            return "للأسف يا عيسى، ما لقيت معلومات عن طلبك بالداتا الحالية."
        
        response = "🔍 **نتائج البحث من Across MENA:**\n\n"
        for item in results:
            response += f"📦 *المادة:* {item.get('description_clean', 'غير معروف')}\n"
            response += f"📂 *التصنيف:* {item.get('category', 'عام')}\n"
            response += f"💰 *السعر الكلي:* {item.get('total_price', 'غير متوفر')}\n"
            response += f"🔗 [رابط الصورة]({item.get('image_search_link', '#')})\n"
            response += "------------------------\n"
        return response
