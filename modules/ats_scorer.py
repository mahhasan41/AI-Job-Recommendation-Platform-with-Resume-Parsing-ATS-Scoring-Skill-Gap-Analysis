"""
ATS (Applicant Tracking System) Score Module
Calculates resume compatibility scores against job descriptions
"""
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def preprocess_text(text):
    """Clean and preprocess text"""
    if not text or not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_keywords(text, top_n=20):
    """Extract important keywords from text using TF-IDF"""
    if not text:
        return []
    
    try:
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Get keywords sorted by score
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [kw for kw, score in keyword_scores if score > 0]
    except:
        return []


def calculate_keyword_match(resume_text, job_text):
    """
    Calculate keyword match percentage
    
    Returns:
        Dictionary with match details
    """
    job_keywords = extract_keywords(job_text, top_n=30)
    resume_keywords = extract_keywords(resume_text, top_n=50)
    
    if not job_keywords:
        return {
            'score': 0,
            'matched': [],
            'missing': [],
            'total_required': 0,
            'percentage': 0
        }
    
    # Find matched keywords
    resume_keywords_set = set(resume_keywords)
    matched_keywords = [kw for kw in job_keywords if kw in resume_keywords_set]
    missing_keywords = [kw for kw in job_keywords if kw not in resume_keywords_set]
    
    match_percentage = (len(matched_keywords) / len(job_keywords)) * 100 if job_keywords else 0
    
    return {
        'score': match_percentage,
        'matched': matched_keywords[:15],
        'missing': missing_keywords[:10],
        'total_required': len(job_keywords),
        'total_matched': len(matched_keywords),
        'percentage': match_percentage
    }


def calculate_skills_match(user_skills, job_description):
    """
    Calculate skills match score
    
    Args:
        user_skills: String or list of user skills
        job_description: Job description text
    
    Returns:
        Dictionary with skills match details
    """
    # Convert user skills to list
    if isinstance(user_skills, str):
        user_skills_list = [s.strip().lower() for s in user_skills.split(',')]
    else:
        user_skills_list = [str(s).lower() for s in user_skills]
    
    job_text_lower = job_description.lower()
    
    # Find which user skills appear in job description
    matched_skills = [skill for skill in user_skills_list if skill in job_text_lower]
    
    # Common tech skills to check for in job description
    common_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
        'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'ai',
        'data science', 'html', 'css', 'typescript', 'c++', 'c#', 'php'
    ]
    
    required_skills = [skill for skill in common_skills if skill in job_text_lower]
    missing_skills = [skill for skill in required_skills if skill not in [s.lower() for s in user_skills_list]]
    
    if required_skills:
        skills_percentage = (len(matched_skills) / len(required_skills)) * 100
    else:
        skills_percentage = 100 if matched_skills else 50
    
    return {
        'score': min(skills_percentage, 100),
        'matched': matched_skills[:10],
        'missing': missing_skills[:10],
        'total_required': len(required_skills),
        'total_matched': len(matched_skills),
        'percentage': min(skills_percentage, 100)
    }


def calculate_experience_match(user_experience, job_description):
    """
    Calculate experience relevance score
    
    Returns:
        Dictionary with experience match details
    """
    if not user_experience or not job_description:
        return {'score': 50, 'details': 'Unable to assess experience match'}
    
    experience_keywords = ['year', 'years', 'experience', 'worked', 'developed', 'managed', 'led']
    job_lower = job_description.lower()
    exp_lower = user_experience.lower()
    
    # Check for experience keywords in both
    job_has_exp = any(kw in job_lower for kw in experience_keywords)
    user_has_exp = any(kw in exp_lower for kw in experience_keywords)
    
    # Simple text similarity for experience sections
    if job_has_exp and user_has_exp:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf = vectorizer.fit_transform([exp_lower, job_lower])
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            score = similarity * 100
        except:
            score = 60
    else:
        score = 50
    
    return {
        'score': score,
        'details': 'Good match' if score >= 70 else 'Moderate match' if score >= 50 else 'Needs improvement'
    }


