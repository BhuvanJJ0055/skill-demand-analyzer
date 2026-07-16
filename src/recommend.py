import os
import sys
import ast
import pandas as pd
from collections import Counter

def recommend_skills(user_skills, role_category, da_counts, ds_counts, top_n=5):
    """
    Given a user's current skills and target role, recommend the top skills 
    they're missing, ranked by market demand.
    
    user_skills: list of skills the user already has (case-insensitive)
    role_category: 'Data Analyst' or 'Data Scientist'
    da_counts, ds_counts: Counter objects with skill frequencies for each role
    """
    user_skills_lower = set(s.lower() for s in user_skills)
    
    if role_category == 'Data Analyst':
        relevant_counts = da_counts
    elif role_category == 'Data Scientist':
        relevant_counts = ds_counts
    else:
        raise ValueError("role_category must be 'Data Analyst' or 'Data Scientist'")
    
    # Rank all skills for this role by demand, excluding what the user already knows
    ranked_skills = relevant_counts.most_common()
    missing_skills = [(skill, count) for skill, count in ranked_skills 
                       if skill.lower() not in user_skills_lower]
    
    return missing_skills[:top_n]


if __name__ == '__main__':
    # Locate files relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_with_skills.csv"))
    
    if not os.path.exists(csv_path):
        print(f"Enriched dataset not found at {csv_path}. Please run extract_skills.py first.")
        sys.exit(1)
        
    clean_df = pd.read_csv(csv_path)
    
    # Parse the string lists in extracted_skills back to real lists
    def parse_skills(val):
        if not isinstance(val, str) or pd.isna(val):
            return []
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
            
    clean_df['extracted_skills'] = clean_df['extracted_skills'].apply(parse_skills)
    
    # Re-calculate counts
    da_skills = [skill for skills_list in clean_df[clean_df['role_category']=='Data Analyst']['extracted_skills'] for skill in skills_list]
    da_counts = Counter(da_skills)
    
    ds_skills = [skill for skills_list in clean_df[clean_df['role_category']=='Data Scientist']['extracted_skills'] for skill in skills_list]
    ds_counts = Counter(ds_skills)
    
    # Test 1: Data Analyst
    test_user_skills = ['Python', 'Excel']
    test_role = 'Data Analyst'
    recommendations = recommend_skills(test_user_skills, test_role, da_counts, ds_counts)
    print(f"User knows: {test_user_skills}")
    print(f"Target role: {test_role}")
    print(f"\nTop skills to learn next:")
    for skill, count in recommendations:
        pct = (count / len(clean_df)) * 100
        print(f"  {skill}: appears in {count} postings ({pct:.1f}%)")

    # Test 2: Data Scientist
    print("\n" + "="*50)
    test_user_skills_2 = ['Python', 'SQL']
    test_role_2 = 'Data Scientist'
    recommendations_2 = recommend_skills(test_user_skills_2, test_role_2, da_counts, ds_counts)
    print(f"User knows: {test_user_skills_2}")
    print(f"Target role: {test_role_2}")
    print(f"\nTop skills to learn next:")
    for skill, count in recommendations_2:
        pct = (count / len(clean_df)) * 100
        print(f"  {skill}: appears in {count} postings ({pct:.1f}%)")
