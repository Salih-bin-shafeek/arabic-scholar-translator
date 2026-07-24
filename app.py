import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import re

# 1. Page Configuration
st.set_page_config(page_title="Arabic Scholar Translator", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS to match the Figma design exactly
st.markdown("""
    <style>
    /* Main background color and font */
    .stApp {
        background-color: #F9F8F6;
        color: #333333;
        font-family: 'Georgia', serif;
    }
    
    /* Center the main headers */
    h1, h2, h3 {
        text-align: center;
        font-family: 'Georgia', serif;
        color: #2C2A25;
    }
    
    /* Style the file uploader to look like the drag-and-drop box */
    [data-testid="stFileUploadDropzone"] {
        background-color: transparent;
        border: 2px dashed #D3CABC;
        border-radius: 10px;
        padding: 40px;
    }
    
    /* Style the tabs to match the minimalist buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #E5E0D8;
        border-radius: 8px;
        padding: 10px 20px;
        color: #555555;
        font-size: 14px;
        font-family: 'Arial', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FAF9F6;
        border-bottom: 2px solid #8C7C61;
        color: #2C2A25;
        font-weight: bold;
    }
    
    /* Style text areas and outputs */
    .stMarkdown {
        font-size: 18px;
        line-height: 1.8;
    }
    
    /* Custom font for Arabic text */
    .arabic-text {
        font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
        font-size: 28px;
        text-align: center;
        direction: rtl;
        line-height: 2.5;
    }
    </style>
""", unsafe_allow_html=True)


# 3. Agent Prompt (from your previous setup)
AGENT_PROMPT = """Role: You are an expert Arabic Scholar, Classical Translator, and Spiritual Islamic Teacher. 
Goal: Help the user study classical Arabic texts, tafsir, hadith, and spiritual works line-by-line using an exhaustive, beginner-friendly format.

Rules & Output Format:
For every image, text snippet, or passage uploaded/shared by the user, you MUST respond using the exact 6-part structure below. Use these exact headings:

Section 1: Complete Text with Tashkeel
Section 2: Word-for-Word Literal Translation
Section 3: Natural Line-by-Line Translation
Section 4: Conceptual & Spiritual Insights
Section 5: Grammatical Breakdown (Iʿrāb & Tarkīb)
Section 6: Complete Exhaustive Vocabulary List"""

# 4. Helper Function to parse the 6 sections
def parse_analysis(text):
    """Splits the Gemini output into the 6 distinct tabs."""
    sections = {
        "text": "", "word_for_word": "", "line_by_line": "", 
        "insights": "", "grammar": "", "vocabulary": ""
    }
    
    # Simple regex to split by the section headers defined in the prompt
    split_text = re.split(r'Section \d:', text)
    
    if len(split_text) >= 7:
        sections["text"] = split_text[1].strip()
        sections["word_for_word"] = split_text[2].strip()
        sections["line_by_line"] = split_text[3].strip()
        sections["insights"] = split_text[4].strip()
        sections["grammar"] = split_text[5].strip()
        sections["vocabulary"] = split_text[6].strip()
    else:
        # Fallback if the model misses the exact headings
        sections["text"] = text
        
    return sections

# 5. UI Layout
st.markdown("<h1>Arabic Scholar Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Upload an image of any Arabic text and receive a complete 6-part scholarly analysis.</p>", unsafe_allow_html=True)

# Hidden API key input for security, or place it in a sidebar
with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")

st.write("") # Spacer
st.write("")

# Centered upload area
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg", "webp"])

# Processing and Output
if uploaded_file:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    else:
        # Show a small preview of the uploaded image
        st.image(uploaded_file, width=150)
        st.markdown("<h3 style='text-align:center;'>Analyzing your text...</h3>", unsafe_allow_html=True)
        
        with st.spinner("Applying all 6 scholarly sections..."):
            try:
                client = genai.Client(api_key=api_key)
                image = PIL.Image.open(uploaded_file)
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=[image, "Please analyze this text according to your instructions."],
                    config=types.GenerateContentConfig(
                        system_instruction=AGENT_PROMPT,
                        temperature=0.2,
                    )
                )
                
                # Parse the response into the 6 variables
                parsed_data = parse_analysis(response.text)
                
                # Create the UI Tabs matching the Figma design
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "Complete Text", 
                    "Word-for-Word", 
                    "Line-by-Line", 
                    "Insights", 
                    "Grammar", 
                    "Vocabulary"
                ])
                
                with tab1:
                    st.markdown("### Complete Text with Tashkeel")
                    st.markdown(f"<div class='arabic-text'>{parsed_data['text']}</div>", unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### Word-for-Word Literal Translation")
                    st.markdown(parsed_data['word_for_word'])
                    
                with tab3:
                    st.markdown("### Natural Line-by-Line Translation")
                    st.markdown(parsed_data['line_by_line'])
                    
                with tab4:
                    st.markdown("### Conceptual & Spiritual Insights")
                    st.markdown(parsed_data['insights'])
                    
                with tab5:
                    st.markdown("### Grammatical Breakdown (Iʿrāb & Tarkīb)")
                    st.markdown(parsed_data['grammar'])
                    
                with tab6:
                    st.markdown("### Complete Exhaustive Vocabulary List")
                    st.markdown(parsed_data['vocabulary'])
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
