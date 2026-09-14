import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image

# Streamlit की तिजोरी (Secrets) से API Key को सुरक्षित तरीके से निकालना
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Settings में Secrets के अंदर GEMINI_API_KEY डालें।")

# Page Config
st.set_page_config(page_title="Swarika AI Checker", page_icon="📝")
st.title("📝 Swarika Playtime - AI Workbook Checker")
st.write("Active AI Worksheet Checking System (Powered by Gemini Vision)")

# Sidebar Details
st.sidebar.header("📋 Student Details")
school_name = st.sidebar.text_input("School Name", value="", placeholder="Enter School Name")
student_class = st.sidebar.selectbox("Class", ["Select Class", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
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
    
    if st.button("🚀 Check Worksheet with AI & Generate PDF"):
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
                    
                    st.info(f"🟢 Connected dynamically to model: **{chosen_model}**")
                    
                    model = genai.GenerativeModel(chosen_model)
                    
                    # 🎯 यहाँ हमने भाषा का निर्देश (Prompt) बदल दिया है
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
                    
                    # ऐप की स्क्रीन पर रिजल्ट दिखाना (यहाँ बिल्कुल सही हिंदी दिखेगी)
                    st.markdown("---")
                    st.subheader("📊 AI Evaluation Report")
                    st.write(ai_feedback)
                    
                    # PDF जनरेट करने का कोड
                    safe_feedback = ai_feedback.encode('latin-1', 'replace').decode('latin-1')
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, f"Swarika Playtime - AI Evaluation Report", 0, 1, 'C')
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(0, 10, f"School: {school_name}", 0, 1)
                    pdf.cell(0, 10, f"Class: {student_class} | Subject: {subject} | Worksheet: {worksheet_no}", 0, 1)
                    pdf.cell(0, 10, f"Student Name: {student_name}", 0, 1)
                    pdf.ln(10)
                    
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "AI Feedback & Corrections:", 0, 1)
                    pdf.set_font("Arial", '', 11)
                    
                    for line in safe_feedback.split('\n'):
                        pdf.multi_cell(0, 8, line)
                    
                    pdf.ln(15)
                    pdf.set_font("Arial", 'I', 10)
                    pdf.cell(0, 10, "Admin: DILIP KUMAR AGGRAWAL, LECTURER, GSSS PALSANA, SIKAR | Mob: 9462064244", 0, 1, 'C')

                    pdf_filename = f"{student_name}_Worksheet_{worksheet_no}_AI_Checked.pdf"
                    pdf.output(pdf_filename)
                    
                    st.success(f"✅ PDF Report Generated: {pdf_filename}")
                    
                    with open(pdf_filename, "rb") as file:
                        st.download_button(
                            label="📥 Download Checked PDF Report",
                            data=file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                        
                    st.info(f"WhatsApp Report ready to send to Parent at: {parent_whatsapp}")

                except Exception as e:
                    st.error(f"AI चेकिंग के दौरान एक एरर आ गया: {e}")
