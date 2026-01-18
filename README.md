# An AI-Powered Job Recommendation Platform: Integrating Resume Parsing, ATS Scoring, Job Matching, and Skill Gap Visualization

## 📋 Project Description

**An AI-Powered Job Recommendation Platform** is an intelligent, end-to-end job matching solution that leverages Natural Language Processing (NLP), Machine Learning (ML), and data mining techniques to connect job seekers with highly relevant opportunities. The platform automates resume analysis, calculates ATS (Applicant Tracking System) compatibility scores, performs intelligent job matching using similarity algorithms, and provides comprehensive skill gap visualization to help users improve their employability.

### Core Objectives
- 🤖 **Automated Resume Parsing**: Extract skills, experience, and education using advanced NLP
- 📊 **ATS Scoring**: Calculate resume compatibility with job postings
- 🎯 **Intelligent Job Matching**: Find the best-fit opportunities using TF-IDF and cosine similarity
- 📈 **Skill Gap Analysis**: Identify missing skills and improvement suggestions
- 📉 **Analytics Dashboard**: Visualize job market trends and salary statistics

---

## ✨ Key Features

### 1. **User Authentication & Profile Management**
- Secure user registration and login system
- Encrypted password storage
- Persistent user profiles with experience, education, and skills

### 2. **Resume Parsing & Analysis**
- Upload PDF/DOCX resume files
- Automatic extraction of:
  - Technical and soft skills
  - Professional experience
  - Educational qualifications
  - Certifications and achievements
- NLP-powered information extraction using spaCy and NLTK

### 3. **Real-Time Job Fetching**
- Integration with Adzuna Job Search API
- Live job postings from multiple sources
- Location-based filtering
- Keyword-based search
- Local caching in MySQL for performance optimization

### 4. **Intelligent Job Recommendation Engine**
- TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
- Cosine similarity algorithm for precise matching
- Top 10 personalized job recommendations
- Relevance scoring (0-100%)
- Real-time ranking

### 5. **ATS Scoring System**
- Resume compatibility analysis
- Keyword density calculation
- ATS score percentage (0-100%)
- Identification of missing keywords
- Actionable improvement suggestions

### 6. **Skill Gap Visualization**
- Visual representation of required vs. possessed skills
- Missing skills identification
- Priority-based recommendations
- Career development roadmap

### 7. **Advanced Analytics Dashboard**
- Job market trend visualization
- Salary statistics (min, max, average, median)
- Skill demand charts
- Job distribution by category and location
- Interactive data visualizations using Chart.js

### 8. **Job Bookmarking & History**
- Save favorite job postings
- Search history tracking
- Personalized saved jobs management

---

## 🏗️ Project Architecture

### Directory Structure
```
DM Project/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── SETUP.md                        # Setup instructions
├── TROUBLESHOOTING.md              # Troubleshooting guide
├── PROJECT_DOCUMENTATION.txt       # Detailed documentation
├── RUM CMD.txt                     # Command reference
├── run.ps1                         # PowerShell startup script
│
├── database/
│   ├── db_config.py               # Database configuration & connection
│   └── schema.sql                 # Database schema definitions
│
├── modules/
│   ├── resume_parser.py           # Resume parsing & NLP analysis
│   ├── job_fetcher.py             # Adzuna API integration
│   ├── ats_scorer.py              # ATS compatibility scoring
│   ├── recommender.py             # Job matching & recommendation engine
│   └── visualizer.py              # Analytics visualization
│
├── templates/
│   ├── base.html                  # Base layout template
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── dashboard.html             # Main dashboard
│   ├── profile.html               # User profile management
│   ├── find_jobs.html             # Job search interface
│   ├── results.html               # Job results & recommendations
│   ├── analytics.html             # Analytics dashboard
│   └── ats_score.html             # ATS scoring interface
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom CSS styling
│   └── js/
│       └── script.js              # Client-side JavaScript
│
├── uploads/
│   └── [user-uploaded resumes]    # Resume file storage
│
└── Data Mining Project Files/
    ├── [Reference papers]         # Research papers
    └── [Screenshots]              # Project screenshots
```

### Technology Stack

#### **Backend**
- **Language**: Python 3.8+
- **Web Framework**: Flask
- **Database**: MySQL
- **NLP Libraries**: spaCy, NLTK
- **ML Libraries**: scikit-learn, pandas, numpy
- **API Integration**: requests (HTTP)

#### **Frontend**
- **HTML5** - Markup
- **CSS3** - Styling with Bootstrap 5
- **JavaScript** - Client-side interactivity
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

#### **External Services**
- **Adzuna Job Search API** - Real-time job data
- **MySQL Server** - Data persistence

---

## 🔄 Data Flow & Algorithm Pipeline

