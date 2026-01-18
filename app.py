"""
Main Flask Application for AI-Driven Real-Time Job Finder and Resume Matcher
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    # Fallback if mysql-connector-python is not installed
    print("Warning: mysql-connector-python not found. Using alternative.")
    mysql = None
    Error = Exception
from database.db_config import DB_CONFIG
from modules.resume_parser import parse_resume
from modules.job_fetcher import search_jobs, get_cached_jobs
from modules.recommender import recommend_jobs, calculate_fit_score
from modules.visualizer import prepare_chart_data, format_chart_data_for_chartjs
from modules.ats_scorer import calculate_ats_score
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this to a secure secret key in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    """Create and return MySQL database connection"""
    if mysql is None:
        print("Error: mysql-connector-python is not installed. Please install it using: pip install mysql-connector-python")
        return None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error. Please try again.', 'danger')
            return render_template('register.html')
        
        try:
            cursor = connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please login instead.', 'danger')
                return render_template('register.html')
            
            # Hash password and insert user
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            connection.commit()
            
            # Get user ID and create session
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            
            flash('Registration successful! Welcome to Job Finder.', 'success')
            return redirect(url_for('dashboard'))
        
        except Error as e:
            flash(f'Registration error: {str(e)}', 'danger')
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error. Please try again.', 'danger')
            return render_template('login.html')
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        
        except Error as e:
            flash(f'Login error: {str(e)}', 'danger')
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/profile')
@login_required
def profile():
    """View user profile (read-only)"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    
    # GET request - fetch current profile
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = %s",
            (user_id,)
        )
        profile = cursor.fetchone()
        
        # Convert skills string to list if needed
        if profile and profile.get('skills'):
            if isinstance(profile['skills'], str):
                skills_list = [s.strip() for s in profile['skills'].split(',')]
            else:
                skills_list = profile['skills']
        else:
            skills_list = []
        
    except Error as e:
        flash(f'Error fetching profile: {str(e)}', 'danger')
        profile = None
        skills_list = []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return render_template('profile.html', profile=profile, skills_list=skills_list)


@app.route('/resume', methods=['GET'])
@login_required
def resume():
    """Resume management page (upload/edit)"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    
    # GET request - fetch current profile
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = %s",
            (user_id,)
        )
        profile = cursor.fetchone()
        
        # Convert skills string to list if needed
        if profile and profile.get('skills'):
            if isinstance(profile['skills'], str):
                skills_list = [s.strip() for s in profile['skills'].split(',')]
            else:
                skills_list = profile['skills']
        else:
            skills_list = []
        
    except Error as e:
        flash(f'Error fetching profile: {str(e)}', 'danger')
        profile = None
        skills_list = []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return render_template('resume.html', profile=profile, skills_list=skills_list)


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile (manual entry)"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('resume'))
    
    user_id = session['user_id']
    
    education = request.form.get('education', '')
    skills = request.form.get('skills', '')
    experience = request.form.get('experience', '')
    location = request.form.get('location', '')
    
    try:
        cursor = connection.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM profiles WHERE user_id = %s", (user_id,))
        profile_exists = cursor.fetchone()
        
        if profile_exists:
            # Update existing profile
            cursor.execute(
                """UPDATE profiles SET education = %s, skills = %s, 
                   experience = %s, location = %s WHERE user_id = %s""",
                (education, skills, experience, location, user_id)
            )
        else:
            # Insert new profile
            cursor.execute(
                """INSERT INTO profiles (user_id, education, skills, experience, location)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, education, skills, experience, location)
            )
        
        connection.commit()
        flash('Profile updated successfully!', 'success')
    
    except Error as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
        connection.rollback()
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return redirect(url_for('resume'))


