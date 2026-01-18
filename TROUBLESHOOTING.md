# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: PowerShell Command Syntax Error

**Problem:**
```powershell
"C:/path/to/python.exe" -m pip list
# Error: Unexpected token '-m'
```

**Solution:**
Use the `&` call operator in PowerShell:
```powershell
& "C:/path/to/python.exe" -m pip list
```

---

### Issue 2: MySQL Not Installed

**Problem:**
```
mysql: The term 'mysql' is not recognized
```

**Solutions:**

#### Option A: Install MySQL Server
1. Download from: https://dev.mysql.com/downloads/installer/
2. Run MySQL Installer
3. Choose "Developer Default" or "Server Only"
4. Set root password during installation
5. Complete installation

#### Option B: Install XAMPP (Easier)
1. Download from: https://www.apachefriends.org/
2. Install XAMPP
3. Start MySQL from XAMPP Control Panel
4. Default credentials: user=root, password=(empty)

#### Option C: Use SQLite (No installation)
Contact me to convert the project to use SQLite instead of MySQL.

---

### Issue 3: Database Connection Failed

**Problem:**
```
Error connecting to MySQL: Access denied for user 'root'@'localhost'
```

**Solution:**
1. Update `database/db_config.py` with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # ← Update this
    'database': 'job_finder_db'
}
```

2. Create the database:
```powershell
mysql -u root -p < database/schema.sql
```

Or manually in MySQL:
```sql
CREATE DATABASE job_finder_db;
USE job_finder_db;
SOURCE database/schema.sql;
```

---

### Issue 4: Database 'job_finder_db' Does Not Exist

**Problem:**
```
Unknown database 'job_finder_db'
```

**Solution:**
Run the schema file to create it:
```powershell
mysql -u root -p < database\schema.sql
```

Or in MySQL Workbench:
1. Open MySQL Workbench
2. Connect to your server
3. File → Run SQL Script
4. Select `database/schema.sql`
5. Execute

---

### Issue 5: spaCy Model Not Found

**Problem:**
```
Warning: spaCy model not found
```

**Solution (Optional):**
The app works without spaCy (you're on Python 3.13). To install:
```powershell
& "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" -m pip install spacy==3.7.2
& "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" -m spacy download en_core_web_sm
```

---

## How to Run the Application

### Method 1: Using PowerShell Script
```powershell
.\run.ps1
```

### Method 2: Direct Command
```powershell
& "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" app.py
```

### Method 3: Activate Virtual Environment First
```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

---

## Quick MySQL Setup Commands

### Create Database
```sql
CREATE DATABASE IF NOT EXISTS job_finder_db;
USE job_finder_db;
```

### Import Schema
```powershell
# If MySQL is in PATH:
mysql -u root -p < database\schema.sql

# Or use full path:
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database\schema.sql
```

### Test Connection
```powershell
& "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='YOUR_PASSWORD'); print('✓ Connected'); conn.close()"
```

---

## Checking MySQL Service

```powershell
# Check if MySQL service is running
Get-Service -Name "MySQL*"

# Start MySQL service (if stopped)
Start-Service -Name "MySQL80"  # Adjust name based on your version
```

---

## Environment Variables Alternative

Instead of hardcoding credentials, use environment variables:

```powershell
# Set environment variables
$env:DB_PASSWORD = "your_password"
$env:DB_USER = "root"
$env:DB_HOST = "localhost"

# Then run the app
& "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" app.py
```

---

## Still Having Issues?

1. **Check MySQL is running:**
   - Open Task Manager → Services
   - Look for "MySQL80" or similar
   - Status should be "Running"

2. **Verify port 5000 is free:**
   ```powershell
   netstat -ano | findstr :5000
   ```

3. **Check Python version:**
   ```powershell
   & "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" --version
   ```
   Should be Python 3.8+

4. **Reinstall dependencies:**
   ```powershell
   & "C:/Users/GLOBAL TECHNOLOGY/Desktop/DM Project/.venv/Scripts/python.exe" -m pip install -r requirements.txt
   ```
