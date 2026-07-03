from utils.file_handler import FileHandler
from utils.text_processor import TextProcessor
from utils.llm_handler import LLMHandler

class ResumeAnalyzer:
    """Main resume analyzer orchestrating all components"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.text_processor = TextProcessor()
        self.llm_handler = LLMHandler()
    
    def run_full_analysis(self, resume_text, job_description):
        """
        Run complete analysis of resume against job description
        
        Args:
            resume_text (str): Extracted resume text
            job_description (str): Job description text
            
        Returns:
            dict: Complete analysis results
        """
        
        # Clean texts
        resume_text = self.text_processor.clean_text(resume_text)
        job_description = self.text_processor.clean_text(job_description)
        
        # Extract skills
        resume_skills = self.text_processor.extract_skills(resume_text)
        job_skills = self.text_processor.extract_skills(job_description)
        
        # Get LLM analysis
        analysis = self.llm_handler.analyze_resume(resume_text, job_description)
        
        # Run static ATS formatting checks
        formatting_result = self.text_processor.check_ats_formatting(resume_text)
        
        # Get suggestions
        suggestions = self.llm_handler.get_suggestions(
            resume_text, 
            job_description, 
            analysis
        )
        
        # Generate improved resume
        improved_resume = self.llm_handler.generate_improved_resume(
            resume_text,
            job_description,
            suggestions
        )
        
        # Compile results
        result = {
            "match_score": analysis.get("match_score", 0),
            "skills_match": self.text_processor.calculate_match_score(resume_skills, job_skills),
            "experience_match": analysis.get("experience_match", 0),
            "matching_skills": analysis.get("matching_skills", []),
            "missing_skills": analysis.get("missing_skills", []),
            "strengths": analysis.get("strengths", []),
            "concerns": analysis.get("concerns", []),
            "education_assessment": analysis.get("education_assessment", ""),
            "ats_formatting": formatting_result,
            "suggestions": suggestions,
            "improved_resume": improved_resume,
            "resume_skills_found": resume_skills,
            "job_skills_required": job_skills,
            "total_resume_skills": len(resume_skills),
            "total_job_skills": len(job_skills)
        }
        
        return result

