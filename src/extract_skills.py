import os
import sys
import re
import pandas as pd
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    from src.skills_taxonomy import SKILLS_TAXONOMY
except ImportError:
    from skills_taxonomy import SKILLS_TAXONOMY  # type: ignore


def build_skill_patterns(skills_list):
    """
    Builds robust compiled regex patterns for skills, handling special characters
    like 'C++', 'A/B testing', and 'CI/CD' which standard \b word boundaries mishandle.
    """
    patterns = {}
    for skill in skills_list:
        escaped = re.escape(skill.lower())
        # Custom boundaries handling punctuation/whitespace
        pattern_str = r'(?:^|[\s,;./()\-[\]{}])' + escaped + r'(?:$|[\s,;./()\-[\]{}])'
        patterns[skill] = re.compile(pattern_str, re.IGNORECASE)
    return patterns

COMPILED_SKILL_PATTERNS = build_skill_patterns(SKILLS_TAXONOMY)

def extract_skills(description, skills_list=None):
    """
    Extracts known skills from job description text.
    """
    if not isinstance(description, str) or not description.strip():
        return []
    
    # Pad string with whitespace to ensure start/end boundaries match cleanly
    text = f" {description.lower()} "
    found_skills = []
    
    patterns = COMPILED_SKILL_PATTERNS if (skills_list is None or skills_list == SKILLS_TAXONOMY) else build_skill_patterns(skills_list)
    
    for skill, pattern in patterns.items():
        if pattern.search(text):
            found_skills.append(skill)
            
    return found_skills

def categorize_role(title):
    """
    Categorizes job title into primary data & AI role families.
    """
    if not isinstance(title, str):
        return 'Other'
        
    title_lower = title.lower()
    
    # Check for ML / AI Engineer first
    if any(kw in title_lower for kw in [
        'machine learning', 'ml engineer', 'mlops', 'ai engineer', 
        'artificial intelligence engineer', 'deep learning'
    ]):
        return 'Machine Learning Engineer'
        
    # Check for Data Engineer
    elif any(kw in title_lower for kw in [
        'data engineer', 'analytics engineer', 'big data engineer', 
        'etl engineer', 'data platform engineer', 'database engineer'
    ]):
        return 'Data Engineer'
        
    # Check for Business Intelligence
    elif any(kw in title_lower for kw in [
        'business intelligence', 'bi analyst', 'bi developer', 
        'power bi developer', 'tableau developer', 'bi lead', 'reporting analyst'
    ]):
        return 'Business Intelligence Analyst'
        
    # Check for Data Scientist
    elif any(kw in title_lower for kw in [
        'data scientist', 'applied scientist', 'research scientist', 
        'decision scientist', 'data science'
    ]):
        return 'Data Scientist'
        
    # Check for Data Analyst
    elif any(kw in title_lower for kw in [
        'data analyst', 'analytics analyst', 'product analyst', 
        'business data analyst', 'quantitative analyst', 'marketing analyst'
    ]):
        return 'Data Analyst'
        
    return 'Other'

def enrich_dataframe(df, skills_list=SKILLS_TAXONOMY):
    """
    Takes a dataframe containing 'title' and 'description' columns,
    extracts skills, calculates counts, and assigns role categories.
    """
    df = df.copy()
    if 'description' not in df.columns:
        raise ValueError("DataFrame must contain a 'description' column")
    if 'title' not in df.columns:
        raise ValueError("DataFrame must contain a 'title' column")

    print(f"Extracting skills for {len(df)} postings...")
    df['extracted_skills'] = df['description'].apply(lambda x: extract_skills(x, skills_list))
    df['num_skills_found'] = df['extracted_skills'].apply(len)
    df['role_category'] = df['title'].apply(categorize_role)
    return df

if __name__ == '__main__':
    # Determine which file to process: prefer latest live jobs if present, else fallback
    live_raw_path = os.path.normpath(os.path.join(script_dir, "../data/raw/live_jobs_raw.csv"))
    cleaned_csv_path = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_cleaned.csv"))
    
    if os.path.exists(live_raw_path):
        input_path = live_raw_path
        output_path = os.path.normpath(os.path.join(script_dir, "../data/processed/latest_jobs_with_skills.csv"))
        print(f"Processing live dataset from {input_path}")
    elif os.path.exists(cleaned_csv_path):
        input_path = cleaned_csv_path
        output_path = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_with_skills.csv"))
        print(f"Processing historical dataset from {input_path}")
    else:
        print("No input dataset found in data/raw or data/processed.")
        sys.exit(1)

    df = pd.read_csv(input_path)
    enriched_df = enrich_dataframe(df, SKILLS_TAXONOMY)
    
    enriched_df.to_csv(output_path, index=False)
    print(f"\nSaved enriched data with skills to {output_path}")
    
    print("\nRole distribution:")
    print(enriched_df['role_category'].value_counts())
    
    print("\nSummary of skills found per posting:")
    print(enriched_df['num_skills_found'].describe())
