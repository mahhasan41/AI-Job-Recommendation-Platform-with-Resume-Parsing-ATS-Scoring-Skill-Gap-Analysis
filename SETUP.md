# Quick Setup Guide

Follow these steps to get the AI Job Finder application running:

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Download spaCy Language Model (Optional)

**Note**: spaCy may not be compatible with Python 3.13. The application works without it, but some advanced NLP features are limited.

If using Python 3.12 or lower:

```bash
pip install spacy==3.7.2
python -m spacy download en_core_web_sm
```

## Step 3: Set Up MySQL Database

1. **Start MySQL Server** (if not already running)

2. **Create Database and Tables**:
   - Open MySQL command line or MySQL Workbench
   - Run the SQL script:
     ```bash
     mysql -u root -p < database/schema.sql
     ```
   - Or manually copy and execute the contents of `database/schema.sql`

3. **Configure Database Connection**:
   - Edit `database/db_config.py`
   - Update with your MySQL credentials:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'your_username',
         'password': 'your_password',
         'database': 'job_finder_db'
     }
     ```

## Step 4: Run the Application

```bash
python app.py
```

## Step 5: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## First Time Usage

1. **Register** a new account
2. **Upload your resume** (PDF or DOCX) OR manually enter your profile
3. **Search for jobs** using keywords and location
4. **View AI recommendations** ranked by relevance
5. **Explore analytics** for market insights

## Troubleshooting

### "Database connection error"
- Verify MySQL server is running
- Check credentials in `database/db_config.py`
- Ensure database `job_finder_db` exists

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

---

**Note**: The Adzuna API credentials are already configured. Make sure you have an active internet connection for job fetching.

