"""
Data Visualization Module
Creates charts and analytics for job market insights
"""
import json
from collections import Counter
import pandas as pd


def analyze_skill_demand(jobs):
    """
    Analyze skill demand from job postings
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        Dictionary with skill frequencies
    """
    skill_keywords = {
        'Python': ['python'],
        'Java': ['java'],
        'JavaScript': ['javascript', 'js'],
        'React': ['react'],
        'SQL': ['sql', 'mysql', 'postgresql'],
        'AWS': ['aws', 'amazon web services'],
        'Docker': ['docker'],
        'Machine Learning': ['machine learning', 'ml', 'tensorflow', 'pytorch'],
        'Data Science': ['data science', 'pandas', 'numpy'],
        'Node.js': ['node', 'nodejs'],
        'Angular': ['angular'],
        'Vue': ['vue'],
        'Django': ['django'],
        'Flask': ['flask'],
        'Spring': ['spring'],
        'MongoDB': ['mongodb'],
        'Git': ['git', 'github'],
        'Kubernetes': ['kubernetes', 'k8s']
    }
    
    skill_counts = {}
    job_descriptions = ' '.join([job.get('description', '').lower() for job in jobs])
    
    for skill_name, keywords in skill_keywords.items():
        count = sum(1 for keyword in keywords if keyword in job_descriptions)
        if count > 0:
            skill_counts[skill_name] = count
    
    return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))


def calculate_salary_statistics(jobs):
    """
    Calculate salary statistics from jobs
    
    Args:
        jobs: List of job dictionaries with salary_min and salary_max
    
    Returns:
        Dictionary with salary statistics
    """
    salaries = []
    for job in jobs:
        if job.get('salary_min') and job.get('salary_min') > 0:
            salaries.append(job['salary_min'])
        if job.get('salary_max') and job.get('salary_max') > 0:
            salaries.append(job['salary_max'])
    
    if not salaries:
        return {
            'average': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }
    
    salaries = [s for s in salaries if s > 0]
    if not salaries:
        return {
            'average': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }
    
    return {
        'average': sum(salaries) / len(salaries),
        'min': min(salaries),
        'max': max(salaries),
        'median': sorted(salaries)[len(salaries) // 2]
    }


def analyze_job_distribution_by_location(jobs):
    """
    Analyze job distribution by location
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        Dictionary with location counts
    """
    locations = {}
    for job in jobs:
        location = job.get('location', 'Unknown')
        if location:
            locations[location] = locations.get(location, 0) + 1
    
    return dict(sorted(locations.items(), key=lambda x: x[1], reverse=True))


def analyze_job_distribution_by_category(jobs):
    """
    Analyze job distribution by category
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        Dictionary with category counts
    """
    categories = {}
    for job in jobs:
        category = job.get('category', 'Unknown')
        if category:
            categories[category] = categories.get(category, 0) + 1
    
    return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))


def prepare_chart_data(jobs, recommendations=None):
    """
    Prepare all chart data for frontend visualization
    
    Args:
        jobs: List of all jobs
        recommendations: List of recommendation results with similarity scores
    
    Returns:
        Dictionary with all chart data in JSON format
    """
    chart_data = {
        'skill_demand': analyze_skill_demand(jobs),
        'salary_stats': calculate_salary_statistics(jobs),
        'location_distribution': analyze_job_distribution_by_location(jobs),
        'category_distribution': analyze_job_distribution_by_category(jobs)
    }
    
    if recommendations:
        # Prepare similarity score distribution
        similarity_scores = [r['similarity_score'] * 100 for r in recommendations]
        chart_data['similarity_scores'] = similarity_scores
    
    return chart_data


def format_chart_data_for_chartjs(chart_data):
    """
    Format data for Chart.js consumption
    
    Args:
        chart_data: Dictionary with chart data
    
    Returns:
        Dictionary formatted for Chart.js
    """
    formatted = {}
    
    # Skill demand bar chart
    if 'skill_demand' in chart_data:
        skills = list(chart_data['skill_demand'].keys())[:10]  # Top 10
        counts = [chart_data['skill_demand'][skill] for skill in skills]
        formatted['skill_demand'] = {
            'labels': skills,
            'datasets': [{
                'label': 'Job Count',
                'data': counts,
                'backgroundColor': 'rgba(54, 162, 235, 0.6)'
            }]
        }
    
    # Location distribution pie chart
    if 'location_distribution' in chart_data:
        locations = list(chart_data['location_distribution'].keys())[:8]  # Top 8
        values = [chart_data['location_distribution'][loc] for loc in locations]
        formatted['location_distribution'] = {
            'labels': locations,
            'datasets': [{
                'label': 'Jobs',
                'data': values,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(199, 199, 199, 0.6)',
                    'rgba(83, 102, 255, 0.6)'
                ]
            }]
        }
    
    # Category distribution
    if 'category_distribution' in chart_data:
        categories = list(chart_data['category_distribution'].keys())[:8]
        values = [chart_data['category_distribution'][cat] for cat in categories]
        formatted['category_distribution'] = {
            'labels': categories,
            'datasets': [{
                'label': 'Jobs',
                'data': values,
                'backgroundColor': 'rgba(75, 192, 192, 0.6)'
            }]
        }
    
    # Similarity scores histogram
    if 'similarity_scores' in chart_data:
        scores = chart_data['similarity_scores']
        formatted['similarity_scores'] = {
            'labels': [f'{i*10}-{(i+1)*10}%' for i in range(10)],
            'datasets': [{
                'label': 'Job Matches',
                'data': scores,
                'backgroundColor': 'rgba(153, 102, 255, 0.6)'
            }]
        }
    
    return formatted