def calculate_education_match(user_education, job_description):
    """
    Calculate education match score
    
    Returns:
        Dictionary with education match details
    """
    if not user_education or not job_description:
        return {'score': 50, 'details': 'No education requirements specified'}
    
    education_levels = {
        'phd': 100,
        'doctorate': 100,
        'master': 80,
        'msc': 80,
        'mba': 80,
        'bachelor': 60,
        'bsc': 60,
        'associate': 40,
        'diploma': 30,
        'high school': 20
    }
    
    job_lower = job_description.lower()
    edu_lower = user_education.lower()
    
    # Find highest education level in user's profile
    user_level = 0
    user_degree = None
    for degree, level in education_levels.items():
        if degree in edu_lower and level > user_level:
            user_level = level
            user_degree = degree
    
    # Find required education level in job
    required_level = 0
    required_degree = None
    for degree, level in education_levels.items():
        if degree in job_lower and level > required_level:
            required_level = level
            required_degree = degree
    
    # Calculate score
    if required_level == 0:
        score = 80  # No specific requirement
        details = 'No specific education requirement'
    elif user_level >= required_level:
        score = 100
        details = f'✓ Meets requirement ({user_degree})'
    elif user_level > 0:
        score = (user_level / required_level) * 100
        details = f'Partial match ({user_degree} vs {required_degree} required)'
    else:
        score = 40
        details = 'Education information needed'
    
    return {
        'score': min(score, 100),
        'details': details
    }


def calculate_ats_score(user_profile, job):
    """
    Calculate comprehensive ATS score
    
    Args:
        user_profile: Dict with keys: skills, education, experience
        job: Dict with job details (title, description, etc.)
    
    Returns:
        Dictionary with overall score and detailed breakdown
    """
    # Combine user profile text
    resume_text = f"{user_profile.get('skills', '')} {user_profile.get('education', '')} {user_profile.get('experience', '')}"
    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('category', '')}"
    
    # Calculate individual scores
    keyword_match = calculate_keyword_match(resume_text, job_text)
    skills_match = calculate_skills_match(user_profile.get('skills', ''), job_text)
    experience_match = calculate_experience_match(user_profile.get('experience', ''), job_text)
    education_match = calculate_education_match(user_profile.get('education', ''), job_text)
    
    # Calculate weighted overall score
    # Keywords: 35%, Skills: 35%, Experience: 20%, Education: 10%
    overall_score = (
        keyword_match['score'] * 0.35 +
        skills_match['score'] * 0.35 +
        experience_match['score'] * 0.20 +
        education_match['score'] * 0.10
    )
    
    # Generate improvement suggestions
    suggestions = []
    
    if keyword_match['missing']:
        suggestions.append(f"Add these keywords: {', '.join(keyword_match['missing'][:5])}")
    
    if skills_match['missing']:
        suggestions.append(f"Consider learning: {', '.join(skills_match['missing'][:3])}")
    
    if experience_match['score'] < 60:
        suggestions.append("Expand your experience section with quantifiable achievements")
    
    if keyword_match['score'] < 70:
        suggestions.append("Tailor your resume to match job description keywords")
    
    # Score interpretation
    if overall_score >= 80:
        interpretation = "Excellent Match"
        color = "success"
    elif overall_score >= 60:
        interpretation = "Good Match"
        color = "warning"
    elif overall_score >= 40:
        interpretation = "Fair Match"
        color = "info"
    else:
        interpretation = "Needs Improvement"
        color = "danger"
    
    return {
        'overall_score': round(overall_score, 1),
        'interpretation': interpretation,
        'color': color,
        'breakdown': {
            'keyword_match': keyword_match,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match
        },
        'suggestions': suggestions,
        'job_title': job.get('title', 'Unknown Position'),
        'company': job.get('company', 'Unknown Company')
    }
