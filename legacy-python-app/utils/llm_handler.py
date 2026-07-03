import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMHandler:
    """Handle OpenAI LLM interactions with Gemini fallback"""
    
    def __init__(self):
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Check if OpenAI key is set and valid, otherwise fallback to Gemini
        if gemini_key and (not openai_key or openai_key == "your_openai_key_here"):
            self.client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self.model = "gemini-2.0-flash-lite"

        else:
            self.client = OpenAI(api_key=openai_key)
            self.model = "gpt-3.5-turbo"
            
        self.temperature = 0.7

    def _clean_json_content(self, content):
        """Clean markdown code block wrappers from JSON string"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    
    def analyze_resume(self, resume_text, job_description):
        """Analyze resume against job description"""
        prompt = f"""Analyze the following resume against the job description and provide a detailed analysis in JSON format.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a JSON response with the following structure:
{{
    "match_score": <0-100>,
    "matching_skills": [list of skills that match],
    "missing_skills": [list of skills required but missing],
    "experience_match": <0-100>,
    "education_assessment": <brief assessment>,
    "strengths": [list of resume strengths],
    "concerns": [list of potential concerns]
}}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert recruiter analyzing resumes. You must output ONLY valid JSON, no conversational text or prefix."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        
        # Parse JSON response
        try:
            cleaned_content = self._clean_json_content(response.choices[0].message.content)
            result = json.loads(cleaned_content)
            return result
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            return {"error": f"Failed to parse LLM response: {str(e)}"}
    
    def get_suggestions(self, resume_text, job_description, analysis_result):
        """Get structured suggestions to improve resume"""
        prompt = f"""Based on the following analysis, provide 4-6 specific, actionable suggestions to improve the resume.
Your suggestions must be detailed enough to be applied to the resume text.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

ANALYSIS:
{json.dumps(analysis_result, indent=2)}

Provide suggestions as a JSON array of objects. Each suggestion object MUST have the following fields:
- "id": A unique integer (1, 2, 3...)
- "type": One of:
    * "add_skill" (to add a missing skill or keyword)
    * "rewrite_bullet" (to improve a work experience description or bullet point)
    * "add_section" (to add a missing section)
- "section": Name of the section (e.g. "skills", "experience", "summary", "education")
- "suggestion": A short human-readable description of what this change accomplishes.
- "target_text": For "rewrite_bullet", this must be the EXACT substring in the original resume text that we will replace. For "add_skill", this should be the section title or context word near where the skill should be appended, or null if it's a general skill to append to the end of the skills list.
- "replacement_text": The exact text to put in place of target_text, or to append to the section. For "rewrite_bullet", this must be the fully rewritten sentence. For "add_skill", it should be the new skill name.
- "impact_points": Estimated ATS score improvement (integer, e.g. 5, 8, 10).

Format example:
[
  {{
    "id": 1,
    "type": "add_skill",
    "section": "skills",
    "suggestion": "Add Docker to the skills list",
    "target_text": null,
    "replacement_text": "Docker",
    "impact_points": 5
  }},
  {{
    "id": 2,
    "type": "rewrite_bullet",
    "section": "experience",
    "suggestion": "Rewrite experience bullet to highlight impact with metrics",
    "target_text": "Responsible for backend development using Python.",
    "replacement_text": "Designed and scaled backend REST APIs using Python and Django, improving throughput by 40% and reducing database query latencies by 25%.",
    "impact_points": 8
  }}
]

Return ONLY valid JSON. Make sure target_text matches the original resume EXACTLY including spaces and punctuation.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert resume writer and career coach. You must output ONLY a valid JSON array of objects, with no explanation or conversational text."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        
        try:
            cleaned_content = self._clean_json_content(response.choices[0].message.content)
            suggestions = json.loads(cleaned_content)
            return suggestions if isinstance(suggestions, list) else []
        except (json.JSONDecodeError, AttributeError, IndexError):
            return []
    
    def generate_improved_resume(self, resume_text, job_description, suggestions):
        """Generate improved version of resume"""
        prompt = f"""Rewrite the following resume to better match the job description and incorporate these suggestions.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

SUGGESTIONS TO INCORPORATE:
{json.dumps(suggestions, indent=2)}

