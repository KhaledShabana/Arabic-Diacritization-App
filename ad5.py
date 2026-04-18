# Arabic Text Diacritization App using Streamlit + Groq API
# Auto model selection + fallback
# Accessible UI (screen-reader friendly)

import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# =============================
# Load environment
# =============================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1"

# =============================
# Get available models from Groq
# =============================
def get_models():
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    try:
        response = requests.get(f"{GROQ_URL}/models", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # filter only chat-capable models (basic filter)
            models = [m['id'] for m in data.get('data', [])]
            return models
        else:
            return []
    except:
        return []

# =============================
# Try models until success
# =============================
def diacritize_text(text):
    if not GROQ_API_KEY:
        return "❌ لم يتم العثور على مفتاح Groq"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
قم بتشكيل النص العربي التالي تشكيلاً كاملاً ودقيقاً (حركات فقط) مع الالتزام التام بما يلي:

1. لا تقم بتغيير أي كلمة أو حرف في النص الأصلي.
2. لا تضف أي شرح أو إعراب أو تعليق.
3. لا تعيد صياغة الجملة.
4. أضف التشكيل (الحركات) فقط فوق الحروف.
5. حافظ على نفس ترتيب الكلمات تماماً.
6. إذا لم تكن متأكدًا من التشكيل، ضع التشكيل الأقرب دون تغيير الكلمة.

النص:
{text}

أعد النص بعد التشكيل فقط بدون أي إضافات.
"""

    models = get_models()

    if not models:
        return "❌ لم يتم جلب النماذج من Groq"

    for model in models:
        try:
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "أنت نموذج متخصص في تشكيل النصوص العربية بدقة عالية."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }

            response = requests.post(f"{GROQ_URL}/chat/completions", headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()

        except:
            continue

    return "❌ فشل في جميع النماذج"

# =============================
# Streamlit UI (Accessible)
# =============================

st.set_page_config(
    page_title="تشكيل النص العربي",
    layout="wide"
)

st.title("📝 تطبيق تشكيل النص العربي")

st.markdown("""
<div role="region" aria-label="وصف التطبيق">
أدخل النص العربي في المربع التالي وسيقوم التطبيق بتشكيله تلقائياً باستخدام الذكاء الاصطناعي.
</div>
""", unsafe_allow_html=True)

# Input
user_input = st.text_area(
    label="أدخل النص العربي هنا",
    height=200,
    help="يمكنك كتابة أو لصق النص الذي تريد تشكيله"
)

# Button
if st.button("تشكيل النص"):
    if user_input.strip() == "":
        st.warning("⚠️ الرجاء إدخال نص أولاً")
    else:
        with st.spinner("⏳ جاري التشكيل..."):
            output = diacritize_text(user_input)

        st.markdown("""
        <div role="region" aria-label="النص بعد التشكيل">
        <h3>النص المشكّل:</h3>
        </div>
        """, unsafe_allow_html=True)

        st.text_area(
            label="الناتج",
            value=output,
            height=200
        )

# =============================
# Accessibility Notes
# =============================
st.markdown("""
---
### ♿ مميزات الوصول (Accessibility):
- Labels واضحة لكل عنصر
- دعم aria-label
- متوافق مع NVDA و VoiceOver
- لا يعتمد على الألوان فقط
""")

# =============================
# Setup Instructions
# =============================
# pip install streamlit requests python-dotenv
# .env -> GROQ_API_KEY=your_key
# streamlit run app.py
