import streamlit as st
import os
import json
from dotenv import load_dotenv
import plotly.graph_objects as go

# Import local utilities
from utils import extract_text_from_file, analyze_resume

# Page configurations
st.set_page_config(
    page_title="AI Resume Analyzer & Enhancer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv(override=True)

# Preload sample data for quick demonstration
SAMPLE_RESUME = """JOHN DOE
Software Engineer | john.doe@email.com | +1-555-0199 | San Francisco, CA

EXPERIENCE
Software Engineer, Tech Solutions Inc. (2023 - Present)
- Worked on developing the backend API.
- Wrote databases queries to retrieve data.
- Fixed bugs and helped deploy releases.
- Communicated with product managers.

Junior Developer, Web Creators Co (2021 - 2023)
- Created basic responsive websites.
- Used JavaScript, HTML, and CSS.
- Handled client requests and updated software features.

TECHNICAL SKILLS
Python, JavaScript, HTML, CSS, SQL, Git, AWS (Basic)

EDUCATION
B.S. in Computer Science, State University (2017 - 2021)
"""

SAMPLE_JD = """We are looking for a Senior/Mid-level Backend Engineer to build high-performance REST and GraphQL APIs.

Key Responsibilities:
- Design, build, and maintain scalable and robust API services using Python and FastAPI.
- Optimize database queries and schema designs in PostgreSQL to improve application performance.
- Work closely with cross-functional teams (Frontend, Product) to translate requirements into technical specs.
- Setup CI/CD pipelines and manage deployment configurations on AWS (EC2, RDS, Docker).

Required Qualifications:
- 3+ years of professional software engineering experience.
- Deep expertise in Python and SQL (PostgreSQL).
- Experience with containerization (Docker) and Git workflows.
- Excellent communication and collaboration skills.
- Familiarity with Redis or Kafka is a plus.
"""

# Custom CSS for glassmorphism / modern dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply global font styling */
    .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Modern header layout */
    .header-container {
        padding: 1.5rem 0rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .header-container h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        padding-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .header-container p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Custom cards and boxes */
    .premium-card {
        background-color: #11151c;
        border: 1px solid #222d3b;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    .strength-item {
        border-left: 4px solid #2ecc71;
        background-color: rgba(46, 204, 113, 0.08);
        padding: 12px 18px;
        border-radius: 4px;
        margin-bottom: 12px;
        color: #e0e0e0;
    }
    
    /* Keywords pills */
    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-match {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.4);
    }
    .pill-missing {
        background-color: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.4);
    }
    
    /* Bullet points re-writer styles */
    .bullet-box {
        background-color: #171d26;
        border: 1px solid #283547;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 18px;
    }
    .diff-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #8892b0;
        margin-bottom: 4px;
    }
    .diff-original {
        color: #ff6b6b;
        background-color: rgba(255, 107, 107, 0.08);
        padding: 8px 12px;
        border-radius: 6px;
        font-style: italic;
        margin-bottom: 10px;
        border-left: 3px solid #ff6b6b;
    }
    .diff-improved {
        color: #51cf66;
        background-color: rgba(81, 207, 102, 0.08);
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 500;
        margin-bottom: 10px;
        border-left: 3px solid #51cf66;
    }
    .diff-rationale {
        color: #a5b4fc;
        font-size: 0.9rem;
        padding-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown("""
<div class="header-container">
    <h1>🤖 AI Resume Analyzer & Enhancer</h1>
    <p>Upload your resume, paste the target job description, and leverage advanced AI to beat the ATS and get hired!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/resume.png", width=150)
    st.markdown("### ⚙️ Settings & Credentials")
    
    # AI Provider Selector
    provider = st.selectbox(
        "Select AI Provider:",
        options=["Google Gemini", "OpenAI"],
        index=0,
        help="Choose the LLM engine to perform the assessment. Google Gemini uses your AI Studio key."
    )
    
    # API Key initialization based on provider
    if provider == "Google Gemini":
        # Load gemini key if available, fallback to openai key location
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        key_label = "Enter Gemini API Key:"
        key_placeholder = "AIzaSy..."
        key_help = "Get one from Google AI Studio: https://aistudio.google.com/"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        key_label = "Enter OpenAI API Key:"
        key_placeholder = "sk-proj-..."
        key_help = "Get one from OpenAI platform: https://platform.openai.com/api-keys"
        
    # Allow overriding or inputting key
    input_key = st.text_input(
        key_label, 
        type="password", 
        value=api_key if api_key else "",
        placeholder=key_placeholder,
        help=key_help
    )
    
    if input_key:
        api_key = input_key
        
    st.markdown("---")
    st.markdown("### 🛠️ Simulation Settings")
    demo_mode = st.checkbox("Enable Demo / Simulation Mode", value=False,
                            help="Check this if your OpenAI API key doesn't have credits. It will bypass the OpenAI API call and display a fully-formed analysis using realistic mock data.")
    
    if demo_mode:
        api_key = "DEMO"
        st.info("🔄 Simulation Mode is Active! No OpenAI API quota will be used.")
        
    st.markdown("---")
    st.markdown("### 💡 Quick Actions")
    use_sample = st.button("📝 Load Sample Resume & JD", help="Loads a mock engineer resume and backend developer JD to try out the system instantly.")
    
    st.markdown("---")
    st.markdown("### 📚 Resources & Links")
    st.markdown("- [OpenAI Documentation](https://platform.openai.com/docs)")
    st.markdown("- [Streamlit Reference](https://docs.streamlit.io)")
    st.markdown("- [Resume Matcher Ideas](https://github.com/srbhr/Resume-Matcher)")
    
    st.info("💡 Note: We recommend using **GPT-4o** or **GPT-4o-mini** which provides incredibly precise structured assessments.")

# App Flow variables
resume_text = ""
job_description = ""

# Input Form
col_res, col_jd = st.columns(2)

with col_res:
    st.markdown("### 📄 Step 1: Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])
    
    # Pre-populate sample if clicked
    default_resume_val = SAMPLE_RESUME if use_sample else ""
    
    resume_input_text = st.text_area(
        "Or paste Resume plain text here:",
        height=280,
        value=default_resume_val,
        placeholder="Paste your professional experience, technical skills, and education details..."
    )
    
    if uploaded_file:
        try:
            with st.spinner("Extracting text from document..."):
                resume_text = extract_text_from_file(uploaded_file)
                st.success(f"Successfully extracted text from {uploaded_file.name}!")
        except Exception as e:
            st.error(str(e))
    elif resume_input_text:
        resume_text = resume_input_text

with col_jd:
    st.markdown("### 💼 Step 2: Paste Target Job Description")
    default_jd_val = SAMPLE_JD if use_sample else ""
    
    job_description = st.text_area(
        "Paste the Job Specification here:",
        height=370,
        value=default_jd_val,
        placeholder="Copy and paste the job description, required qualifications, and key responsibilities..."
    )

st.markdown("---")

# Trigger Analysis button
st.markdown("### 🎯 Step 3: Run AI Match Engine")
col_center, _ = st.columns([1, 4])
with col_center:
    submit_button = st.button("🚀 Analyze Fit & Suggest Improvements", use_container_width=True)

if submit_button:
    # Validation
    if not resume_text:
        st.error("⚠️ Please upload a resume file or paste the text details first.")
    elif not job_description:
        st.error("⚠️ Please provide the job description details to compare against.")
    elif not api_key:
        st.error(f"🔑 {provider} API Key not found. Please paste it in the sidebar to authenticate.")
    else:
        # Proceed with loading and calling LLM
        with st.spinner(f"🧠 {provider} is analyzing your details... mapping key skills, scoring alignment, and drafting enhancements..."):
            try:
                analysis_results = analyze_resume(resume_text, job_description, api_key, provider=provider)
                
                # Cache results in streamlit session state to prevent losing them on interactions
                st.session_state["analysis_results"] = analysis_results
                st.success("🎉 Analysis complete! View the insights below.")
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")

# Display results if cached in session state
if "analysis_results" in st.session_state:
    results = st.session_state["analysis_results"]
    
    # Create Layout for Tabs
    tab_dashboard, tab_gaps, tab_enhancer, tab_interview = st.tabs([
        "📊 Match Dashboard",
        "🔍 Keyword Gap Analysis",
        "💡 Resume Enhancer",
        "💬 Interview Prep Q&A"
    ])
    
    # TAB 1: DASHBOARD
    with tab_dashboard:
        col_score, col_summary = st.columns([2, 3])
        
        with col_score:
            score = results.get("match_score", 0)
            
            # Gauge chart design
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "ATS MATCH SCORE", 'font': {'size': 20, 'family': 'Outfit'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#2ecc71" if score >= 75 else ("#f1c40f" if score >= 50 else "#e74c3c")},
                    'bgcolor': "#1e293b",
                    'borderwidth': 2,
                    'bordercolor': "#475569",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(231, 76, 60, 0.1)'},
                        {'range': [50, 75], 'color': 'rgba(241, 196, 15, 0.1)'},
                        {'range': [75, 100], 'color': 'rgba(46, 204, 113, 0.1)'}
                    ]
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "white", 'family': "Outfit"},
                height=280,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Simple assessment card
            match_status = "Excellent Fit" if score >= 75 else ("Moderate Fit" if score >= 50 else "Weak Match")
            status_color = "#2ecc71" if score >= 75 else ("#f1c40f" if score >= 50 else "#e74c3c")
            
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 8px; background-color: #1e293b; border: 1px solid #334155;">
                <span style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Assessment Category</span>
                <h3 style="margin: 5px 0 0 0; color: {status_color}; font-weight: 700;">{match_status}</h3>
            </div>
            """, unsafe_allow_html=True)
            
        with col_summary:
            st.markdown("### 📝 Professional Match Summary")
            st.markdown(f"<div class='premium-card'>{results.get('summary', '')}</div>", unsafe_allow_html=True)
            
            st.markdown("### 🌟 Key Candidate Strengths")
            for strength in results.get("strengths", []):
                st.markdown(f"<div class='strength-item'>✅ {strength}</div>", unsafe_allow_html=True)
                
    # TAB 2: KEYWORD GAP ANALYSIS
    with tab_gaps:
        st.markdown("### 🔍 Skill and Keyword Optimization")
        st.markdown("Below is a breakdown of matching keywords detected in both texts, and critical keywords in the Job Description that are missing or require strengthening in your resume.")
        
        gap_data = results.get("keyword_gap_analysis", {})
        matching = gap_data.get("matching_keywords", [])
        missing = gap_data.get("missing_keywords", [])
        
        col_match, col_miss = st.columns(2)
        
        with col_match:
            st.markdown(f"#### 🟢 Matching Skills/Keywords ({len(matching)})")
            st.markdown("<div class='premium-card' style='min-height: 250px;'>", unsafe_allow_html=True)
            if matching:
                pills_html = "".join([f"<span class='pill pill-match'>{skill}</span>" for skill in matching])
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.info("No explicit skills detected in common yet. Improve your resume skills section!")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_miss:
            st.markdown(f"#### 🔴 Missing Critical Keywords ({len(missing)})")
            st.markdown("<div class='premium-card' style='min-height: 250px;'>", unsafe_allow_html=True)
            if missing:
                pills_html = "".join([f"<span class='pill pill-missing'>{skill}</span>" for skill in missing])
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.success("Amazing! No major keyword gaps detected. Your resume matches the job requirements perfectly!")
            st.markdown("</div>", unsafe_allow_html=True)
            
    # TAB 3: RESUME ENHANCER
    with tab_enhancer:
        st.markdown("### 💡 AI-Suggested Enhancements")
        st.markdown("Integrate the optimized bullet points below into your experience section, using metrics and active keywords to increase relevance.")
        
        improvements = results.get("bullet_point_improvements", [])
        
        if improvements:
            for idx, item in enumerate(improvements):
                st.markdown(f"""
                <div class="bullet-box">
                    <div class="diff-title">Point #{idx+1} Enhancement</div>
                    <div class="diff-title" style="font-size: 0.7rem; color: #ff6b6b; margin-top: 5px;">Original (From Resume)</div>
                    <div class="diff-original">"{item.get('original', '')}"</div>
                    <div class="diff-title" style="font-size: 0.7rem; color: #51cf66;">AI Suggested (Tailored to Job)</div>
                    <div class="diff-improved">"{item.get('improved', '')}"</div>
                    <div class="diff-title" style="font-size: 0.7rem; color: #a5b4fc;">Strategic Rationale</div>
                    <div class="diff-rationale">💡 {item.get('rationale', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No individual bullet points suggested for change. Read the tailored sections below.")
            
        tailored = results.get("tailored_sections", [])
        if tailored:
            st.markdown("### 📂 Tailored Sections")
            st.markdown("Copy and paste these pre-optimized sections directly into your resume build.")
            
            for section in tailored:
                with st.expander(f"📝 Optimized Section: {section.get('section_name', 'Tailored Section')}"):
                    st.code(section.get("content", ""), language="markdown")
                    
    # TAB 4: INTERVIEW PREP
    with tab_interview:
        st.markdown("### 💬 Customized Interview Preparation")
        st.markdown("Prepare responses to potential questions based on the requirements of this role and the specific details on your resume.")
        
        questions = results.get("interview_questions", [])
        
        if questions:
            for idx, q_item in enumerate(questions):
                with st.expander(f"❓ Question #{idx+1}: {q_item.get('question', '')}"):
                    st.markdown("**💡 Response Strategy:**")
                    st.write(q_item.get("answer_strategy", ""))
                    
                    st.markdown("---")
                    st.markdown("**🗣️ Sample High-Quality Answer:**")
                    st.markdown(f"*{q_item.get('sample_answer', '')}*")
        else:
            st.info("No sample prep questions generated. Practice behavior questions based on standard engineering goals!")
            
    # Add a PDF download or copy-paste container
    st.markdown("---")
    st.markdown("### 📤 Export Tailored Content")
    st.write("You can copy the tailored bullet points and sections directly from the tabs above to update your word document or LaTex file.")