Provide the improved resume text. Make it professional, concise, and tailored to the job description.
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Improve resumes to match job descriptions while keeping them truthful and professional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5  # Lower temperature for more consistent output
        )
        
        return response.choices[0].message.content

    def parse_resume_to_json(self, resume_text):
        """Parse raw resume text into structured JSON schema"""
        prompt = f"""You are an expert resume parser. Parse the following resume text into a structured JSON object.

RESUME TEXT:
{resume_text}

Output ONLY valid JSON with this exact structure:
{{
  "name": "Full Name",
  "contact": {{
    "email": "email address or empty string",
    "phone": "phone number or empty string",
    "linkedin": "linkedin profile url or empty string",
    "location": "location or empty string"
  }},
  "summary": "professional summary or empty string",
  "experience": [
    {{
      "job_title": "title",
      "company": "company name",
      "dates": "date range (e.g. 2021 - Present)",
      "description": [
        "bullet point 1",
        "bullet point 2"
      ]
    }}
  ],
  "skills": ["skill1", "skill2"],
  "education": [
    {{
      "degree": "degree / major",
      "school": "school name",
      "dates": "date range"
    }}
  ]
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume parsing tool. Output ONLY valid JSON, no description."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            cleaned = self._clean_json_content(response.choices[0].message.content)
            return json.loads(cleaned)
        except Exception as e:
            # Robust heuristic fallback parsing when LLM fails
            fallback = {
                "name": "Resume Owner",
                "contact": {"email": "", "phone": "", "linkedin": "", "location": ""},
                "summary": "",
                "experience": [],
                "skills": [],
                "education": []
            }
            try:
                lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
                if lines:
                    # Name is usually the first non-empty line
                    fallback["name"] = lines[0]
                    
                # Find Email
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
                if email_match:
                    fallback["contact"]["email"] = email_match.group(0)
                    
                # Find Phone
                phone_match = re.search(r'\(?\+?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{3,9}[-.\s]?[0-9]{3,9}', resume_text)
                if phone_match:
                    fallback["contact"]["phone"] = phone_match.group(0)
                    
                # Find LinkedIn
                li_match = re.search(r'linkedin\.com/in/[\w\-]+', resume_text, re.IGNORECASE)
                if li_match:
                    fallback["contact"]["linkedin"] = li_match.group(0)
                
                # Very basic section parsing
                current_section = None
                skills_list = []
                summary_lines = []
                
                for line in lines:
                    ll = line.lower()
                    if "skills" in ll or "technologies" in ll or "key competencies" in ll:
                        current_section = "skills"
                        continue
                    elif "summary" in ll or "profile" in ll or "about me" in ll:
                        current_section = "summary"
                        continue
                    elif "experience" in ll or "employment" in ll or "work history" in ll:
                        current_section = "experience"
                        continue
                    elif "education" in ll or "academic" in ll:
                        current_section = "education"
                        continue
                        
                    if current_section == "skills":
                        # Split by comma or list item indicators
                        parts = re.split(r'[,|•·\-\*]', line)
                        for part in parts:
                            if part.strip() and len(part.strip()) < 30:
                                skills_list.append(part.strip())
                    elif current_section == "summary":
                        summary_lines.append(line)
                
                if skills_list:
                    fallback["skills"] = list(set(skills_list))
                if summary_lines:
                    fallback["summary"] = " ".join(summary_lines)
                    
                # If experience is empty, let's at least populate one block with raw text to avoid losing details
                if not fallback["experience"]:
                    fallback["experience"] = [{
                        "job_title": "Details",
                        "company": "Uploaded Resume Content",
                        "dates": "",
                        "description": lines[1:15] if len(lines) > 15 else lines[1:]
                    }]
            except Exception:
                pass
            return fallback

    def generate_cover_letter(self, resume_text, job_description, notes=None):
        """Generate a tailored cover letter based on resume and job description."""
        prompt = f"""Draft a professional, compelling cover letter matching the candidate's resume to the job description.
        
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""
        if notes:
            prompt += f"\nADDITIONAL USER NOTES/INSTRUCTIONS:\n{notes}\n"
            
        prompt += """
Keep the letter to 3-4 structured paragraphs:
1. Introduction: Express enthusiasm for the role and name the target company.
2. Value Proposition (Paragraph 2-3): Connect specific, matching experience/skills from the resume directly to key requirements of the job description.
3. Call to Action / Closing: State desire for an interview and close professionally.

Use standard business placeholders for contact information if not fully clear, or construct a clean header structure. Do not output markdown code formatting wrapper or explanation, just the raw text of the cover letter.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional resume writer and career coach. Draft a compelling cover letter."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

    def refine_cover_letter(self, letter_text, feedback, history=None):
        """Iteratively refine a cover letter based on user feedback and chat history."""
        messages = [
            {"role": "system", "content": "You are a helpful career assistant. Edit the user's cover letter as requested, maintaining professional tone and matching requirements."}
        ]
        
        if history:
            for item in history:
                messages.append({"role": item["role"], "content": item["content"]})
                
        prompt = f"""Here is the current cover letter:
