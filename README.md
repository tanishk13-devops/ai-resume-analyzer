# 🤖 AI Resume Analyzer & Enhancer

An AI-powered Resume Analyzer and Enhancer built using Streamlit, Python, and the Google Gemini API (with support for OpenAI). This tool extracts text from resumes (PDF, DOCX, TXT), maps it against job descriptions, and provides structured feedback to improve formatting, keyword density, and overall ATS matching scores.

🚀 **Live App URL:** [https://ai-resume-analyzer-xi-jet.vercel.app](https://ai-resume-analyzer-xi-jet.vercel.app)

---

## 🌟 Key Features

- **📊 Match Dashboard**: Displays an interactive Plotly-based ATS match score gauge, candidate strengths, and a professional fit summary.
- **🔍 Keyword Gap Analysis**: Visualizes matching and missing skills or keywords using clean, side-by-side color-coded pill chips.
- **💡 Resume Enhancer**: Generates action-oriented, metrics-driven bullet point recommendations using the CAR/STAR method, with strategic rationale.
- **💬 Interview Prep Q&A**: Dynamically creates custom interview questions, answer strategies, and sample answers based on the resume gaps.
- **🛠️ Multi-Provider Support**: Supports both **Google Gemini** (pre-configured for `gemini-2.5-flash`) and **OpenAI** models. Includes a offline **Demo Mode** for local testing without API credits.

---

## 🛠️ Local Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tanishk13-devops/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   # Google Gemini API Key
   GEMINI_API_KEY=your_gemini_api_key_here

   # OpenAI API Key (Optional)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Install Dependencies and Run**:
   It is recommended to run the app using `uv` or a virtual environment (Python 3.12 is recommended):
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## 🐋 Docker Support

You can also run this application containerized using Docker:

1. **Build the image**:
   ```bash
   docker build -t ai-resume-analyzer .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 ai-resume-analyzer
   ```
   Open `http://localhost:8501` to access the application.

---

## 🤝 Contributing
Feel free to open issues or pull requests to suggest new features or improvements.

---

### Created with ❤️ by [Tanishk Jaiswal](https://www.linkedin.com/in/tanishk-jaiswal-05a24724a/)
🐱 [GitHub](https://github.com/tanishk13-devops) | 💼 [LinkedIn](https://www.linkedin.com/in/tanishk-jaiswal-05a24724a/) | 📧 [Email](mailto:nickyjaiswal85@gmail.com)
