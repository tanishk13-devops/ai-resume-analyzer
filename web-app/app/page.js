'use client';

import { useState } from 'react';

// Preloaded mock data templates
const SAMPLE_RESUME = `JOHN DOE
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
`;

const SAMPLE_JD = `We are looking for a Senior/Mid-level Backend Engineer to build high-performance REST and GraphQL APIs.

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
`;

export default function Home() {
  // App States
  const [provider, setProvider] = useState('Google Gemini');
  const [apiKey, setApiKey] = useState('');
  const [demoMode, setDemoMode] = useState(false);
  
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  // UI Tabs & Accordions States
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeFaq, setActiveFaq] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  // Dynamic Key Configs
  const isGemini = provider === 'Google Gemini';
  const finalApiKey = demoMode ? 'DEMO' : apiKey;

  // Pre-fill sample data handler
  const loadSampleData = () => {
    setResumeText(SAMPLE_RESUME);
    setJobDescription(SAMPLE_JD);
    setFile(null);
  };

  // Drag and drop / file input handlers
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setResumeText(''); // clear text if file is uploaded
    }
  };

  // Copy to clipboard utility
  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Form Submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResults(null);

    // Validation
    if (!resumeText.trim() && !file) {
      setError('Please upload a resume file or paste your resume text details.');
      return;
    }
    if (!jobDescription.trim()) {
      setError('Please paste the target job description to compare against.');
      return;
    }
    if (!demoMode && !apiKey.trim()) {
      setError(`Please configure your ${provider} API Key in the sidebar settings.`);
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else {
        formData.append('resumeText', resumeText);
      }
      formData.append('jobDescription', jobDescription);
      formData.append('provider', demoMode ? 'Demo Mode' : provider);
      formData.append('apiKey', finalApiKey);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Server error occurred during analysis.');
      }

      setResults(data);
      setActiveTab('dashboard'); // Default to dashboard on success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // SVG Gauge calculations
  const matchScore = results?.match_score || 0;
  const radius = 80;
  const strokeWidth = 10;
  const normalizedRadius = radius - strokeWidth * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (matchScore / 100) * circumference;

  let scoreColor = '#ef4444'; // Red
  let assessmentText = 'Weak Match';
  if (matchScore >= 75) {
    scoreColor = '#10b981'; // Green
    assessmentText = 'Excellent Fit';
  } else if (matchScore >= 50) {
    scoreColor = '#f59e0b'; // Yellow/Orange
    assessmentText = 'Moderate Fit';
  }

  return (
    <main style={{ padding: '24px 0' }}>
      {/* Header Panel */}
      <div style={{ maxWidth: '1400px', margin: '0 auto 30px auto', padding: '0 20px' }}>
        <div className="page-header">
          <h1 className="page-title">🤖 AI Resume Analyzer & Enhancer</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Upload your resume, paste the target job description, and leverage advanced AI to beat the ATS and get hired!
          </p>
        </div>
      </div>

      <div className="layout-container">
        {/* Left Side: Sidebar Settings */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: '700', borderBottom: '1px solid var(--panel-border)', paddingBottom: '8px' }}>
              ⚙️ Settings & Credentials
            </h2>

            {/* Provider Select */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)' }}>
                Select AI Provider:
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                style={{
                  padding: '10px',
                  borderRadius: '8px',
                  background: '#182235',
                  border: '1px solid var(--panel-border)',
                  color: 'white',
                  outline: 'none',
                }}
              >
                <option value="Google Gemini">Google Gemini</option>
                <option value="OpenAI">OpenAI</option>
              </select>
            </div>

            {/* API Key Input */}
            {!demoMode && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)' }}>
                  {isGemini ? 'Enter Gemini API Key:' : 'Enter OpenAI API Key:'}
                </label>
                <input
                  type="password"
                  placeholder={isGemini ? 'AIzaSy...' : 'sk-proj-...'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  style={{
                    padding: '10px',
                    borderRadius: '8px',
                    background: '#182235',
                    border: '1px solid var(--panel-border)',
                    color: 'white',
                    outline: 'none',
                  }}
                />
                <a
                  href={isGemini ? 'https://aistudio.google.com/' : 'https://platform.openai.com/api-keys'}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', textDecoration: 'none' }}
                >
                  Get key from {isGemini ? 'Google AI Studio' : 'OpenAI Platform'}
                </a>
              </div>
            )}

            {/* Simulation Settings */}
            <div style={{ borderTop: '1px solid var(--panel-border)', paddingTop: '16px' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '8px', color: '#c7d2fe' }}>
                🛠️ Simulation Settings
              </h3>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={demoMode}
                  onChange={(e) => setDemoMode(e.target.checked)}
                  style={{ width: '16px', height: '16px' }}
                />
                Enable Demo / Simulation Mode
              </label>
              {demoMode && (
                <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '8px 12px', borderRadius: '6px', fontSize: '0.78rem', color: '#a5b4fc', marginTop: '10px' }}>
                  🔄 Simulation Mode Active! App will bypass API calls and use local backend mock data.
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div style={{ borderTop: '1px solid var(--panel-border)', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#c7d2fe' }}>
                💡 Quick Actions
              </h3>
              <button
                type="button"
                onClick={loadSampleData}
                style={{
                  padding: '10px',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid var(--panel-border)',
                  color: 'white',
                  cursor: 'pointer',
                  fontWeight: '600',
                  textAlign: 'left',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                📝 Load Sample Resume & JD
              </button>
            </div>
          </div>
        </aside>

        {/* Right Side: Form & Results */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          {/* Inputs Section */}
          <form onSubmit={handleSubmit} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {/* Step 1: Upload Resume */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>📄 Step 1: Upload Resume</h3>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: '#182235',
                    border: '1px dashed rgba(255,255,255,0.2)',
                    color: '#9ca3af',
                    cursor: 'pointer',
                  }}
                />
                {file && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--color-green)' }}>
                    Selected file: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                  </p>
                )}
                <textarea
                  placeholder="Or paste Resume plain text here..."
                  value={resumeText}
                  onChange={(e) => {
                    setResumeText(e.target.value);
                    if (file) setFile(null); // clear file if text is typed
                  }}
                  disabled={!!file}
                  style={{
                    height: '220px',
                    padding: '12px',
                    borderRadius: '8px',
                    background: '#0d131f',
                    border: '1px solid var(--panel-border)',
                    color: 'white',
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    resize: 'none',
                    opacity: file ? 0.5 : 1,
                  }}
                />
              </div>

              {/* Step 2: Job Description */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>💼 Step 2: Paste Target Job Description</h3>
                <textarea
                  placeholder="Paste the Job Specification here (required qualifications, key responsibilities, tools needed)..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  style={{
                    height: '280px',
                    padding: '12px',
                    borderRadius: '8px',
                    background: '#0d131f',
                    border: '1px solid var(--panel-border)',
                    color: 'white',
                    resize: 'none',
                  }}
                />
              </div>
            </div>

            {/* Error Banner */}
            {error && (
              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#fca5a5', fontSize: '0.9rem' }}>
                ⚠️ {error}
              </div>
            )}

            {/* Submit Action */}
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '12px 28px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%)',
                  color: 'white',
                  cursor: 'pointer',
                  fontWeight: '700',
                  border: 'none',
                  boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)',
                  transition: 'all 0.2s',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? '🧠 Running AI Engine...' : '🚀 Analyze Fit & Suggest Improvements'}
              </button>
            </div>
          </form>

          {/* Results Visuals Section */}
          {results && (
            <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Tab Selector Buttons */}
              <div className="tab-container">
                <button
                  type="button"
                  onClick={() => setActiveTab('dashboard')}
                  className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                >
                  📊 Match Dashboard
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('gaps')}
                  className={`tab-btn ${activeTab === 'gaps' ? 'active' : ''}`}
                >
                  🔍 Keyword Gap Analysis
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('enhancer')}
                  className={`tab-btn ${activeTab === 'enhancer' ? 'active' : ''}`}
                >
                  💡 Resume Enhancer
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('interview')}
                  className={`tab-btn ${activeTab === 'interview' ? 'active' : ''}`}
                >
                  💬 Interview Prep Q&A
                </button>
              </div>

              {/* Tab 1: Dashboard */}
              {activeTab === 'dashboard' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '30px' }}>
                  {/* Gauge score display */}
                  <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '20px', justifyContent: 'center' }}>
                    <div className="score-circle-container">
                      <svg className="score-svg" viewBox="0 0 160 160">
                        <circle className="score-bg-circle" cx="80" cy="80" r={normalizedRadius} />
                        <circle
                          className="score-progress-circle"
                          stroke={scoreColor}
                          strokeDasharray={circumference + ' ' + circumference}
                          strokeDashoffset={strokeDashoffset}
                          cx="80"
                          cy="80"
                          r={normalizedRadius}
                        />
                      </svg>
                      <div className="score-text">
                        <div className="score-val">{matchScore}</div>
                        <div className="score-label">Match %</div>
                      </div>
                    </div>
                    <div style={{ background: '#182235', border: '1px solid var(--panel-border)', borderRadius: '8px', padding: '8px 16px', display: 'inline-block', margin: '0 auto' }}>
                      <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Assessment Category</span>
                      <h4 style={{ color: scoreColor, fontWeight: '700', fontSize: '1.2rem', marginTop: '2px' }}>{assessmentText}</h4>
                    </div>
                  </div>

                  {/* Summary & Strengths */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>📝 Professional Match Summary</h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.98rem', background: '#0d131f', border: '1px solid var(--panel-border)', padding: '16px', borderRadius: '10px' }}>
                        {results.summary}
                      </p>
                    </div>

                    <div>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>🌟 Key Candidate Strengths</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {results.strengths?.map((strength, idx) => (
                          <div key={idx} style={{ background: 'rgba(16, 185, 129, 0.06)', borderLeft: '4px solid var(--color-green)', borderRadius: '0 8px 8px 0', padding: '10px 14px', fontSize: '0.92rem' }}>
                            ✅ {strength}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Keyword Gaps */}
              {activeTab === 'gaps' && (
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>🔍 Skill and Keyword Optimization</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '20px' }}>
                    Below is a breakdown of matching keywords detected in both texts, and critical keywords in the Job Description that are missing or require strengthening in your resume.
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    {/* Matching */}
                    <div className="glass-panel" style={{ background: 'rgba(255,255,255,0.01)', minHeight: '200px' }}>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--color-green)', marginBottom: '14px' }}>
                        🟢 Matching Skills/Keywords ({results.keyword_gap_analysis?.matching_keywords?.length || 0})
                      </h4>
                      <div>
                        {results.keyword_gap_analysis?.matching_keywords?.map((skill, idx) => (
                          <span key={idx} className="pill pill-match">{skill}</span>
                        ))}
                        {(!results.keyword_gap_analysis?.matching_keywords || results.keyword_gap_analysis.matching_keywords.length === 0) && (
                          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No matching keywords detected.</p>
                        )}
                      </div>
                    </div>

                    {/* Missing */}
                    <div className="glass-panel" style={{ background: 'rgba(255,255,255,0.01)', minHeight: '200px' }}>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--color-red)', marginBottom: '14px' }}>
                        🔴 Missing Critical Keywords ({results.keyword_gap_analysis?.missing_keywords?.length || 0})
                      </h4>
                      <div>
                        {results.keyword_gap_analysis?.missing_keywords?.map((skill, idx) => (
                          <span key={idx} className="pill pill-missing">{skill}</span>
                        ))}
                        {(!results.keyword_gap_analysis?.missing_keywords || results.keyword_gap_analysis.missing_keywords.length === 0) && (
                          <p style={{ color: 'var(--color-green)', fontSize: '0.9rem', fontWeight: '600' }}>Amazing! No major keyword gaps detected.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: Resume Enhancer */}
              {activeTab === 'enhancer' && (
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>💡 AI-Suggested Enhancements</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '20px' }}>
                    Integrate the optimized bullet points below into your experience section, using metrics and active keywords to increase relevance.
                  </p>

                  {results.bullet_point_improvements?.map((item, idx) => (
                    <div key={idx} className="bullet-box">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div className="diff-tag diff-rationale-tag" style={{ fontSize: '0.85rem' }}>Enhancement #{idx + 1}</div>
                        <button
                          type="button"
                          className={`copy-btn ${copiedIndex === `bullet-${idx}` ? 'copied' : ''}`}
                          onClick={() => copyToClipboard(item.improved, `bullet-${idx}`)}
                        >
                          {copiedIndex === `bullet-${idx}` ? '✓ Copied' : '📋 Copy Suggestion'}
                        </button>
                      </div>
                      
                      <div className="diff-tag diff-original-tag">Original (From Resume)</div>
                      <div className="diff-original-val">"{item.original}"</div>
                      
                      <div className="diff-tag diff-improved-tag">AI Suggested (Tailored to Job)</div>
                      <div className="diff-improved-val">"{item.improved}"</div>
                      
                      <div className="diff-tag diff-rationale-tag">Strategic Rationale</div>
                      <div className="diff-rationale-val">💡 {item.rationale}</div>
                    </div>
                  ))}

                  {/* Tailored Sections */}
                  {results.tailored_sections && results.tailored_sections.length > 0 && (
                    <div style={{ marginTop: '30px' }}>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '14px' }}>📂 Pre-Tailored Resume Sections</h3>
                      {results.tailored_sections.map((section, idx) => (
                        <div key={idx} style={{ background: '#0d131f', border: '1px solid var(--panel-border)', borderRadius: '10px', padding: '16px', marginBottom: '16px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                            <h4 style={{ fontWeight: '600', color: 'var(--accent-blue)' }}>📝 {section.section_name}</h4>
                            <button
                              type="button"
                              className={`copy-btn ${copiedIndex === `section-${idx}` ? 'copied' : ''}`}
                              onClick={() => copyToClipboard(section.content, `section-${idx}`)}
                            >
                              {copiedIndex === `section-${idx}` ? '✓ Copied' : '📋 Copy Section'}
                            </button>
                          </div>
                          <pre style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap', background: '#060a12', padding: '12px', borderRadius: '6px' }}>
                            {section.content}
                          </pre>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: Interview Prep */}
              {activeTab === 'interview' && (
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>💬 Customized Interview Preparation</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '20px' }}>
                    Prepare responses to potential questions based on the requirements of this role and the specific details on your resume.
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {results.interview_questions?.map((item, idx) => (
                      <div
                        key={idx}
                        className={`faq-item ${activeFaq === idx ? 'active' : ''}`}
                        style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--panel-border)', borderRadius: '8px', padding: '4px 16px 12px 16px' }}
                      >
                        <button
                          type="button"
                          className="faq-question"
                          onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                        >
                          <span>❓ Q#{idx + 1}: {item.question}</span>
                          <span className="faq-arrow">▼</span>
                        </button>
                        <div className="faq-answer">
                          <div className="faq-answer-inner">
                            <p style={{ marginBottom: '12px' }}>
                              <strong style={{ color: '#c7d2fe' }}>💡 Response Strategy:</strong><br />
                              <span style={{ display: 'block', marginTop: '4px' }}>{item.answer_strategy}</span>
                            </p>
                            <p>
                              <strong style={{ color: '#a7f3d0' }}>🗣️ Sample High-Quality Answer:</strong><br />
                              <span style={{ display: 'block', marginTop: '4px', fontStyle: 'italic' }}>"{item.sample_answer}"</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      {/* Footer Section */}
      <hr style={{ border: 0, height: '1px', background: 'linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0))', marginTop: '4rem', marginBottom: '1.5rem' }} />
      <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem', paddingBottom: '2rem' }}>
        <p>Created with ❤️ by <span style={{ color: 'var(--color-green)', fontWeight: '600' }}>Tanishk Jaiswal</span></p>
        <div style={{ marginTop: '10px' }}>
          <a href="https://github.com/tanishk13-devops" target="_blank" rel="noreferrer" style={{ color: '#a5b4fc', textDecoration: 'none', margin: '0 10px', fontWeight: '500' }}>🐱 GitHub</a> | 
          <a href="https://www.linkedin.com/in/tanishk-jaiswal-05a24724a/" target="_blank" rel="noreferrer" style={{ color: '#a5b4fc', textDecoration: 'none', margin: '0 10px', fontWeight: '500' }}>💼 LinkedIn</a> | 
          <a href="mailto:nickyjaiswal85@gmail.com" style={{ color: '#a5b4fc', textDecoration: 'none', margin: '0 10px', fontWeight: '500' }}>📧 Email</a>
        </div>
      </div>
    </main>
  );
}
