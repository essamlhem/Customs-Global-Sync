import json

def reverse_arabic_fix(text):
    """
    هذه الدالة تقوم بتعديل اتجاه النص إذا كان مخزناً بشكل معكوس
    """
    if not text:
        return ""
    # إذا كان النص يبدأ بترميز معكوس، نعيد ترتيبه
    return text[::-1] 

def main():
    input_file = 'customs_logic (4).json'
    output_file = 'customs_logic_fixed.json'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fixed_data = {}
        for key, value in data.items():
            # تصليح النص المعكوس لكل بند
            fixed_data[key] = reverse_arabic_fix(value)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ تم بنجاح! الملف الجديد الجاهز هو: {output_file}")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
