# AI Resume Analyzer

Your AI-powered resume analyzer using OpenAI GPT and Streamlit.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- OpenAI API key

### 2. Installation

```bash
# Clone or navigate to project
cd ai-resume-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Run Application

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

## 📁 Project Structure

```
ai-resume-analyzer/
├── main.py                 # Streamlit app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── utils/
│   ├── file_handler.py    # PDF/DOCX text extraction
│   ├── text_processor.py  # Text processing & skill extraction
│   └── llm_handler.py     # OpenAI API integration
├── modules/
│   └── resume_analyzer.py # Main analysis orchestrator
└── data/
    └── (for storing analyses)
```

## ✨ Features

- **Resume Upload**: Support for PDF and DOCX formats
- **Job Description Input**: Text paste or file upload
- **AI Analysis**: Match score, skill analysis, suggestions
- **Improved Resume**: AI-generated optimized resume
- **Export Results**: Download analysis and improved resume

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-3.5-turbo
- **Document Processing**: PyPDF2, python-docx
- **Data Processing**: Pandas
- **Database**: SQLAlchemy (optional)

## 📊 How It Works

1. Upload resume and job description
2. Extract text from files
3. Analyze using OpenAI GPT
4. Generate match scores and suggestions
5. Create AI-optimized resume
6. Display and download results

## 🎯 Analysis Results

- **Match Score**: Overall resume-to-job alignment (0-100%)
- **Matching Skills**: Skills present in both resume and job
- **Missing Skills**: Required skills not in resume
- **Suggestions**: Specific improvements for resume
- **Improved Resume**: AI-rewritten resume optimized for job

## 🔐 Security

- API keys stored in `.env` (never commit to git)
- File uploads processed locally
- No data stored without user consent

## 📝 Requirements

- OpenAI API key with credits
- Minimum 10 MB file upload support
- Modern web browser
- Python 3.8+

## 🐛 Troubleshooting

**Issue**: "Invalid API key"
- Check `.env` file has correct OPENAI_API_KEY
- Verify API key has available credits

**Issue**: "File upload failed"
- Check file size is less than 10 MB
- Verify file is PDF or DOCX format

**Issue**: Module import errors
- Run `pip install -r requirements.txt`
- Verify virtual environment is activated

## 📚 Development

### Phase 1: Foundation ✅
- Project structure created
- All base files set up
- Dependencies configured

### Phase 2-10: Coming Next
- Document processing enhancement
- Database integration
- Advanced features
- Deployment

## 📄 License

MIT

## 👨‍💻 Author

Created as part of AI Resume Analyzer project

---

**Next Steps**: 
1. Install dependencies: `pip install -r requirements.txt`
2. Add OpenAI API key to `.env`
3. Run: `streamlit run main.py`
