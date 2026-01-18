"""
Resume Parser Module
Extracts text from PDF/DOCX files and processes using NLP to extract skills and information
"""
import os
import re
import PyPDF2
from docx import Document
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Note: spaCy is not installed. Some advanced NLP features will be disabled.")
    nlp = None

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Load spaCy model if available (download if needed: python -m spacy download en_core_web_sm)
if SPACY_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
        nlp = None
else:
    nlp = None

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Common technical skills keywords
TECH_SKILLS = [
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular', 'vue',
    'node', 'express', 'django', 'flask', 'spring', 'mongodb', 'mysql', 'postgresql',
    'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'agile', 'scrum',
    'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'pandas',
    'numpy', 'excel', 'tableau', 'powerbi', 'salesforce', 'oracle', 'sap'
]


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""


def extract_text_from_resume(file_path):
    """Extract text from resume file (PDF or DOCX)"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx') or file_path.endswith('.doc'):
        return extract_text_from_docx(file_path)
    else:
        return ""


def preprocess_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text):
    """Extract skills from resume text using NLP and keyword matching"""
    if not text:
        return []
    
    # Preprocess text
    processed_text = preprocess_text(text)
    
    # Tokenize and remove stopwords
    tokens = word_tokenize(processed_text)
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Lemmatize
    lemmatized = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    
    # Find matching skills
    found_skills = []
    
    # Check against known tech skills
    text_lower = processed_text.lower()
    for skill in TECH_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill.title())
    
    # Use spaCy for entity recognition if available
    if nlp and SPACY_AVAILABLE:
        try:
            doc = nlp(processed_text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY']:
                    found_skills.append(ent.text.title())
        except Exception:
            # Fallback if spaCy processing fails
            pass
    
    # Remove duplicates and return
    return list(set(found_skills))


def extract_education(text):
    """Extract education information from resume"""
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'education']
    education_info = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            # Get the line and context
            context = ' '.join(lines[max(0, i-1):min(len(lines), i+2)])
            education_info.append(context.strip())
    
    return '; '.join(education_info[:3])  # Return first 3 education mentions


def extract_experience(text):
    """Extract experience information from resume"""
    experience_keywords = ['experience', 'worked', 'employed', 'years', 'project', 'developed']
    experience_info = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            context = ' '.join(lines[max(0, i-1):min(len(lines), i+3)])
            experience_info.append(context.strip())
    
    return '; '.join(experience_info[:5])  # Return first 5 experience mentions


def parse_resume(file_path):
    """
    Main function to parse resume and extract structured information
    Returns a dictionary with extracted data
    """
    text = extract_text_from_resume(file_path)
    
    if not text:
        return {
            'skills': [],
            'education': '',
            'experience': '',
            'raw_text': ''
        }
    
    return {
        'skills': extract_skills(text),
        'education': extract_education(text),
        'experience': extract_experience(text),
        'raw_text': text
    }

