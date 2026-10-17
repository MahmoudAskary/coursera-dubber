import streamlit as st
import asyncio
import os
import re
import base64
from deep_translator import GoogleTranslator
import edge_tts

# إعدادات الصفحة
st.set_page_config(page_title="Coursera Cyber Studio", page_icon="🚀", layout="centered")

# --- تصميم الواجهة الأسطورية (Dark Mode + Custom CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #090d16;
        color: #f8fafc;
    }
    .main-header {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        height: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚀 Coursera Cyber Study Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">منصة الدبلجة والتتبع الصوتي الذكي - النسخة الاحترافية الداكنة</div>', unsafe_allow_html=True)

# أصوات الذكاء الاصطناعي
VOICES = {
    "فصحى - أنثى (رسمي وواضح)": "ar-SA-ZahraNeural",
    "فصحى - ذكر (رسمي وواضح)": "ar-SA-HamedNeural",
    "لهجة سورية - أنثى": "ar-SY-AmanyNeural",
    "لهجة سورية - ذكر": "ar-SY-LaithNeural",
    "لهجة مصرية - أنثى": "ar-EG-SalmaNeural",
    "لهجة مصرية - ذكر": "ar-EG-ShakirNeural"
}

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header("⚙️ إعدادات الاستوديو")
    selected_voice_name = st.selectbox("🎙️ اختر الصوت واللهجة:", list(VOICES.keys()))
    translate_option = st.selectbox("🌐 لغة الملف:", ["نعم (ترجم من الإنجليزية للعربية)", "لا (النص عربي أصلاً)"])
    st.markdown("---")
    st.markdown("💡 **تعليمات الاستخدام:**\n1. ارفع ملف الترجمة `.vtt` أو `.txt`.\n2. اضغط بدء المعالجة.\n3. استخدم **مشغل التتبع التفاعلي** لقراءة النص وتغيير لونه تلقائياً مع الصوت!")

uploaded_file = st.file_uploader("📁 ارفع ملف الترجمة هنا", type=['vtt', 'txt'])

def parse_subtitles(content, file_name):
    segments = []
    if file_name.endswith('.vtt') or '-->' in content:
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if '-->' in line:
                parts = line.split('-->')
                def time_to_sec(t_str):
                    try:
                        t_parts = t_str.strip().split(':')
                        h = int(t_parts[0])
                        m = int(t_parts[1])
                        s_ms = t_parts[2].split('.')
                        return h * 3600 + m * 60 + int(s_ms[0]) + int(s_ms[1]) / 1000.0
                    except:
                        return 0.0
                
                start_sec = time_to_sec(parts[0])
                end_sec = time_to_sec(parts[1])
                
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                    clean_l = re.sub(r'<[^>]+>', '', lines[i].strip())
                    if clean_l:
                        text_lines.append(clean_l)
                    i += 1
                txt = " ".join(text_lines)
                if txt:
                    segments.append({'start': start_sec, 'end': end_sec if end_sec > start_sec else start_sec + 4.0, 'text': txt})
            else:
                i += 1
    
    # لو الملف نصي عادي بدون تواقيت (TXT)
    if not segments:
        clean_content = re.sub(r'<[^>]+>', '', content)
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', clean_content) if s.strip()]
        current_time = 0.0
        for sent in sentences:
            duration = max(3.0, len(sent.split()) * 0.4) # تقدير زمني تقريبي
            segments.append({'start': current_time, 'end': current_time + duration, 'text': sent})
            current_time += duration
            
    return segments

async def generate_audio(text, voice_code, output_path):
    communicate = edge_tts.Communicate(text, voice_code)
    await communicate.save(output_path)

if uploaded_file is not None:
    raw_content = uploaded_file.read().decode("utf-8", errors="ignore")
    segments = parse_subtitles(raw_content, uploaded_file.name)
    
    if not segments:
        st.error("⚠️ لم يتم العثور على نصوص صالحة في الملف.")
    else:
        if st.button("⚡ بدء معالجة وتوليد الاستوديو الذكي"):
            with st.spinner("🔄 جاري الترجمة، ضبط التواقيت الزمنية، وتوليد الصوت النقي..."):
                try:
                    translator = GoogleTranslator(source='en', target='ar') if "نعم" in translate_option else None
                    
                    full_text_list = []
                    for seg in segments:
                        txt = seg['text']
                        if translator:
                            try:
                                txt = translator.translate(txt)
                            except:
                                pass
                        seg['ar_text'] = txt
                        full_text_list.append(txt)
                    
                    st.session_state['segments'] = segments
                    
                    output_mp3 = "coursera_studio.mp3"
                    voice_code = VOICES[selected_voice_name]
                    combined_text = " ".join(full_text_list)
                    
                    asyncio.run(generate_audio(combined_text, voice_code, output_mp3))
                    st.session_state['studio_ready'] = True
                    st.success("✨ تم إنشاء الاستوديو الصوتي والتزمني بنجاح!")
                except Exception as e:
                    st.error(f"خطأ في المعالجة: {str(e)}")

        # --- واجهة الاستوديو والتتبع التفاعلي المخصصة وقت تشغيل الصوت ---
        if 'studio_ready' in st.session_state and st.session_state['studio_ready']:
            st.markdown("---")
            st.markdown("### 🎧 استوديو المتابعة والتتبع اللحظي")
            
            # قراءة ملف الصوت وتحويله لـ Base64 لضمان عمله بسلاسة داخل المكون التفاعلي
            audio_path = "coursera_studio.mp3"
            if os.path.exists(audio_path):
                with open(audio_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                import json
                segments_json = json.dumps(st.session_state['segments'], ensure_ascii=False)
                
                # تضمين مشغل تفاعلي ذكي بـ HTML, CSS, و JavaScript لتغيير الألوان والقفز الزمني
                player_html = f"""
                <!DOCTYPE html>
                <html lang="ar" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            background-color: #0b1120;
                            color: #f1f5f9;
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            margin: 0;
                            padding: 15px;
                        }}
                        .player-container {{
                            background: linear-gradient(145deg, #131d31, #0f172a);
                            border: 1px solid #1e293b;
                            border-radius: 16px;
                            padding: 20px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                        }}
                        audio {{
                            width: 100%;
                            border-radius: 8px;
                            outline: none;
                            filter: invert(100%) hue-rotate(180deg) brightness(95%);
                        }}
                        .transcript-box {{
                            margin-top: 20px;
                            max-height: 350px;
                            overflow-y: auto;
                            padding-right: 5px;
                            scroll-behavior: smooth;
                        }}
                        .transcript-box::-webkit-scrollbar {{
                            width: 6px;
                        }}
                        .transcript-box::-webkit-scrollbar-thumb {{
                            background: #334155;
                            border-radius: 4px;
                        }}
                        .sub-item {{
                            padding: 12px 16px;
                            margin-bottom: 10px;
                            border-radius: 10px;
                            background-color: rgba(30, 41, 59, 0.5);
                            border: 1px solid rgba(51, 65, 85, 0.4);
                            cursor: pointer;
                            transition: all 0.25s ease;
                            font-size: 16px;
                            line-height: 1.6;
                        }}
                        .sub-item:hover {{
                            background-color: rgba(51, 65, 85, 0.8);
                        }}
                        .sub-item.active {{
                            background-color: rgba(6, 182, 212, 0.15);
                            border-color: #06b6d4;
                            color: #22d3ee;
                            box-shadow: 0 0 15px rgba(6, 182, 212, 0.25);
                            transform: scale(1.01);
                        }}
                    </style>
                </head>
                <body>
                    <div class="player-container">
                        <audio id="audioPlayer" controls>
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            متصفحك لا يدعم تشغيل الصوت.
                        </audio>
                        <div class="transcript-box" id="transcriptBox"></div>
                    </div>

                    <script>
                        const segments = {segments_json};
                        const audio = document.getElementById('audioPlayer');
                        const box = document.getElementById('transcriptBox');
                        
                        // بناء قائمة النصوص تفاعلياً
                        segments.forEach((seg, index) => {{
                            const div = document.createElement('div');
                            div.className = 'sub-item';
                            div.id = 'seg-' + index;
                            div.innerText = seg.ar_text;
                            div.onclick = () => {{
                                audio.currentTime = seg.start;
                                audio.play();
                            }};
                            box.appendChild(div);
                        }});

                        let activeIndex = -1;
                        audio.addEventListener('timeupdate', () => {{
                            const t = audio.currentTime;
                            let currentIdx = segments.findIndex(s => t >= s.start && t <= s.end);
                            
                            if (currentIdx !== -1 && currentIdx !== activeIndex) {{
                                if (activeIndex !== -1) {{
                                    document.getElementById('seg-' + activeIndex).classList.remove('active');
                                }}
                                activeIndex = currentIdx;
                                const activeEl = document.getElementById('seg-' + activeIndex);
                                activeEl.classList.add('active');
                                activeEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }}
                        }});
                    </script>
                </body>
                </html>
                """
                
                # عرض الاستوديو التفاعلي عبر مكون HTML مخصص داخل Streamlit
                st.components.v1.html(player_html, height=480)
                
                # زر تحميل إضافي
                with open(audio_path, "rb") as f:
                    st.download_button(
                        label="📥 تحميل ملف الصوت MP3 بصيغة نهائية",
                        data=f,
                        file_name="Coursera_Dubbed_Studio.mp3",
                        mime="audio/mp3"
                    )

# --- مفكرة المهندس الذكية الداكنة ---
st.markdown("---")
st.markdown("### 📝 مفكرة الأفكار التقنية")
note_text = st.text_area("سجل ملاحظاتك وبرمجياتك أثناء متابعة الكورس:", placeholder="اكتب ملاحظاتك هنا...")
if st.button("حفظ وتنزيل الملاحظات الشخصية"):
    if note_text:
        st.download_button(
            label="💾 تحميل ملف الملاحظات (TXT)",
            data=note_text,
            file_name="My_Study_Notes.txt",
            mime="text/plain"
        )
        st.success("تم تجهيز ملف الملاحظات للتحميل!")
    else:
        st.warning("يرجى كتابة ملاحظة أولاً.")
