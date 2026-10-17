
import streamlit as st
import asyncio
import os
import re
from deep_translator import GoogleTranslator
import edge_tts

# إعدادات صفحة الموقع
st.set_page_config(page_title="Coursera Arabic Dubber", page_icon="🎧", layout="centered")

st.title("🎧 مدبلج ومساعد كورسيرا الذكي")
st.write("حمل ملف الترجمة (.vtt أو .txt) الخاص بكورسيرا، وحوله لصوت عربي بالهجة التي تحبها فوراً!")

# أصوات الذكاء الاصطناعي المتاحة
VOICES = {
    "فصحى - أنثى (رسمي وواضح)": "ar-SA-ZahraNeural",
    "فصحى - ذكر (رسمي وواضح)": "ar-SA-HamedNeural",
    "لهجة سورية - أنثى": "ar-SY-AmanyNeural",
    "لهجة سورية - ذكر": "ar-SY-LaithNeural",
    "لهجة مصرية - أنثى": "ar-EG-SalmaNeural",
    "لهجة مصرية - ذكر": "ar-EG-ShakirNeural"
}

# خيارات الواجهة
uploaded_file = st.file_uploader("📁 اختر ملف الترجمة (.vtt أو .txt)", type=['vtt', 'txt'])
selected_voice_name = st.selectbox("🎙️ اختر الصوت واللهجة:", list(VOICES.keys()))
translate_option = st.selectbox("🌐 لغة الملف:", ["نعم (ترجم من الإنجليزية للعربية)", "لا (النص عربي أصلاً)"])

async def generate_audio(text, voice_code, output_path):
    communicate = edge_tts.Communicate(text, voice_code)
    await communicate.save(output_path)

if uploaded_file is not None:
    if st.button("🚀 بدء التحويل وإنشاء ملف الصوت"):
        with st.spinner("جاري معالجة الملف، الترجمة، وتوليد الصوت... يرجى الانتظار ⏳"):
            try:
                # قراءة الملف المرفوع
                content = uploaded_file.read().decode("utf-8", errors="ignore")
                
                # تنظيف الملف إذا كان VTT
                if uploaded_file.name.endswith('.vtt') or '-->' in content:
                    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*', '', content)
                    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
                    content = re.sub(r'<[^>]+>', '', content)
                
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                clean_text = " ".join(lines)
                
                if not clean_text:
                    st.error("الملف فارغ أو لم يتم العثور على نصوص داخله!")
                else:
                    # الترجمة إذا طُلب ذلك
                    if "نعم" in translate_option:
                        chunks = [clean_text[i:i+4000] for i in range(0, len(clean_text), 4000)]
                        translator = GoogleTranslator(source='en', target='ar')
                        translated = [translator.translate(chunk) for chunk in chunks]
                        final_text = " ".join(translated)
                    else:
                        final_text = clean_text
                    
                    # مسار الحفظ المؤقت
                    output_mp3 = "coursera_dubbed.mp3"
                    voice_code = VOICES[selected_voice_name]
                    
                    # تنفيذ التوليد بشكل غير متزامن
                    asyncio.run(generate_audio(final_text, voice_code, output_mp3))
                    
                    st.success("تم تحويل الكورس وصنع الملف الصوتي بنجاح! 🎉")
                    
                    # مشغل صوت مدمج داخل الموقع
                    st.audio(output_mp3, format='audio/mp3')
                    
                    # زر لتحميل الملف مباشرة لهاتفك
                    with open(output_mp3, "rb") as f:
                        st.download_button(
                            label="📥 تحميل ملف MP3 على هاتفك",
                            data=f,
                            file_name="coursera_arabic_audio.mp3",
                            mime="audio/mp3"
                        )
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")

# --- قسم الملاحظات السريعة ---
st.markdown("---")
st.subheader("📝 مفكرة أفكار الكورس السريعة")
note_text = st.text_area("اكتب ملاحظاتك أثناء الاستماع للشرح:")
if st.button("حفظ الملاحظة"):
    if note_text:
        st.download_button(
            label="💾 تحميل ملف الملاحظات (TXT)",
            data=note_text,
            file_name="My_Coursera_Notes.txt",
            mime="text/plain"
        )
        st.success("الملاحظة جاهزة للتحميل كملف نصي على هاتفك!")
    else:
        st.warning("اكتب شيئاً في الملاحظات أولاً.")