---
{letter_text}
---

USER FEEDBACK / REWRITE REQUEST:
{feedback}

Please provide the fully rewritten cover letter. Return ONLY the new cover letter text, with no other conversational introduction or explanation.
"""
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

    def generate_interview_prep(self, resume_text, job_description):
        """Generate interview preparation questions, behavioral STAR points, and technical topics in JSON format."""
        prompt = f"""Create a tailored interview preparation guide by analyzing the candidate's resume and target job description.
        
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide the output in JSON format with three main sections:
1. "common_questions": 3-4 standard/situational questions with tailored model answers highlighting this specific candidate's strengths.
2. "behavioral_star": 3 behavioral questions mapped to specific projects/experiences on the resume. For each, outline the STAR response structure (Situation, Task, Action, Result).
3. "technical_topics": 3-4 core technical topics, questions, or system concepts likely to be tested, along with bullet-point explanations of how this candidate can answer.

Output format:
{{
  "common_questions": [
    {{
      "question": "...",
      "why_they_ask": "...",
      "suggested_answer": "..."
    }}
  ],
  "behavioral_star": [
    {{
      "question": "...",
      "situation": "...",
      "task": "...",
      "action": "...",
      "result": "..."
    }}
  ],
  "technical_topics": [
    {{
      "topic": "...",
      "question": "...",
      "key_talking_points": ["...", "..."]
    }}
  ]
}}

Return ONLY valid JSON, no conversational markdown or prefixes.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an elite tech recruiter and interviewer. You must output ONLY a valid JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        try:
            cleaned = self._clean_json_content(response.choices[0].message.content)
            return json.loads(cleaned)
        except Exception as e:
            return {
                "error": f"Failed to parse prep guide: {str(e)}",
                "common_questions": [],
                "behavioral_star": [],
                "technical_topics": []
            }

    def interview_mock_response(self, chat_history, user_answer, last_question, job_description):
        """Analyze a user's answer in a mock interview, give constructive feedback, and ask the next question."""
        messages = [
            {
                "role": "system", 
                "content": f"You are a friendly but rigorous technical recruiter conducting a mock interview for a role described in this job description:\n{job_description}\n\nAssess their answers constructively, point out what was strong and what could be added (like metrics or details), and then naturally ask the next relevant question."
            }
        ]
        
        # Add history
        for item in chat_history:
            messages.append({"role": item["role"], "content": item["content"]})
            
        # Add user's latest response
        user_msg = f"Last question asked: \"{last_question}\"\nMy response: \"{user_answer}\"\n\nPlease evaluate my response, give constructive feedback (strengths and areas of improvement), and ask your next question."
        messages.append({"role": "user", "content": user_msg})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def generate_bullet_suggestion(self, role, company, basic_description):
        """AI Resume Builder helper: Enhances a basic bullet description into a metric-driven, action-verb ATS optimized bullet."""
        prompt = f"""Transform the following basic description of a task/experience into a high-impact, professional, ATS-friendly resume bullet point. Use a strong action verb and make it sound metric-driven (estimate reasonable metrics or add placeholders like '[X]%').
        
Role: {role}
Company: {company}
Task description: {basic_description}

Return ONLY the single bullet point string. Do not include bullet points characters like '*' or '-', or any introduction.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Return ONLY a single enhanced sentence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip().lstrip('-*• ')

    def generate_summary_suggestion(self, personal_info, experiences, skills, target_job):
        """AI Resume Builder helper: Generates a professional summary based on profile details."""
        prompt = f"""Write a professional, compelling, 3-sentence summary for a candidate's resume.
        
Candidate profile details:
- Name/Title: {personal_info.get('name', 'Professional')} - {personal_info.get('title', 'Specialist')}
- Recent Roles: {', '.join([exp.get('job_title', '') + ' at ' + exp.get('company', '') for exp in experiences[:2]])}
- Key Skills: {', '.join(skills[:6])}
- Target Job / Industry: {target_job if target_job else 'relevant tech roles'}

Draft a summary highlighting years of experience (if any), technical competence, and value add. Return ONLY the summary text, no introduction.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Return ONLY a professional 3-sentence paragraph."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
