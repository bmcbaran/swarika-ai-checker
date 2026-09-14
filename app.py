import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import textwrap

# 1. Streamlit की तिजोरी (Secrets) से API Key निकालना
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Settings में Secrets के अंदर GEMINI_API_KEY डालें।")

# 2. हिंदी फॉन्ट (Hindi Font) को ऑटोमैटिक डाउनलोड करना
font_path = "NotoSansDevanagari.ttf"
if not os.path.exists(font_path):
    with st.spinner("हिंदी फॉन्ट सेट किया जा रहा है..."):
        url = "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf"
        try:
            response = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except:
            pass # अगर फेल हुआ तो डिफ़ॉल्ट इंग्लिश फॉन्ट इस्तेमाल होगा

# Page Config
st.set_page_config(page_title="Swarika AI Checker", page_icon="📝")
st.title("📝 Swarika Playtime - AI Workbook Checker")
st.write("Active AI Worksheet Checking System")

# Sidebar Details
st.sidebar.header("📋 Student Details")
school_name = st.sidebar.text_input("School Name", value="", placeholder="Enter School Name")
student_class = st.sidebar.selectbox("Class", ["Select Class", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"])
subject = st.sidebar.selectbox("Subject", ["Select Subject", "Mathematics", "Science"])
worksheet_no = st.sidebar.text_input("Worksheet No.", value="", placeholder="e.g. 7")
student_name = st.sidebar.text_input("Student Name", value="", placeholder="Enter Student Name")
parent_whatsapp = st.sidebar.text_input("Parent's WhatsApp No.", value="", placeholder="e.g. +919462064244")

# Admin Details
st.sidebar.markdown("---")
st.sidebar.markdown("**Admin Details:**")
st.sidebar.markdown("👨‍🏫 **DILIP KUMAR AGGRAWAL**")
st.sidebar.markdown("🏫 LECTURER, GSSS PALSANA, SIKAR")
st.sidebar.markdown("📞 Mobile No: 9462064244")

# Camera Section
st.subheader("📸 Capture Worksheet Photo")
worksheet_photo = st.file_uploader("📸 Take a photo or Upload Worksheet", type=['jpg', 'jpeg', 'png'])

if worksheet_photo is not None:
    st.success("Worksheet photo captured successfully!")
    image = Image.open(worksheet_photo)
    
    if st.button("🚀 Check Worksheet with AI & Generate Report"):
        if not student_name or student_class == "Select Class":
            st.warning("⚠️ कृपया साइडबार में स्टूडेंट का नाम और क्लास भरें!")
        else:
            with st.spinner("AI आपकी वर्कशीट को पढ़ रहा है और चेक कर रहा है... इसमें कुछ सेकंड लग सकते हैं⏳"):
                try:
                    # 🚀 AUTO-DYNAMIC MODEL FINDER
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if 'models/gemini-flash-latest' in available_models:
                        chosen_model = 'gemini-flash-latest'
                    else:
                        flash_models = [m for m in available_models if 'flash' in m and 'preview' not in m and 'lite' not in m]
                        if flash_models:
                            chosen_model = sorted(flash_models)[-1].replace('models/', '')
                        elif available_models:
                            chosen_model = available_models[-1].replace('models/', '')
                        else:
                            chosen_model = 'gemini-1.5-flash'
                    
                    st.info(f"🟢 Connected to AI Model: {chosen_model}")
                    model = genai.GenerativeModel(chosen_model)
                    
                    prompt = """
                    You are an expert teacher checking a student's worksheet.
                    Please analyze the uploaded image of the worksheet.
                    1. Identify the questions and the student's answers.
                    2. Check if the answers are correct or incorrect.
                    3. Provide a brief step-by-step solution for incorrect answers or a confirmation for correct ones.
                    4. Give a final score.
                    
                    CRITICAL LANGUAGE INSTRUCTION:
                    You MUST respond in the EXACT SAME LANGUAGE that is used in the worksheet. 
                    - If the worksheet is in Hindi, your entire feedback MUST be in proper Hindi language.
                    - If the worksheet is in English, reply in English.
                    
                    IMPORTANT: Do NOT use emojis, bold (**), symbols, or special characters. Keep the text simple.
                    """
                    
                    response = model.generate_content([prompt, image])
                    ai_feedback = response.text.replace('*', '').replace('#', '')

                    st.markdown("---")
                    st.subheader("📊 AI Evaluation Report")
                    st.write(ai_feedback)
                    
                    # ==========================================
                    # 1. PDF GENERATION (विशुद्ध हिंदी के साथ)
                    # ==========================================
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # फॉन्ट सेट करना
                    if os.path.exists(font_path):
                        pdf.add_font("HindiFont", fname=font_path)
                        pdf.set_font("HindiFont", size=16)
                    else:
                        pdf.set_font("Arial", size=16)
                        
                    pdf.cell(0, 10, "Swarika Playtime - AI Evaluation Report", ln=True, align='C')
                    
                    if os.path.exists(font_path):
                        pdf.set_font("HindiFont", size=12)
                    else:
                        pdf.set_font("Arial", size=12)
                        
                    pdf.cell(0, 10, f"School: {school_name}", ln=True)
                    pdf.cell(0, 10, f"Name: {student_name} | Class: {student_class} | Subject: {subject}", ln=True)
                    pdf.cell(0, 10, "-"*60, ln=True)
                    
                    # हिंदी टेक्स्ट को लाइन-बाय-लाइन लिखना
                    for line in ai_feedback.split('\n'):
                        pdf.multi_cell(0, 8, line)
                        
                    pdf.ln(10)
                    pdf.cell(0, 10, "Admin: DILIP KUMAR AGGRAWAL, LECTURER, GSSS PALSANA, SIKAR | Mob: 9462064244", ln=True, align='C')
                    
                    pdf_filename = f"{student_name}_Report.pdf"
                    pdf.output(pdf_filename)

                    # ==========================================
                    # 2. JPG (IMAGE) GENERATION (WhatsApp के लिए)
                    # ==========================================
                    img_width = 800
                    lines_to_draw = []
                    lines_to_draw.append(("Swarika Playtime - AI Evaluation Report", 26))
                    lines_to_draw.append((f"Name: {student_name} | Class: {student_class} | Subject: {subject}", 20))
                    lines_to_draw.append(("-"*70, 20))
                    
                    # टेक्स्ट को इमेज के हिसाब से काटना (Wrap text)
                    for paragraph in ai_feedback.split('\n'):
                        wrapped = textwrap.wrap(paragraph, width=60)
                        for w in wrapped:
                            lines_to_draw.append((w, 20))
                        lines_to_draw.append(("", 20)) # पैराग्राफ के बीच खाली जगह
                        
                    lines_to_draw.append(("-"*70, 20))
                    lines_to_draw.append(("Admin: DILIP KUMAR AGGRAWAL, LECTURER, GSSS PALSANA", 18))
                    
                    # इमेज की ऊंचाई (Height) तय करना
                    img_height = 100 + (len(lines_to_draw) * 32)
                    result_img = Image.new('RGB', (img_width, img_height), color='white')
                    draw = ImageDraw.Draw(result_img)
                    
                    # इमेज में फॉन्ट लोड करना
                    try:
                        font_regular = ImageFont.truetype(font_path, 22)
                        font_bold = ImageFont.truetype(font_path, 28)
                    except:
                        font_regular = ImageFont.load_default()
                        font_bold = ImageFont.load_default()
                        
                    # इमेज पर टेक्स्ट लिखना
                    y_text = 40
                    for text, size in lines_to_draw:
                        f = font_bold if size == 28 else font_regular
                        draw.text((40, y_text), text, font=f, fill='black')
                        y_text += 32
                        
                    jpg_filename = f"{student_name}_Report.jpg"
                    result_img.save(jpg_filename)

                    # ==========================================
                    # 3. डाउनलोड बटन (PDF और JPG दोनों के लिए)
                    # ==========================================
                    st.success("✅ शानदार! रिपोर्ट PDF और JPG (फोटो) दोनों में तैयार है।")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with open(pdf_filename, "rb") as file:
                            st.download_button(label="📄 Download PDF", data=file, file_name=pdf_filename, mime="application/pdf")
                    with col2:
                        with open(jpg_filename, "rb") as file:
                            st.download_button(label="🖼️ Download JPG (Photo)", data=file, file_name=jpg_filename, mime="image/jpeg")
                            
                    st.info(f"📲 WhatsApp Report ready to send to Parent at: {parent_whatsapp}")

                except Exception as e:
                    st.error(f"AI चेकिंग के दौरान एक एरर आ गया: {e}")
