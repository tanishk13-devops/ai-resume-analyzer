import re
from collections import Counter

class TextProcessor:
    """Process and extract information from resume text"""
    
    COMMON_SKILLS = {
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift',
        'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring', 'Node.js', 'Express',
        'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Firebase',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN',
        'HTML', 'CSS', 'Sass', 'Webpack', 'Vite', 'Babel',
        'REST', 'GraphQL', 'API', 'WebSocket', 'OAuth',
        'Machine Learning', 'AI', 'NLP', 'TensorFlow', 'PyTorch', 'Scikit-learn',
        'Data Analysis', 'Data Science', 'Pandas', 'NumPy', 'Matplotlib',
        'Agile', 'Scrum', 'Kanban', 'CI/CD', 'DevOps',
        'Excel', 'Power BI', 'Tableau', 'Looker',
        'Linux', 'Windows', 'macOS', 'Unix',
        'Communication', 'Leadership', 'Problem-solving', 'Project Management',
        'Team player', 'Collaboration', 'Creativity', 'Critical thinking'
    }
    
    def __init__(self):
        self.skills_database = self.COMMON_SKILLS
    
    def extract_skills(self, text):
        """Extract skills from text"""
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.skills_database:
            if skill.lower() in text_lower:
                found_skills.add(skill)
        
        return list(found_skills)
    
    def extract_experience_years(self, text):
        """Extract years of experience from text"""
        # Look for patterns like "5 years", "5+ years", etc.
        pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            years = [int(m) for m in matches]
            return max(years)  # Return highest mentioned years
        
        return 0
    
    def extract_education(self, text):
        """Extract education information"""
        degrees = {
            'bachelor': 'Bachelor\'s Degree',
            'master': 'Master\'s Degree',
            'phd': 'PhD',
            'associate': 'Associate Degree',
            'diploma': 'Diploma'
        }
        
        found_degrees = []
        text_lower = text.lower()
        
        for degree_key, degree_name in degrees.items():
            if degree_key in text_lower:
                found_degrees.append(degree_name)
        
        return found_degrees
    
    def clean_text(self, text):
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s.,\-]', '', text)
        
        return text.strip()
    
    def extract_sections(self, text):
        """Extract major sections from resume"""
        sections = {
            'summary': None,
            'experience': None,
            'education': None,
            'skills': None,
            'projects': None,
            'certifications': None
        }
        
        section_patterns = {
            'summary': r'(?:summary|profile|objective)',
            'experience': r'(?:experience|employment|work history)',
            'education': r'(?:education|academic)',
            'skills': r'(?:skills|technical skills|competencies)',
            'projects': r'(?:projects|portfolio)',
            'certifications': r'(?:certifications|licenses)'
        }
        
        text_lower = text.lower()
        
        for section, pattern in section_patterns.items():
            if re.search(pattern, text_lower):
                sections[section] = True
        
        return sections
    
    def calculate_match_score(self, resume_skills, job_skills):
        """Calculate skill match percentage"""
        if not job_skills:
            return 0
        
        matching = set(resume_skills) & set(job_skills)
        score = (len(matching) / len(job_skills)) * 100
        
        return min(score, 100)

    def check_ats_formatting(self, text):
        """
        Run static heuristic formatting checks for ATS compatibility
        
        Returns:
            dict: Formatting score, passed checks, failed checks
        """
        passed = []
        failed = []
        score = 100
        
        # 1. Contact Information Checks
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        has_linkedin = 'linkedin.com/' in text.lower() or 'linkedin.com' in text.lower()
        
        if has_email:
            passed.append({"check": "Email Address found", "tip": "Essential for recruiter contact."})
        else:
            failed.append({"check": "Missing Email Address", "tip": "Ensure your email is clearly visible at the top.", "score_impact": 15})
            score -= 15
            
        if has_phone:
            passed.append({"check": "Phone Number found", "tip": "Essential for recruiter contact."})
        else:
            failed.append({"check": "Missing Phone Number", "tip": "Include a contact phone number in your header.", "score_impact": 15})
            score -= 15
            
        if has_linkedin:
            passed.append({"check": "LinkedIn Profile link found", "tip": "Helps recruiters verify details."})
        else:
            failed.append({"check": "Missing LinkedIn Link", "tip": "Add a link to your LinkedIn profile in the header.", "score_impact": 10})
            score -= 10
            
        # 2. Section Headings Checks
        sections = self.extract_sections(text)
        required_sections = {
            'experience': 'Work Experience / Professional Experience',
            'skills': 'Skills / Technologies',
            'education': 'Education / Academic Background'
        }
        
        for key, name in required_sections.items():
            if sections.get(key):
                passed.append({"check": f"Standard '{name}' section found", "tip": "ATS parses standard headings easily."})
            else:
                failed.append({"check": f"Missing or non-standard '{name}' heading", "tip": f"Ensure you have a clearly labeled '{name}' section header.", "score_impact": 15})
                score -= 15
                
        # 3. Bullet Points Check
        bullet_pattern = r'[\u2022\u2023\u25E6\u2043\u2219\-]\s+\w+'
        has_bullets = bool(re.search(bullet_pattern, text))
        
        if has_bullets:
            passed.append({"check": "Action-oriented bullet points detected", "tip": "Bullet points make descriptions readable for both ATS and humans."})
        else:
            failed.append({"check": "No standard bullet points detected", "tip": "Use standard bullet points (-, •) for your experience descriptions instead of long paragraphs.", "score_impact": 15})
            score -= 15
            
        # 4. Word Count Check
        word_count = len(text.split())
        if 200 <= word_count <= 1500:
            passed.append({"check": f"Ideal resume length ({word_count} words)", "tip": "Keep it between 200 and 1500 words for a 1-2 page resume."})
        else:
            if word_count < 200:
                failed.append({"check": f"Resume is too short ({word_count} words)", "tip": "Add more details about your work experience and skills.", "score_impact": 15})
                score -= 15
            else:
                failed.append({"check": f"Resume is very long ({word_count} words)", "tip": "Try to condense your descriptions. Aim for 1-2 pages.", "score_impact": 10})
                score -= 10
                
        # Normalize score between 0 and 100
        score = max(0, min(score, 100))
        
        return {
            "score": score,
            "passed": passed,
            "failed": failed
        }