### Resume Processing Pipeline
```
Resume Upload (PDF/DOCX)
    ↓
[resume_parser.py]
    ├── Text extraction
    ├── Tokenization (NLTK)
    ├── Named Entity Recognition (spaCy)
    ├── Skill extraction
    ├── Experience parsing
    └── Education extraction
    ↓
[database/schema.sql - profiles table]
    ↓
User Profile Created
```

### Job Matching Pipeline
```
User Profile + Job Search Query
    ↓
[job_fetcher.py]
    ├── Call Adzuna API
    ├── Fetch job listings
    └── Cache in MySQL
    ↓
[recommender.py]
    ├── TF-IDF Vectorization
    ├── Cosine Similarity Calculation
    └── Ranking & Sorting
    ↓
[ats_scorer.py]
    ├── Keyword matching
    ├── Score calculation
    └── Gap analysis
    ↓
[results.html]
    ├── Display top 10 matches
    ├── Show relevance scores
    └── List missing skills
    ↓
[visualizer.py]
    ├── Generate charts
    ├── Analytics insights
    └── Market trends
```

### Similarity Algorithm
**Cosine Similarity Formula**:
```
similarity = (A · B) / (||A|| × ||B||)
```
Where A and B are TF-IDF vectors of user profile and job description.

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+** (Not Python 3.13)
- **MySQL Server** (installed and running)
- **pip** (Python package manager)
- **Git** (for version control)

### Step 1: Clone the Repository
```bash
cd c:\Users\GLOBAL TECHNOLOGY\Desktop\DM Lab
git clone <repository-url>
cd DM\ Project
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**On Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt)**:
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux**:
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Database

1. Open MySQL and create database:
```sql
CREATE DATABASE job_finder_db;
```

2. Update database credentials in `database/db_config.py`:
```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_password'
DB_NAME = 'job_finder_db'
```

3. Execute schema:
```bash
mysql -u root -p job_finder_db < database/schema.sql
```

### Step 6: Configure Adzuna API

Update credentials in `modules/job_fetcher.py`:
```python
ADZUNA_APP_ID = ''
ADZUNA_APP_KEY = ''
```

### Step 7: Run Application

**Using PowerShell**:
```powershell
.\run.ps1
```

**Using Command Prompt**:
```cmd
python app.py
```

**Using Flask CLI**:
```bash
flask run
```

### Step 8: Access Application
Open browser and navigate to:
```
http://localhost:5000
```

---

## 📖 Usage Guide

### 1. **Create Account**
- Click "Sign Up"
- Enter email and password
- Confirm registration

### 2. **Upload Resume** (Option A)
- Go to Dashboard
- Click "Upload Resume"
- Select PDF/DOCX file (max 16MB)
- System automatically extracts information

### 3. **Manual Profile Entry** (Option B)
- Go to Profile
- Enter skills, experience, education manually
- Save profile

### 4. **Search Jobs**
- Navigate to "Find Jobs"
- Enter job title/keyword
- Select location
- Click "Search"

### 5. **Review Recommendations**
- View top 10 matching jobs
- Check relevance scores (%)
- Review ATS compatibility scores
- See skill gaps per job

### 6. **Save Jobs**
- Click "Save" on desired jobs
- Access saved jobs from Dashboard

### 7. **View Analytics**
- Go to Analytics Dashboard
- Explore market trends
- Check salary statistics
- Identify in-demand skills

---

## 🧠 Machine Learning Algorithms

### TF-IDF (Term Frequency-Inverse Document Frequency)
- Converts text into numerical vectors
- Weights important words higher
- Formula: `TF-IDF(t,d) = TF(t,d) × IDF(t)`

### Cosine Similarity
- Measures similarity between two vectors
- Range: 0 (completely different) to 1 (identical)
- Output: Percentage match (0-100%)

### Named Entity Recognition (NER)
- Identifies skills, locations, organizations
- Uses spaCy pre-trained models
- Extracts structured information from unstructured text

### Keyword Matching (ATS Scoring)
- Analyzes keyword density
- Compares resume keywords with job requirements
- Calculates compatibility percentage
- Identifies missing keywords

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Profiles Table
```sql
CREATE TABLE profiles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT UNIQUE,
  skills TEXT,
  experience TEXT,
  education TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  job_id VARCHAR(255) UNIQUE,
  title VARCHAR(255),
  company VARCHAR(255),
  location VARCHAR(255),
  description LONGTEXT,
  salary_min INT,
  salary_max INT,
  posted_date TIMESTAMP,
  cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Saved Jobs Table
