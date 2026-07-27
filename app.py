import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io
import re

# 1. Page Configuration
st.set_page_config(
    page_title="Arabic Scholar Translator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Dark Mode Purple Gradient CSS
st.markdown("""
    <style>
    /* Hide Streamlit default top header (Fork / GitHub icons) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0px;
    }
    footer {
        visibility: hidden;
    }
    
    /* Main Background: Dark Purple Gradient */
    .stApp {
        background: linear-gradient(135deg, #120A2A 0%, #200B3B 50%, #360940 100%);
        color: #FFFFFF;
        font-family: 'Georgia', serif;
    }
    
    /* Center and color main headers */
    h1, h2, h3 {
        text-align: center;
        font-family: 'Georgia', serif;
        color: #F3E8FF !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
    }
    
    p, span, label {
        color: #E2D9F3 !important;
    }
    
    /* File Uploader styling */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed #9333EA !important;
        border-radius: 12px;
        padding: 30px;
    }
    
    /* Style Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 10px 20px;
        color: #D8B4FE !important;
        font-size: 14px;
        font-family: 'Arial', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7E22CE !important;
        border: 1px solid #A855F7 !important;
        color: #FFFFFF !important;
        font-weight: bold;
    }
    
    /* Custom font and layout for Arabic text */
    .arabic-text {
        font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
        font-size: 32px;
        text-align: center;
        direction: rtl;
        line-height: 2.5;
        color: #FAF5FF;
        background: rgba(0, 0, 0, 0.2);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(168, 85, 247, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #9333EA;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #A855F7;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.6);
    }
    </style>
""", unsafe_allow_html=True)


# 3. Agent System Prompt
AGENT_PROMPT = """SYSTEM INSTRUCTION: ARABIC LINGUISTIC & SPIRITUAL ANALYSIS AGENT

ROLE AND PURPOSE:
You are an expert Arabic Scholar, Classical Translator, and Spiritual Islamic Teacher. Your goal is to provide a rigorous, exhaustive, and beginner-friendly linguistic and spiritual analysis of uploaded classical Arabic texts using English as the primary language of instruction.

CORE DIRECTIVE & OUTPUT STRUCTURE:
For every image, Arabic text passage, or excerpt provided by the user, you MUST generate your output strictly adhering to the following 6-part structure in exact sequence. Do not skip or combine any sections.

---

Section 1: Complete Text with Tashkeel
- Reproduce the complete Arabic text with full vocalization (Tashkeel / Harakat) on every letter for accurate recitation.

Section 2: Word-for-Word Literal Translation
- Break down the Arabic text word-by-word, prefix-by-prefix, and particle-by-particle.
- Map every individual Arabic word directly to its literal English counterpart.
- Format as a clear bulleted or line-by-line list.

Section 3: Natural Line-by-Line Translation
- Provide a fluent, natural, and idiomatic English translation.
- Maintain full fidelity to the context and spiritual depth of the Arabic text.

Section 4: Conceptual & Spiritual Insights
- Provide concise, profound spiritual, theological, or pedagogical lessons.
- All insights MUST be strictly rooted in and derived directly from the provided text.

Section 5: Grammatical Breakdown (Iʿrāb & Tarkīb)
- Explain the Arabic grammatical mechanics (Iʿrāb) using clear English explanations alongside standard Arabic technical terms (e.g., Mubtada', Khabar, Fiʿl, Fāʿil, Mafʿūl, Ḥarf Jarr).

Section 6: Complete Exhaustive Vocabulary List (al-Mufradāt)
- Provide a comprehensive Markdown table containing EVERY SINGLE UNIQUE WORD from the Arabic passage.
- Do NOT abbreviate, truncate, or select only "key" terms. Every word must be listed.
- Table Columns:
  1. Word in Text (As it appears in the passage, vocalized)
  2. Root (Jadhr - 3-letter system)
  3. Verb Forms / Conjugation (Past / Present / Future or Imperative - Māḍī, Muḍāriʿ, Amr, where applicable; indicate N/A for non-verbs)
  4. Meaning in Context
  5. Grammatical Type (e.g., Ism, Fiʿl Form I–X, Ḥarf, Active Participle, Verbal Noun/Maṣdar)

---

STRICT BEHAVIORAL RULES:
1. INSTRUCTION LANGUAGE: Strictly use English for all explanations, translations, and grammatical terms.
2. EXHAUSTIVE VOCABULARY RULE: The vocabulary table in Section 6 MUST include every single word from the text, explicitly detailing its form in the text, root, past/present/future forms (if a verb/derived noun), context meaning, and type.
3. PEDAGOGICAL TONE: Maintain an encouraging, scholarly, and spiritually grounded tone.
4. PRESERVE THE RULES: Always remain locked into this exact 6-part framework."""


@st.cache_data
def process_uploaded_bytes(file_bytes):
    return PIL.Image.open(io.BytesIO(file_bytes))


def parse_analysis(text):
    """Splits the Gemini output into the 6 distinct tabs."""
    sections = {
        "text": "", "word_for_word": "", "line_by_line": "", 
        "insights": "", "grammar": "", "vocabulary": ""
    }
    
    split_text = re.split(r'Section \d:', text)
    
    if len(split_text) >= 7:
        sections["text"] = split_text[1].strip()
        sections["word_for_word"] = split_text[2].strip()
        sections["line_by_line"] = split_text[3].strip()
        sections["insights"] = split_text[4].strip()
        sections["grammar"] = split_text[5].strip()
        sections["vocabulary"] = split_text[6].strip()
    else:
        sections["text"] = text
        
    return sections


# 4. Header Section
st.markdown("<h1>Arabic Scholar Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px;'>Upload an image of any Arabic text and receive a complete 6-part scholarly analysis.</p>", unsafe_allow_html=True)

# API Key handling
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# Centered upload area
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg", "webp"])

# Processing Section
if uploaded_file:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar or Streamlit Secrets.")
    else:
        file_bytes = uploaded_file.getvalue()
        image = process_uploaded_bytes(file_bytes)
        
        st.image(image, width=200)
        
        if st.button("Analyze Document", type="primary"):
            st.markdown("<h3 style='text-align:center;'>Analyzing your text...</h3>", unsafe_allow_html=True)
            
            with st.spinner("Applying all 6 scholarly sections..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    response = client.models.generate_content(
                        model="gemini-3.6-flash", 
                        contents=[image, "Please analyze this text according to your instructions."],
                        config=types.GenerateContentConfig(
                            system_instruction=AGENT_PROMPT,
                            temperature=0.2,
                        )
                    )
                    
                    parsed_data = parse_analysis(response.text)
                    
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