@app.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    """Handle resume upload and parsing"""
    if 'resume' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('resume'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('resume'))
    
    if file and allowed_file(file.filename):
        user_id = session['user_id']
        filename = secure_filename(f"{user_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse resume
        parsed_data = parse_resume(filepath)
        
        # Update profile with parsed data
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Convert skills list to comma-separated string
                skills_str = ', '.join(parsed_data.get('skills', []))
                
                # Check if profile exists
                cursor.execute("SELECT id FROM profiles WHERE user_id = %s", (user_id,))
                profile_exists = cursor.fetchone()
                
                if profile_exists:
                    cursor.execute(
                        """UPDATE profiles SET education = %s, skills = %s, 
                           experience = %s, resume_path = %s WHERE user_id = %s""",
                        (parsed_data.get('education', ''),
                         skills_str,
                         parsed_data.get('experience', ''),
                         filepath,
                         user_id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO profiles (user_id, education, skills, experience, resume_path)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (user_id,
                         parsed_data.get('education', ''),
                         skills_str,
                         parsed_data.get('experience', ''),
                         filepath)
                    )
                
                connection.commit()
                flash('Resume uploaded and parsed successfully!', 'success')
            
            except Error as e:
                flash(f'Error saving parsed data: {str(e)}', 'danger')
                connection.rollback()
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        return redirect(url_for('resume'))
    
    flash('Invalid file type. Please upload PDF or DOCX.', 'danger')
    return redirect(url_for('resume'))


@app.route('/find_jobs', methods=['GET', 'POST'])
@login_required
def find_jobs():
    """Job search and recommendation"""
    if request.method == 'POST':
        job_title = request.form.get('job_title', '')
        location = request.form.get('location', 'us')  # Default to US
        
        # Fetch jobs
        jobs = search_jobs(job_title=job_title, location=location, max_results=50)
        
        # Get user profile
        user_id = session['user_id']
        connection = get_db_connection()
        profile = None
        
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM profiles WHERE user_id = %s",
                    (user_id,)
                )
                profile = cursor.fetchone()
                
                # Save search history
                cursor.execute(
                    """INSERT INTO search_history (user_id, search_query, location, results_count)
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, job_title, location, len(jobs))
                )
                connection.commit()
            
            except Error as e:
                print(f"Error fetching profile: {e}")
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        # Get recommendations if profile exists
        recommendations = []
        if profile and jobs:
            profile_data = {
                'skills': profile.get('skills', ''),
                'education': profile.get('education', ''),
                'experience': profile.get('experience', ''),
                'location': profile.get('location', '')
            }
            recommendations = recommend_jobs(profile_data, jobs, top_n=10)
        
        # Prepare visualization data
        chart_data = prepare_chart_data(jobs, recommendations)
        chart_js_data = format_chart_data_for_chartjs(chart_data)
        
        return render_template('results.html',
                             jobs=jobs,
                             recommendations=recommendations,
                             job_title=job_title,
                             location=location,
                             chart_data=chart_js_data)
    
    return render_template('find_jobs.html')


@app.route('/save_job', methods=['POST'])
@login_required
def save_job():
    """Save a job to user's favorites"""
    data = request.get_json()
    job_id = data.get('job_id')
    similarity_score = data.get('similarity_score', 0)
    
    if not job_id:
        return jsonify({'success': False, 'message': 'Job ID required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database error'}), 500
    
    user_id = session['user_id']
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO saved_jobs (user_id, job_id, similarity_score)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE similarity_score = %s""",
            (user_id, job_id, similarity_score, similarity_score)
        )
        connection.commit()
        return jsonify({'success': True, 'message': 'Job saved successfully'})
    
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/saved_jobs')
@login_required
def saved_jobs():
    """View saved jobs"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    saved_jobs_list = []
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Get saved jobs with job details
        cursor.execute(
            """SELECT sj.id, sj.job_id, sj.similarity_score, sj.saved_at,
                      j.title, j.company, j.description, j.location, 
                      j.salary_min, j.salary_max, j.category, j.url
               FROM saved_jobs sj
               JOIN jobs j ON sj.job_id = j.job_id
               WHERE sj.user_id = %s
               ORDER BY sj.saved_at DESC""",
            (user_id,)
        )
        saved_jobs_list = cursor.fetchall()
        
        # Calculate fit score percentage
        for job in saved_jobs_list:
            if job.get('similarity_score'):
                job['fit_percentage'] = round(job['similarity_score'] * 100, 1)
            else:
                job['fit_percentage'] = 0
    
    except Error as e:
        flash(f'Error fetching saved jobs: {str(e)}', 'danger')
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return render_template('saved_jobs.html', saved_jobs=saved_jobs_list)


@app.route('/unsave_job/<job_id>', methods=['POST'])
@login_required
def unsave_job(job_id):
    """Remove a job from saved jobs"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('saved_jobs'))
    
    user_id = session['user_id']
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM saved_jobs WHERE user_id = %s AND job_id = %s",
            (user_id, job_id)
        )
        connection.commit()
        flash('Job removed from saved jobs.', 'success')
    
    except Error as e:
        flash(f'Error removing job: {str(e)}', 'danger')
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return redirect(url_for('saved_jobs'))


@app.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    """Delete user account and all associated data"""
    user_id = session['user_id']
    connection = get_db_connection()
    
    if not connection:
        flash('Database connection error.', 'danger')
        return redirect(url_for('profile'))
    
    try:
        cursor = connection.cursor()
        
        # Delete user (cascade will delete related records)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        
        session.clear()
        flash('Your account has been deleted successfully.', 'info')
        return redirect(url_for('login'))
    
    except Error as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
        connection.rollback()
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return redirect(url_for('profile'))


@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    # Get all cached jobs for analytics
    jobs = get_cached_jobs(limit=200)
    
    print(f"DEBUG: Found {len(jobs)} jobs for analytics")
    
    # Prepare chart data
    chart_data = prepare_chart_data(jobs)
    
    print(f"DEBUG: Chart data keys: {chart_data.keys()}")
    if 'skill_demand' in chart_data:
        print(f"DEBUG: Skills found: {list(chart_data['skill_demand'].keys())[:5]}")
    
    return render_template('analytics.html', chart_data=chart_data, jobs_count=len(jobs))


@app.route('/ats_score')
@login_required
def ats_score():
    """ATS Score analysis page"""
    user_id = session.get('user_id')
    
    # Get user profile
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('dashboard'))
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user profile
        cursor.execute("""
            SELECT education, skills, experience, location 
            FROM profiles 
            WHERE user_id = %s
        """, (user_id,))
        profile = cursor.fetchone()
        
        if not profile or not profile.get('skills'):
            flash('Please complete your profile first to get ATS score', 'warning')
            return redirect(url_for('resume'))
        
        # Get cached jobs (limit to recent 50 for performance)
        cursor.execute("""
            SELECT job_id, title, company, description, location, 
                   salary_min, salary_max, category, url
            FROM jobs
            ORDER BY cached_at DESC
            LIMIT 50
        """)
        jobs = cursor.fetchall()
        
        if not jobs:
            flash('No jobs available for ATS analysis. Please search for jobs first.', 'info')
            return redirect(url_for('find_jobs'))
        
        # Calculate ATS scores for all jobs
        ats_results = []
        for job in jobs:
            score_data = calculate_ats_score(profile, job)
            score_data['job_id'] = job['job_id']
            score_data['url'] = job.get('url', '#')
            score_data['salary_min'] = job.get('salary_min', 0)
            score_data['salary_max'] = job.get('salary_max', 0)
            score_data['location'] = job.get('location', 'Not specified')
            ats_results.append(score_data)
        
        # Sort by overall score (highest first)
        ats_results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Get top 10 for detailed display
        top_matches = ats_results[:10]
        
        # Calculate summary statistics
        scores = [r['overall_score'] for r in ats_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        # Count by score range
        excellent_count = len([s for s in scores if s >= 80])
        good_count = len([s for s in scores if 60 <= s < 80])
        fair_count = len([s for s in scores if 40 <= s < 60])
        poor_count = len([s for s in scores if s < 40])
        
        summary = {
            'average': round(avg_score, 1),
            'highest': round(max_score, 1),
            'lowest': round(min_score, 1),
            'total_jobs': len(ats_results),
            'excellent_count': excellent_count,
            'good_count': good_count,
            'fair_count': fair_count,
            'poor_count': poor_count
        }
        
        return render_template('ats_score.html', 
                             matches=top_matches, 
                             summary=summary,
                             profile=profile)
    
    except Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving ATS scores', 'error')
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    # Check database connection on startup
    conn = get_db_connection()
    if conn:
        print("✓ Database connection successful")
        conn.close()
    else:
        print("✗ Database connection failed. Please check your MySQL configuration.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

