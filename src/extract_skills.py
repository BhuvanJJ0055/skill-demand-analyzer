import os
import sys
import re
import pandas as pd
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))

if script_dir not in sys.path:
    sys.path.append(script_dir)

csv_path = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_cleaned.csv"))
clean_df = pd.read_csv(csv_path)

from skills_taxonomy import SKILLS_TAXONOMY

def extract_skills(description, skills_list):
    if not isinstance(description, str):
        return []
    description_lower = description.lower()
    found_skills = []
    for skill in skills_list:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, description_lower):
            found_skills.append(skill)
    return found_skills

def categorize_role(title):
    title_lower = title.lower()
    if 'data scientist' in title_lower:
        return 'Data Scientist'
    elif 'data analyst' in title_lower:
        return 'Data Analyst'
    return 'Other'

if __name__ == '__main__':
    clean_df['extracted_skills'] = clean_df['description'].apply(
        lambda x: extract_skills(x, SKILLS_TAXONOMY)
    )
    clean_df['num_skills_found'] = clean_df['extracted_skills'].apply(len)
    clean_df['role_category'] = clean_df['title'].apply(categorize_role)
    
    print(clean_df['num_skills_found'].describe())

    print(clean_df[['title', 'extracted_skills']].head(10))

    output_path = os.path.normpath(os.path.join(script_dir, "../data/processed/da_ds_with_skills.csv"))
    clean_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

    zero_skill_rows = clean_df[clean_df['num_skills_found'] == 0]
    print(f"Rows with 0 skills found: {len(zero_skill_rows)}")
    print(zero_skill_rows[['title', 'description']])
    
    # Look at full descriptions for a few zero-skill rows
    sample_indices = [idx for idx in [64, 124, 261] if idx in zero_skill_rows.index]
    if not sample_indices:
        sample_indices = list(zero_skill_rows.index[:3])
        
    for idx in sample_indices:
        print(f"\n{'='*60}")
        print(f"Title: {clean_df.loc[idx, 'title']}")
        print(clean_df.loc[idx, 'description'])

    # How many descriptions end with "Show more" (indicating truncation)?
    truncated = clean_df[clean_df['description'].str.strip().str.endswith('Show more')]
    print(f"Descriptions ending in 'Show more': {len(truncated)} out of {len(clean_df)}")
    print(f"Percentage: {len(truncated)/len(clean_df)*100:.1f}%")

    # Cross-check: what % of the 0-skill rows specifically end this way?
    zero_truncated = zero_skill_rows[zero_skill_rows['description'].str.strip().str.endswith('Show more')]
    print(f"\nOf the {len(zero_skill_rows)} zero-skill rows, {len(zero_truncated)} end with 'Show more'")

    # Flatten all extracted skills into one big list, then count frequency
    all_skills = [skill for skills_list in clean_df['extracted_skills'] for skill in skills_list]
    skill_counts = Counter(all_skills)
    
    print("\n=== TOP 20 SKILLS OVERALL ===")
    for skill, count in skill_counts.most_common(20):
        pct = (count / len(clean_df)) * 100
        print(f"{skill:20s} {count:4d} postings  ({pct:.1f}%)")
    
    # Break down by role: Data Analyst vs Data Scientist
    print("\n=== TOP 10 SKILLS — DATA ANALYST ROLES ===")
    da_skills = [skill for skills_list in clean_df[clean_df['role_category']=='Data Analyst']['extracted_skills'] for skill in skills_list]
    da_counts = Counter(da_skills)
    for skill, count in da_counts.most_common(10):
        print(f"{skill:20s} {count:4d}")
    
    print("\n=== TOP 10 SKILLS — DATA SCIENTIST ROLES ===")
    ds_skills = [skill for skills_list in clean_df[clean_df['role_category']=='Data Scientist']['extracted_skills'] for skill in skills_list]
    ds_counts = Counter(ds_skills)
    for skill, count in ds_counts.most_common(10):
        print(f"{skill:20s} {count:4d}")

    # --- Chart 5: DA vs DS skill comparison ---
    import matplotlib.pyplot as plt

    top_da = dict(da_counts.most_common(8))
    top_ds = dict(ds_counts.most_common(8))

    all_top_skills = list(set(list(top_da.keys()) + list(top_ds.keys())))
    # Sort skills by total frequency (descending) to make the chart easier to scan
    all_top_skills.sort(key=lambda s: da_counts.get(s, 0) + ds_counts.get(s, 0), reverse=True)
    
    # Retrieve actual counts from full counters instead of top 8 dicts to avoid misleading 0s
    da_vals = [da_counts.get(s, 0) for s in all_top_skills]
    ds_vals = [ds_counts.get(s, 0) for s in all_top_skills]

    x = range(len(all_top_skills))
    plt.figure(figsize=(12, 6))
    plt.bar([i - 0.2 for i in x], da_vals, width=0.4, label='Data Analyst', color='#4C72B0')
    plt.bar([i + 0.2 for i in x], ds_vals, width=0.4, label='Data Scientist', color='#DD8452')
    plt.xticks(x, all_top_skills, rotation=45, ha='right')
    plt.ylabel('Number of Postings')
    plt.title('Top Skills: Data Analyst vs Data Scientist')
    plt.legend()
    
    # Add caption explaining the data representation and resolving the "0" bars nuance
    plt.figtext(0.5, -0.05, 
                "Note: Includes the union of the top 8 skills from each role. True counts are shown for both roles, even if the skill wasn't in that role's own top 8.",
                ha='center', fontsize=8, style='italic', wrap=True)
    
    plt.tight_layout()

    chart_path = os.path.normpath(os.path.join(script_dir, "../notebooks/chart5_skill_comparison.png"))
    plt.savefig(chart_path, bbox_inches='tight')
    print(f"\nChart saved to {chart_path}")
    plt.show()
