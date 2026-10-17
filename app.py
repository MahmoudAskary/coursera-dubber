import streamlit as st
import asyncio
import os
import re
from deep_translator import GoogleTranslator
import edge_tts

# إعدادات صفحة الموقع بتصميم نظيف
st.set_page_config(page_title="Coursera Pro Study Companion", page_icon="🎓", layout="centered")

# تصميم وتنسيق بصري احترافي عبر CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 15px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 منصة كورسيرا الذكية للدراسة والتتبع الصوتي</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">حول ملفات الشرح إلى دبلجة عربية، تابع النص بصرياً، ودرس باحترافية من هاتفك!</div>', unsafe_allow_html=True)

# أصوات الذكاء الاصطناعي المتاحة
VOICES = {
    "فصحى - أنثى (رسمي وواضح)": "ar-SA-ZahraNeural",
    "فصحى - ذكر (رسمي وواضح)": "ar-SA-HamedNeural",
    "لهجة سورية - أنثى": "ar-SY-AmanyNeural",
    "لهجة سورية - ذكر": "ar-SY-LaithNeural",
    "لهجة مصرية - أنثى": "ar-EG-SalmaNeural",
    "لهجة مصرية - ذكر": "ar-EG-ShakirNeural"
}

# شريط جانبي (Sidebar) للتحكم المنظم
with st.sidebar:
    st.header("⚙️ إعدادات التحويل")
    selected_voice_name = st.selectbox("🎙️ اختر الصوت واللهجة:", list(VOICES.keys()))
    translate_option = st.selectbox("🌐 لغة الملف:", ["نعم (ترجم من الإنجليزية للعربية)", "لا (النص عربي أصلاً)"])
    st.markdown("---")
    st.info("💡 **نصيحة دراسية:** افتح فيديو الكورس على شاشة ونصف الشاشة، واجعل هذا التطبيق في النصف الآخر لتستمع وتتابع النص بتركيز.")

# رفع الملف
uploaded_file = st.file_uploader("📁 اختر ملف الترجمة (.vtt أو .txt) الخاص بالكورس", type=['vtt', 'txt'])

async def generate_audio(text, voice_code, output_path):
    communicate = edge_tts.Communicate(text, voice_code)
    await communicate.save(output_path)

if uploaded_file is not None:
    # قراءة وتنظيف الملف
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    
    if uploaded_file.name.endswith('.vtt') or '-->' in content:
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*', '', content)
        content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'<[^>]+>', '', content)
    
    raw_lines = [line.strip() for line in content.split('\n') if line.strip()]
    clean_text = " ".join(raw_lines)

    if not clean_text:
        st.error("⚠️ الملف فارغ أو لم يتم العثور على نصوص داخله!")
    else:
        # زر البدء بالمعالجة
        if st.button("🚀 معالجة وترجمة وتوليد الصوت الآن"):
            with st.spinner("⏳ جاري تنظيف النص، الترجمة، وتوليد الصوت بدقة عالية..."):
                try:
                    if "نعم" in translate_option:
                        chunks = [clean_text[i:i+4000] for i in range(0, len(clean_text), 4000)]
                        translator = GoogleTranslator(source='en', target='ar')
                        translated = [translator.translate(chunk) for chunk in chunks]
                        final_text = " ".join(translated)
                    else:
                        final_text = clean_text
                    
                    # حفظ النصوص في الذاكرة المؤقتة للجلسة
                    st.session_state['final_text'] = final_text
                    
                    output_mp3 = "coursera_dubbed.mp3"
                    voice_code = VOICES[selected_voice_name]
                    
                    asyncio.run(generate_audio(final_text, voice_code, output_mp3))
                    st.session_state['audio_ready'] = True
                    st.success("🎉 تم تحويل الكورس وصنع الملف الصوتي بنجاح تام!")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")

        # إذا تم تجهيز النص والصوت، نعرض الميزات المتقدمة للتتبع والدراسة
        if 'audio_ready' in st.session_state and st.session_state['audio_ready']:
            st.markdown("---")
            st.subheader("🎧 مشغل الصوت المدمج")
            st.audio("coursera_dubbed.mp3", format='audio/mp3')
            
            with open("coursera_dubbed.mp3", "rb") as f:
                st.download_button(
                    label="📥 تحميل ملف MP3 للاستماع في أي وقت",
                    data=f,
                    file_name="coursera_arabic_audio.mp3",
                    mime="audio/mp3"
                )
            
            st.markdown("---")
            st.subheader("📖 عارض النص التفاعلي (للقراءة والتتبع أثناء الاستماع)")
            
            # ميزة البحث السريع داخل النص
            search_query = st.text_input("🔍 البحث عن كلمة أو مفهوم داخل الشرح:")
            display_text = st.session_state['final_text']
            
            if search_query:
                st.info(f"نتائج البحث عن: '{search_query}'")
                # إبراز النص أو تصفيته
                paragraphs = [p for p in display_text.split('.') if search_query.lower() in p.lower()]
                formatted_text = ". ".join(paragraphs) if paragraphs else "لم يتم العثور على الكلمة في النص."
            else:
                formatted_text = display_text

            # صندوق قراءة منسق ومرتب
            st.text_area("النص المعالج (جاهز للقراءة والمتابعة):", formatted_text, height=250)

# --- قسم المفكرة الدراسية المتقدمة ---
st.markdown("---")
st.subheader("📝 مفكرة المهندس والملاحظات السريعة")
note_text = st.text_area("سجل الأفكار، القوانين، أو الملاحظات الهامة أثناء متابعة الكورس هنا:")
if st.button("حفظ وتنزيل الملاحظات"):
    if note_text:
        st.download_button(
            label="💾 تحميل ملف الملاحظات الشخصي (TXT)",
            data=note_text,
            file_name="My_Study_Notes.txt",
            mime="text/plain"
        )
        st.success("الملاحظات جاهزة للتحميل على هاتفك!")
    else:
        st.warning("اكتب شيئاً في المفكرة أولاً.")
        
