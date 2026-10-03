import os
import sys
import ast
import pandas as pd
from collections import Counter

def get_relevant_counts(role_category, role_counts_or_da, ds_counts=None):
    """
    Helper to resolve Counter for role_category whether passed as dict of Counters
    or as separate da_counts, ds_counts arguments.
    """
    if isinstance(role_counts_or_da, dict):
        if role_category in role_counts_or_da:
            return role_counts_or_da[role_category]
        # fallback to empty Counter if not found
        return Counter()
    elif isinstance(role_counts_or_da, Counter) and ds_counts is None:
        return role_counts_or_da
    else:
        # Legacy positional arguments: da_counts, ds_counts
        if role_category == 'Data Analyst':
            return role_counts_or_da
        elif role_category == 'Data Scientist':
            return ds_counts if ds_counts is not None else Counter()
        else:
            return Counter()

def recommend_skills(user_skills, role_category, role_counts_or_da, ds_counts=None, top_n=5):
    """
    Given a user's current skills and target role, recommend the top skills 
    they're missing, ranked by market demand.
    
    user_skills: list of skills the user already has (case-insensitive)
    role_category: target role name (e.g. 'Data Analyst', 'Data Scientist', 'Data Engineer', etc.)
    role_counts_or_da: dict of {role_name: Counter} OR da_counts Counter (legacy)
    """
    user_skills_lower = set(s.lower() for s in user_skills)
    relevant_counts = get_relevant_counts(role_category, role_counts_or_da, ds_counts)
    
    # Rank all skills for this role by demand, excluding what the user already knows
    ranked_skills = relevant_counts.most_common()
    missing_skills = [(skill, count) for skill, count in ranked_skills 
                       if skill.lower() not in user_skills_lower]
    
    return missing_skills[:top_n]

def skill_gap_summary(user_skills, role_category, role_counts_or_da, ds_counts=None, top_n=8):
    """
    Returns a summary of how many of the role's top N skills the user already has.
    """
    user_skills_lower = set(s.lower() for s in user_skills)
    relevant_counts = get_relevant_counts(role_category, role_counts_or_da, ds_counts)
    
    top_skills = [skill for skill, count in relevant_counts.most_common(top_n)]
    matched = [s for s in top_skills if s.lower() in user_skills_lower]
    missing = [s for s in top_skills if s.lower() not in user_skills_lower]
    
    total = len(top_skills) if top_skills else top_n
    match_pct = (len(matched) / total * 100) if total > 0 else 0
    
    return {
        'matched_skills': matched,
        'missing_skills': missing,
        'match_percentage': match_pct,
        'total_top_skills': total
    }

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for live data first, then historical
    live_csv = os.path.normpath(os.path.join(script_dir, "../data/processed/latest_jobs_with_skills.csv"))
    historical_csv = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_with_skills.csv"))
    
    csv_path = live_csv if os.path.exists(live_csv) else historical_csv
    
    if not os.path.exists(csv_path):
        print(f"Enriched dataset not found at {csv_path}. Please run extract_skills.py or fetch_jobs.py first.")
        sys.exit(1)
        
    print(f"Loading dataset from: {csv_path}")
    clean_df = pd.read_csv(csv_path)
    
    def parse_skills(val):
        if not isinstance(val, str) or pd.isna(val):
            return []
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
            
    clean_df['extracted_skills'] = clean_df['extracted_skills'].apply(parse_skills)
    
    # Calculate role counts dynamically for all roles
    role_counters = {}
    for role in clean_df['role_category'].unique():
        if pd.isna(role) or role == 'Other':
            continue
        role_skills = [
            skill for skills_list in clean_df[clean_df['role_category'] == role]['extracted_skills']
            for skill in skills_list
        ]
        role_counters[role] = Counter(role_skills)
    
    print(f"Active roles available: {list(role_counters.keys())}")
    
    # Test for Data Analyst
    test_user_skills = ['Python', 'Excel']
    test_role = 'Data Analyst'
    recommendations = recommend_skills(test_user_skills, test_role, role_counters)
    print(f"\nUser knows: {test_user_skills}")
    print(f"Target role: {test_role}")
    print("Top skills to learn next:")
    for skill, count in recommendations:
        pct = (count / len(clean_df[clean_df['role_category'] == test_role])) * 100
        print(f"  {skill}: appears in {count} postings ({pct:.1f}%)")
