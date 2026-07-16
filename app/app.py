import streamlit as st
import pandas as pd
from collections import Counter
import sys
import os

# Add src folder to path so we can import our functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

st.set_page_config(page_title="Skill Demand Analyzer", page_icon="📊", layout="centered")

st.title("📊 Skill Demand Analyzer")
st.markdown("Find out what skills you need to learn next for a Data Analyst or Data Scientist role — based on real job posting data.")

# Load the enriched dataset (with extracted skills)
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'da_ds_with_skills.csv'))
    return df

df = load_data()

# Rebuild role categorization and skill counters
def categorize_role(title):
    title_lower = str(title).lower()
    if 'data scientist' in title_lower:
        return 'Data Scientist'
    elif 'data analyst' in title_lower:
        return 'Data Analyst'
    return 'Other'

df['role_category'] = df['title'].apply(categorize_role)

# extracted_skills is stored as a string representation of a list after CSV save/load — need to parse it back
import ast
df['extracted_skills'] = df['extracted_skills'].apply(ast.literal_eval)

da_skills = [s for skills in df[df['role_category']=='Data Analyst']['extracted_skills'] for s in skills]
ds_skills = [s for skills in df[df['role_category']=='Data Scientist']['extracted_skills'] for s in skills]
da_counts = Counter(da_skills)
ds_counts = Counter(ds_skills)

# --- User Interface ---
st.subheader("Tell us about yourself")

role_choice = st.selectbox("Target role", ["Data Analyst", "Data Scientist"])

all_skills = sorted(set(list(da_counts.keys()) + list(ds_counts.keys())))
user_skills = st.multiselect("Skills you already know", options=all_skills)

if st.button("Get Recommendations"):
    relevant_counts = da_counts if role_choice == "Data Analyst" else ds_counts
    user_skills_lower = set(s.lower() for s in user_skills)
    
    ranked = relevant_counts.most_common()
    missing = [(s, c) for s, c in ranked if s.lower() not in user_skills_lower][:5]
    
    top8 = [s for s, c in relevant_counts.most_common(8)]
    matched = [s for s in top8 if s.lower() in user_skills_lower]
    match_pct = (len(matched) / 8) * 100

    st.subheader("Your Results")
    st.metric("Skill Match", f"{match_pct:.0f}%", f"{len(matched)}/8 top skills")

    st.write("### Top skills to learn next:")
    for skill, count in missing:
        pct = (count / len(df[df['role_category']==role_choice])) * 100
        st.write(f"- **{skill}** — appears in {pct:.0f}% of {role_choice} postings")

st.markdown("---")
st.caption(f"Based on {len(df)} real job postings (Apr-Jun 2025, LinkedIn). Data may not reflect current market conditions.")