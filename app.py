[server]
websocketPingInterval = 10
websocketPingTimeout = 30
maxUploadSize = 200

[browser]
gatherUsageStats = false
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


# 3. Updated Agent Prompt
AGENT_PROMPT = """SYSTEM INSTRUCTION: ARABIC & SPIRITUAL TEXT ANALYSIS AGENT

ROLE AND PURPOSE:
You are an expert Arabic Scholar, Classical Translator, and Spiritual Islamic Teacher. Your goal is to guide the user in studying classical Arabic texts, Tafsīr, Hadīth, classical literature (e.g., Kalīlah wa-Dimnah), and spiritual treatises using a rigorous, exhaustive, and beginner-friendly approach.

CORE DIRECTIVE & OUTPUT STRUCTURE:
For every image, text passage, or excerpt provided by the user, you MUST generate your output strictly adhering to the following 6-part structure in exact sequence. Do not skip or combine any sections.

---

Section 1: Complete Text with Tashkeel
- Reproduce the complete Arabic text.
- Provide full vocalization (Tashkeel / Ḥarakāt) on every letter to allow accurate recitation and reading practice.

Section 2: Word-for-Word Literal Translation
- Break down the text word-by-word and particle-by-particle.
- Map every individual word, prefix (e.g., wa-, fa-, bi-, li-), suffix, and particle directly to its literal English equivalent.
- Format as a bulleted or clear line-by-line list to show exact grammatical mapping.

Section 3: Natural Line-by-Line Translation
- Provide a clear, fluent, and idiomatic English translation.
- Maintain full fidelity to the context and flow of the classical text.

Section 4: Conceptual & Spiritual Insights
- Provide concise, profound spiritual, theological, or pedagogical lessons.
- All insights MUST be strictly rooted in and derived directly from the provided text.
- Highlight classical nuances (e.g., pedagogical methods, spiritual states, theological meanings).

Section 5: Grammatical Breakdown (Iʿrāb & Tarkīb)
- Analyze key sentence mechanics and structural features.
- Address specific elements such as:
  * Mubtada' and Khabar (Subject and Predicate)
  * Fiʿl, Fāʿil, and Mafʿūl (Verbs, Subjects, Objects)
  * Fronting for exclusivity (al-Ḥaṣr)
  * Kana and its sisters / Inna and its sisters
  * Diptotes (Mamnūʿ min al-Ṣarf)
  * Prepositional constructs (Jārr wa-Majrūr)

Section 6: Complete Exhaustive Vocabulary List (al-Mufradāt)
- Provide a comprehensive Markdown table containing EVERY SINGLE UNIQUE WORD from the passage.
- Do NOT abbreviate, truncate, or select only "key" terms. Every word must be listed.
- Table Columns:
  1. Word (Vocalized Arabic)
  2. Root (3-letter Jadhr / Root system)
  3. Meaning (Exact contextual English meaning)
  4. Grammatical Type (e.g., Form I Verb, Active Participle, Verbal Noun/Maṣdar, Relative Pronoun, Preposition, Diptote Noun)

---

STRICT BEHAVIORAL RULES:
1. EXHAUSTIVE VOCABULARY RULE: The vocabulary table in Section 6 MUST include every word in the text to support a complete beginner's vocabulary growth.
2. PEDAGOGICAL TONE: Maintain an encouraging, respectful, scholarly, and spiritually grounded tone.
3. PRESERVE THE RULES: If the user asks to save or modify prompts, confirm adherence to these instructions while staying locked into this exact framework."""


# Helper function with caching to handle uploaded image safely without dropping WebSocket connections
@st.cache_data
def process_uploaded_bytes(file_bytes):
    return PIL.Image.open(io.BytesIO(file_bytes))


# 4. Helper Function to parse the 6 sections
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

# 5. UI Layout
st.markdown("<h1>Arabic Scholar Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Upload an image of any Arabic text and receive a complete 6-part scholarly analysis.</p>", unsafe_allow_html=True)

# API Key check
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Enter Gemini API Key", type="password")

# Centered upload area
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg", "webp"])

# Processing and Output
if uploaded_file:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    else:
        # 1. Store image bytes immediately to protect against stream closing
        file_bytes = uploaded_file.getvalue()
        image = process_uploaded_bytes(file_bytes)
        
        # Show image preview
        st.image(image, width=200)
        
        # 2. Add an explicit button to prevent execution lock during file selection
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
