"""
Job Fetcher Module
Fetches jobs from Adzuna API and caches them in MySQL
"""
import requests
import json
from datetime import datetime
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    # Fallback if mysql-connector-python is not installed
    print("Warning: mysql-connector-python not found. Using alternative.")
    mysql = None
    Error = Exception
from database.db_config import DB_CONFIG

# Adzuna API Configuration
APP_ID = "13db5e2e"
APP_KEY = "7627ce049a9510af7c6843498553d8ce"
BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def get_db_connection():
    """Create and return MySQL database connection"""
    if mysql is None:
        print("Error: mysql-connector-python is not installed.")
        return None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def fetch_jobs_from_api(job_title="", location="", salary_min=None, salary_max=None, results_per_page=50):
    """
    Fetch jobs from Adzuna API
    
    Args:
        job_title: Job title or keywords to search
        location: Location (e.g., "us", "gb", "au")
        salary_min: Minimum salary
        salary_max: Maximum salary
        results_per_page: Number of results to fetch (max 50)
    
    Returns:
        List of job dictionaries
    """
    url = f"{BASE_URL}/{location}/search/{1}"  # Page 1
    
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'results_per_page': min(results_per_page, 50),
        'sort_by': 'date',
        'content-type': 'application/json'
    }
    
    if job_title:
        params['what'] = job_title
    if salary_min:
        params['salary_min'] = salary_min
    if salary_max:
        params['salary_max'] = salary_max
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        if 'results' in data:
            for job in data['results']:
                job_data = {
                    'job_id': str(job.get('id', '')),
                    'title': job.get('title', ''),
                    'company': job.get('company', {}).get('display_name', 'Unknown'),
                    'description': job.get('description', ''),
                    'location': job.get('location', {}).get('display_name', ''),
                    'salary_min': job.get('salary_min', 0),
                    'salary_max': job.get('salary_max', 0),
                    'category': job.get('category', {}).get('label', ''),
                    'url': job.get('redirect_url', ''),
                    'date_posted': job.get('created', '')[:10] if job.get('created') else None
                }
                jobs.append(job_data)
        
        return jobs
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs from API: {e}")
        return []


def cache_jobs_in_db(jobs):
    """
    Cache fetched jobs in MySQL database
    """
    if not jobs:
        return
    
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        for job in jobs:
            # Insert or update job
            query = """
                INSERT INTO jobs (job_id, title, company, description, location, 
                                salary_min, salary_max, category, url, date_posted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    company = VALUES(company),
                    description = VALUES(description),
                    location = VALUES(location),
                    salary_min = VALUES(salary_min),
                    salary_max = VALUES(salary_max),
                    category = VALUES(category),
                    url = VALUES(url),
                    date_posted = VALUES(date_posted),
                    cached_at = CURRENT_TIMESTAMP
            """
            
            cursor.execute(query, (
                job['job_id'],
                job['title'],
                job['company'],
                job['description'],
                job['location'],
                job['salary_min'],
                job['salary_max'],
                job['category'],
                job['url'],
                job['date_posted']
            ))
        
        connection.commit()
        print(f"Cached {len(jobs)} jobs in database")
    
    except Error as e:
        print(f"Error caching jobs: {e}")
        connection.rollback()
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_cached_jobs(limit=100, job_title_filter=None, location_filter=None):
    """
    Retrieve cached jobs from database
    
    Args:
        limit: Maximum number of jobs to retrieve
        job_title_filter: Filter by job title (case-insensitive partial match)
        location_filter: Filter by location
    
    Returns:
        List of job dictionaries
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if job_title_filter:
            query += " AND title LIKE %s"
            params.append(f"%{job_title_filter}%")
        
        if location_filter:
            query += " AND location LIKE %s"
            params.append(f"%{location_filter}%")
        
        query += " ORDER BY cached_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        
        return jobs
    
    except Error as e:
        print(f"Error retrieving cached jobs: {e}")
        return []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def search_jobs(job_title="", location="", use_cache=True, max_results=50):
    """
    Search for jobs - checks cache first, then API if needed
    
    Args:
        job_title: Job title/keywords
        location: Location code (e.g., "us", "gb")
        use_cache: Whether to use cached results first
        max_results: Maximum number of results
    
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    # Try cache first if enabled
    if use_cache:
        jobs = get_cached_jobs(limit=max_results, 
                              job_title_filter=job_title if job_title else None,
                              location_filter=location if location else None)
    
    # If cache doesn't have enough results or cache disabled, fetch from API
    if len(jobs) < max_results or not use_cache:
        api_jobs = fetch_jobs_from_api(job_title=job_title, 
                                       location=location,
                                       results_per_page=max_results)
        
        # Cache the fetched jobs
        if api_jobs:
            cache_jobs_in_db(api_jobs)
        
        # Combine and deduplicate
        existing_ids = {job['job_id'] for job in jobs}
        new_jobs = [job for job in api_jobs if job['job_id'] not in existing_ids]
        jobs.extend(new_jobs)
    
    # Return top max_results
    return jobs[:max_results]

