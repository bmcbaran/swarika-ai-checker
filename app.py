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
school_name = st.sidebar.text_input("School Name", value="Govt Upper Primary School")
student_class = st.sidebar.selectbox("Class", ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"])
subject = st.sidebar.selectbox("Subject", ["Mathematics", "Science"])
worksheet_no = st.sidebar.text_input("Worksheet No.", value="7")
student_name = st.sidebar.text_input("Student Name", value="Hari")
parent_whatsapp = st.sidebar.text_input("Parent's WhatsApp No.", value="+919462064244")

# Admin Details in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**Admin Details:**")
st.sidebar.markdown("👨‍🏫 **DILIP KUMAR AGGRAWAL**")
st.sidebar.markdown("🏫 LECTURER, GSSS PALSANA, SIKAR")
st.sidebar.markdown("📞 Mobile No: 9462064244")

# Camera Section
st.subheader("📸 Capture Worksheet Photo")
worksheet_photo = st.file_uploader("📸 Take a photo or Upload Worksheet", type=['jpg', 'jpeg', 'png'])

if worksheet_photo is not None:
    st.success(f"Worksheet photo captured successfully for {student_name}!")
    
    # कैमरे की फोटो को पढ़ने लायक बनाना
    image = Image.open(worksheet_photo)
    
    if st.button("🚀 Check Worksheet with AI & Generate PDF"):
        with st.spinner("AI आपकी वर्कशीट को पढ़ रहा है और चेक कर रहा है... इसमें कुछ सेकंड लग सकते हैं⏳"):
            try:
                # Google Gemini 1.5 pro मॉडल चालू करना
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # AI को निर्देश (Prompt) देना - (यहाँ कोटेशन ठीक कर दिए गए हैं)
                prompt = """
                You are an expert mathematics teacher checking a student's worksheet.
                Please analyze the uploaded image of the worksheet.
                1. Identify the questions and the student's answers.
                2. Check if the answers are correct or incorrect.
                3. Provide a brief step-by-step solution for incorrect answers or a confirmation for correct ones.
                4. Give a final score based on correct answers out of total questions.
                
                IMPORTANT: Please provide the output ONLY in plain English text. Do NOT use emojis, bold (**), symbols, or special characters. Keep the text simple so it can be printed easily in a PDF.
                """
                
                # AI से रिजल्ट मांगना
                response = model.generate_content([prompt, image])
                ai_feedback = response.text
                
                # PDF में एरर न आए, इसलिए टेक्स्ट को सुरक्षित करना
                safe_feedback = ai_feedback.replace('*', '').replace('#', '').encode('latin-1', 'replace').decode('latin-1')

                # ऐप में रिजल्ट दिखाना
                st.markdown("---")
                st.subheader("📊 AI Evaluation Report")
                st.write(safe_feedback)
                
                # असली AI रिजल्ट से PDF जनरेट करना
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
                
                # AI के जवाब को PDF में लाइन-बाय-लाइन छापना
                for line in safe_feedback.split('\n'):
                    pdf.multi_cell(0, 8, line)
                
                # PDF के नीचे Admin का नाम जोड़ना
                pdf.ln(15)
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, "Admin: DILIP KUMAR AGGRAWAL, LECTURER, GSSS PALSANA, SIKAR | Mob: 9462064244", 0, 1, 'C')

                pdf_filename = f"{student_name}_Worksheet_{worksheet_no}_AI_Checked.pdf"
                pdf.output(pdf_filename)
                
                st.success(f"✅ PDF Report Generated: {pdf_filename}")
                
                # नया डाउनलोड बटन
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
