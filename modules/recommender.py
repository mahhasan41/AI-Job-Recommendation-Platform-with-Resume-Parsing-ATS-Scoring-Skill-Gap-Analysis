"""
AI-Based Job Recommender Module
Uses TF-IDF vectorization and cosine similarity to match jobs with user profiles
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download required NLTK data if needed
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def preprocess_text(text):
    """
    Preprocess text for similarity matching
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def combine_user_profile(profile_data):
    """
    Combine user profile fields into a single text string for matching
    
    Args:
        profile_data: Dictionary with keys: skills, education, experience, location
    
    Returns:
        Combined text string
    """
    parts = []
    
    if profile_data.get('skills'):
        if isinstance(profile_data['skills'], list):
            parts.append(' '.join(profile_data['skills']))
        else:
            parts.append(str(profile_data['skills']))
    
    if profile_data.get('education'):
        parts.append(str(profile_data['education']))
    
    if profile_data.get('experience'):
        parts.append(str(profile_data['experience']))
    
    if profile_data.get('location'):
        parts.append(str(profile_data['location']))
    
    return ' '.join(parts)


def extract_job_text(job):
    """
    Extract and combine relevant text from a job posting
    
    Args:
        job: Dictionary containing job information
    
    Returns:
        Combined text string
    """
    parts = []
    
    if job.get('title'):
        parts.append(str(job['title']))
    
    if job.get('description'):
        parts.append(str(job['description']))
    
    if job.get('category'):
        parts.append(str(job['category']))
    
    if job.get('company'):
        parts.append(str(job['company']))
    
    return ' '.join(parts)


def calculate_similarity(user_profile_text, job_texts):
    """
    Calculate cosine similarity between user profile and multiple job descriptions
    
    Args:
        user_profile_text: Combined text from user profile
        job_texts: List of combined text from job postings
    
    Returns:
        Array of similarity scores (0-1)
    """
    if not user_profile_text or not job_texts:
        return np.zeros(len(job_texts) if job_texts else 0)
    
    # Combine user profile and all jobs for TF-IDF
    all_texts = [user_profile_text] + job_texts
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=1,
        max_df=0.95
    )
    
    try:
        # Fit and transform all texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Extract user profile vector (first one)
        user_vector = tfidf_matrix[0:1]
        
        # Extract job vectors (rest)
        job_vectors = tfidf_matrix[1:]
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_vector, job_vectors)[0]
        
        return similarities
    
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return np.zeros(len(job_texts))


def identify_skill_gaps(user_skills, job_description):
    """
    Identify skills mentioned in job description but missing from user profile
    
    Args:
        user_skills: List of user skills
        job_description: Job description text
    
    Returns:
        List of missing skills
    """
    if not job_description or not user_skills:
        return []
    
    # Normalize user skills
    user_skills_set = {skill.lower().strip() for skill in user_skills if skill}
    
    # Extract potential skills from job description
    job_text = preprocess_text(job_description.lower())
    job_words = set(word_tokenize(job_text))
    
    # Common skill keywords
    skill_keywords = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular',
        'vue', 'node', 'express', 'django', 'flask', 'spring', 'mongodb', 'mysql',
        'postgresql', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux',
        'agile', 'scrum', 'machine learning', 'ai', 'data science', 'tensorflow',
        'pytorch', 'pandas', 'numpy', 'excel', 'tableau', 'powerbi', 'salesforce'
    ]
    
    # Find skills in job description
    job_skills = []
    for keyword in skill_keywords:
        if keyword in job_text:
            job_skills.append(keyword)
    
    # Find missing skills
    missing_skills = [skill for skill in job_skills if skill not in user_skills_set]
    
    return list(set(missing_skills))[:10]  # Return top 10 missing skills


def recommend_jobs(user_profile, jobs, top_n=10):
    """
    Main recommendation function
    
    Args:
        user_profile: Dictionary with user profile data (skills, education, experience, location)
        jobs: List of job dictionaries
        top_n: Number of top recommendations to return
    
    Returns:
        List of tuples: (job_dict, similarity_score, skill_gaps)
    """
    if not jobs:
        return []
    
    # Combine user profile into text
    user_profile_text = combine_user_profile(user_profile)
    
    if not user_profile_text:
        return []
    
    # Extract job texts
    job_texts = [extract_job_text(job) for job in jobs]
    
    # Calculate similarities
    similarities = calculate_similarity(user_profile_text, job_texts)
    
    # Get user skills for gap analysis
    user_skills = []
    if user_profile.get('skills'):
        if isinstance(user_profile['skills'], list):
            user_skills = user_profile['skills']
        elif isinstance(user_profile['skills'], str):
            # Parse comma-separated or semicolon-separated skills
            user_skills = [s.strip() for s in re.split(r'[,;]', user_profile['skills'])]
    
    # Create results with similarity scores
    results = []
    for i, job in enumerate(jobs):
        similarity_score = float(similarities[i]) if i < len(similarities) else 0.0
        
        # Identify skill gaps
        job_desc = job.get('description', '')
        skill_gaps = identify_skill_gaps(user_skills, job_desc)
        
        results.append({
            'job': job,
            'similarity_score': similarity_score,
            'skill_gaps': skill_gaps
        })
    
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Return top N recommendations
    return results[:top_n]


def calculate_fit_score(similarity_score):
    """
    Convert similarity score (0-1) to a more readable fit score (0-100)
    
    Args:
        similarity_score: Cosine similarity score (0-1)
    
    Returns:
        Fit score (0-100) and label
    """
    fit_score = int(similarity_score * 100)
    
    if fit_score >= 80:
        label = "Excellent Match"
    elif fit_score >= 60:
        label = "Good Match"
    elif fit_score >= 40:
        label = "Fair Match"
    elif fit_score >= 20:
        label = "Below Average"
    else:
        label = "Poor Match"
    
    return fit_score, label

