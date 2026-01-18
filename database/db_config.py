"""
Database configuration module for MySQL connection
"""
import os

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': '',  # Change to your MySQL password
    'database': 'job_finder_db'  # Database name
}

# Alternatively, use environment variables
DB_CONFIG_ENV = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'job_finder_db')
}