```sql
CREATE TABLE saved_jobs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  job_id INT,
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

### Search History Table
```sql
CREATE TABLE search_history (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  search_query VARCHAR(255),
  search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## ⚙️ Configuration Details

### Environment Variables
Create `.env` file in root directory:
```env
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=job_finder_db
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
MAX_FILE_SIZE=16777216
ALLOWED_EXTENSIONS=pdf,doc,docx
```

### File Upload Restrictions
- **Formats**: PDF, DOC, DOCX
- **Max Size**: 16 MB
- **Storage Location**: `uploads/`

### API Configuration
- **Adzuna API**: Real-time job fetching
- **Rate Limit**: Check Adzuna documentation
- **Cache Duration**: 24 hours (configurable)

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: spaCy` | Python 3.13 incompatibility | Downgrade to Python 3.12 or lower |
| `MySQL Connection Error` | Database not running | Start MySQL server: `mysql.server start` |
| `API Rate Limit Exceeded` | Too many concurrent requests | Implement request queuing or caching |
| `Resume Parsing Error` | Corrupted PDF | Validate file format and try again |
| `No Jobs Found` | Invalid search parameters | Check location and keyword spelling |

For more details, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📋 Dependencies

See [requirements.txt](requirements.txt) for complete list:

```
Flask==2.3.2
MySQL-connector-python==8.0.33
spacy==3.5.0
nltk==3.8.1
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
Werkzeug==2.3.6
```

---

## 🔐 Security Features

- ✅ Password hashing with Werkzeug
- ✅ SQL injection prevention (parameterized queries)
- ✅ File upload validation (format & size checks)
- ✅ Session-based authentication
- ✅ CSRF protection in Flask
- ⚠️ **TODO**: Implement HTTPS/SSL
- ⚠️ **TODO**: Add rate limiting
- ⚠️ **TODO**: Implement OAuth 2.0

---

## 📈 Performance Optimization

- **Database Indexing**: Optimized frequently queried columns
- **API Caching**: Cache job results in MySQL (24-hour TTL)
- **TF-IDF Caching**: Pre-compute user profile vectors
- **Lazy Loading**: Load recommendations on-demand
- **Connection Pooling**: Reuse database connections

**Scalability Roadmap**:
- Implement Celery for async job processing
- Add Redis caching layer
- Optimize NLP pipeline for batch processing
- Database sharding for large user bases

---

## 🚀 Deployment Guide

### Production Checklist
- [ ] Change Flask secret key to secure random value
- [ ] Set `FLASK_ENV=production`
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Implement rate limiting
- [ ] Set up error tracking (Sentry)
- [ ] Enable CORS for frontend
- [ ] Use production-grade WSGI server (Gunicorn)

### Deploy to Heroku
```bash
heroku create your-app-name
heroku addons:create cleardb:ignite
git push heroku main
heroku open
```

### Deploy to AWS/Azure
- Use RDS for MySQL
- Deploy on EC2 or App Service
- Configure S3 for file storage
- Set up CloudFront for CDN

---


## 🎓 Learning Outcomes

This project demonstrates:
- **Data Mining**: Text extraction, NLP, feature engineering
- **Machine Learning**: TF-IDF, cosine similarity, clustering
- **Web Development**: Flask, database design, API integration
- **Software Engineering**: Modular architecture, design patterns
- **Data Visualization**: Charts, dashboards, analytics
- **Database Design**: Schema design, optimization, indexing
- **API Integration**: RESTful API consumption, data aggregation
- **Security**: Authentication, authorization, data protection

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 👥 Authors & Contributors

- **Project Lead**: Md. Mahmudol Hasan
- **Contributors**: [Rudra Roy, Khadija Begum]

---


## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Resume parsing & analysis
- ✅ Job fetching from Adzuna
- ✅ Basic job recommendation
- ✅ ATS scoring
- ✅ Analytics dashboard

### Version 1.1 (Planned)
- 🔄 Multi-resume support
- 🔄 Interview preparation tips
- 🔄 Company reviews integration
- 🔄 Networking suggestions

### Version 2.0 (Future)
- 🔄 AI chatbot for career guidance
- 🔄 Resume optimization suggestions
- 🔄 Salary negotiation tips
- 🔄 Mobile app
- 🔄 Integration with LinkedIn
- 🔄 Skill assessment tests

---

## 📊 Statistics & Metrics

- **Total Functions**: 50+
- **Database Tables**: 5
- **API Endpoints**: 25+
- **Supported File Formats**: 3 (PDF, DOC, DOCX)
- **Max Resume File Size**: 16 MB
- **Job Recommendation Count**: Top 10
- **ATS Score Range**: 0-100%

---

## 🙏 Acknowledgments

- Adzuna for job data API
- spaCy for NLP models
- scikit-learn for ML algorithms
- Bootstrap for responsive UI
- Flask community for excellent documentation

---

**Last Updated**: January 18, 2026  
**Version**: 1.0.0  
**Status**: Active Development

---