import streamlit as st
import pandas as pd
from collections import Counter
import sys
import os
import ast

# Add src folder to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.normpath(os.path.join(script_dir, '..', 'src'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from src.recommend import recommend_skills, skill_gap_summary
    from src.learning_resources import get_skill_learning_info, filter_fresher_jobs
except ImportError:
    from recommend import recommend_skills, skill_gap_summary  # type: ignore
    from learning_resources import get_skill_learning_info, filter_fresher_jobs  # type: ignore

st.set_page_config(
    page_title="Skill Demand Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .resource-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 16px;
    }
    .job-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out;
    }
    .job-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }
    .job-meta {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 8px;
    }
    .fresher-badge {
        background-color: #DCFCE7;
        color: #15803D;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .skill-tag {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4338CA;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 4px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    live_path = os.path.normpath(os.path.join(script_dir, '..', 'data', 'processed', 'latest_jobs_with_skills.csv'))
    historical_path = os.path.normpath(os.path.join(script_dir, '..', 'data', 'processed', 'da_ds_with_skills.csv'))
    
    is_live = False
    if os.path.exists(live_path):
        df = pd.read_csv(live_path)
        is_live = True
    elif os.path.exists(historical_path):
        df = pd.read_csv(historical_path)
    else:
        st.error("No dataset found. Please run src/extract_skills.py or src/fetch_jobs.py.")
        st.stop()

    def parse_skills(val):
        if isinstance(val, list):
            return val
        if not isinstance(val, str) or pd.isna(val):
            return []
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []

    df['extracted_skills'] = df['extracted_skills'].apply(parse_skills)
    return df, is_live

df, is_live_data = load_data()

# Compute available roles and skill counters
all_roles = [r for r in df['role_category'].unique() if pd.notna(r) and r != 'Other']
if not all_roles:
    all_roles = ['Data Analyst', 'Data Scientist']

preferred_order = [
    'Data Analyst', 'Data Scientist', 'Data Engineer', 
    'Machine Learning Engineer', 'Business Intelligence Analyst'
]
sorted_roles = [r for r in preferred_order if r in all_roles] + [r for r in all_roles if r not in preferred_order]

role_counters = {}
for role in sorted_roles:
    role_skills = [
        s for skills in df[df['role_category'] == role]['extracted_skills'] for s in skills
    ]
    role_counters[role] = Counter(role_skills)

all_available_skills = sorted(list({s for c in role_counters.values() for s in c.keys()}))

# --- SIDEBAR ---
with st.sidebar:
    st.header("📈 Market Dataset")
    if is_live_data:
        st.success("🟢 Active: Live Real-World Postings")
    else:
        st.info("🟡 Active: Baseline Dataset")

    st.markdown(f"**Total Postings Analyzed:** `{len(df):,}`")
    
    if 'date_posted' in df.columns:
        dates = pd.to_datetime(df['date_posted'], errors='coerce').dropna()
        if not dates.empty:
            st.markdown(f"**Date Range:** {dates.min().strftime('%b %Y')} – {dates.max().strftime('%b %Y')}")

    if 'source' in df.columns:
        sources = df['source'].dropna().unique().tolist()
        st.markdown(f"**Job Boards:** {', '.join(str(s).title() for s in sources)}")
    
    st.markdown("---")
    st.subheader("Available Roles in Data")
    for r in sorted_roles:
        count = len(df[df['role_category'] == r])
        st.markdown(f"- **{r}:** {count} jobs")

    st.markdown("---")
    st.markdown("""
    💡 **Need fresh market data?**
    Run the batch scraper from your terminal:
    ```bash
    python src/fetch_jobs.py --results-wanted 25 --location "India"
    ```
    """)

# --- MAIN CONTENT ---
st.markdown('<div class="main-header">📊 Skill Demand Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover in-demand skills across top Data & AI roles, '
    'get customized learning resources (YouTube & Official Docs), and explore entry-level / fresher job postings.</div>',
    unsafe_allow_html=True
)

col_input1, col_input2 = st.columns([1, 2])

with col_input1:
    role_choice = st.selectbox(
        "🎯 Select your target role:",
        options=sorted_roles,
        index=0
    )

with col_input2:
    user_skills = st.multiselect(
        "🛠️ Skills you already know:",
        options=all_available_skills,
        placeholder="Type or select skills (e.g. Python, SQL, Tableau)..."
    )

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("🚀 Analyze Skill Match & Learning Path", type="primary", use_container_width=True)

if run_btn:
    role_count_total = len(df[df['role_category'] == role_choice])
    relevant_counts = role_counters.get(role_choice, Counter())
    
    if role_count_total == 0 or not relevant_counts:
        st.warning(f"No postings found for {role_choice} in the current dataset.")
    else:
        gap_info = skill_gap_summary(user_skills, role_choice, role_counters, top_n=8)
        missing_recommendations = recommend_skills(user_skills, role_choice, role_counters, top_n=5)
        
        st.markdown("---")
        st.subheader(f"Results for: **{role_choice}**")

        # Metric row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                label="Benchmark Match Rate",
                value=f"{gap_info['match_percentage']:.0f}%",
                help="Percentage of the top 8 market skills for this role that you currently possess."
            )
        with m2:
            st.metric(
                label="Top Skills Matched",
                value=f"{len(gap_info['matched_skills'])} / {gap_info['total_top_skills']}"
            )
        with m3:
            st.metric(
                label="Market Sample Size",
                value=f"{role_count_total} Postings"
            )

        col_left, col_right = st.columns([1.3, 1])

        with col_left:
            st.markdown("### 🎯 Recommended Skills to Learn Next")
            if missing_recommendations:
                for skill, count in missing_recommendations:
                    pct = (count / role_count_total) * 100
                    learn_info = get_skill_learning_info(skill)

                    st.markdown(f"#### 🔹 **{skill}** — *in {pct:.1f}% of {role_choice} postings ({count} jobs)*")
                    st.progress(min(pct / 100.0, 1.0))

                    # Learning Resources Expandable Card
                    with st.expander(f"📚 Best YouTube Channels & Official Docs for **{skill}**"):
                        st.markdown(f"💡 **Study Tip:** {learn_info['tip']}")
                        
                        # Official Website
                        st.markdown(f"🌐 **Official Documentation:** [{learn_info['official_name']}]({learn_info['official']})")
                        
                        # Recommended YouTube channels
                        yt_links = [f"[{yt['name']}]({yt['channel']})" for yt in learn_info['youtube']]
                        st.markdown(f"📺 **Top YouTube Channels:** {', '.join(yt_links)}")
                        
                        # Direct YouTube search
                        st.markdown(f"🔍 [Search beginner courses for {skill} on YouTube]({learn_info['youtube_search_url']})")
                    
                    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
            else:
                st.success("🎉 Outstanding! You already have all top skills in demand for this role!")

        with col_right:
            st.markdown("### 📋 Top 10 In-Demand Skills")
            top10 = relevant_counts.most_common(10)
            user_skills_lower = {s.lower() for s in user_skills}
            
            for skill, count in top10:
                pct = (count / role_count_total) * 100
                status = "✅" if skill.lower() in user_skills_lower else "⏳"
                st.markdown(f"{status} **{skill}** — `{pct:.0f}%` of jobs ({count})")

        # --- SECTION: Fresher & Entry-Level Job Opportunities ---
        st.markdown("---")
        st.subheader(f"🎓 Entry-Level & Fresher Opportunities for **{role_choice}**")
        st.markdown("Real-world postings from the dataset suitable for freshers, juniors, and early-career candidates:")

        fresher_jobs = filter_fresher_jobs(df, role_choice, top_n=6)

        if fresher_jobs:
            f_cols = st.columns(2)
            for idx, job in enumerate(fresher_jobs):
                with f_cols[idx % 2]:
                    with st.container():
                        st.markdown(f"""
                        <div class="job-card">
                            <div class="fresher-badge">🌱 {job['reason']}</div>
                            <div class="job-title">{job['title']}</div>
                            <div class="job-meta">🏢 <strong>{job['company']}</strong> &nbsp;|&nbsp; 📍 {job['location']} &nbsp;|&nbsp; 🏷️ {job['source']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Skills tags
                        if job['skills'] and isinstance(job['skills'], list):
                            skills_html = "".join([f"<span class='skill-tag'>{s}</span>" for s in job['skills'][:6]])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        
                        # Direct apply / view link
                        if job['link']:
                            st.link_button(
                                f"🔗 View / Apply on {job['source']}",
                                url=job['link'],
                                use_container_width=True
                            )
                        else:
                            st.caption("Job link unavailable in dataset.")
                        st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info(f"No specific entry-level postings detected in the current dataset for {role_choice}.")

st.markdown("---")
with st.expander("ℹ️ About this platform & data pipeline"):
    st.markdown(f"""
    - **Data Pipeline:** Pulls real-world job postings across LinkedIn, Indeed, Glassdoor, and ZipRecruiter using automated batch ingestion.
    - **Skill Taxonomy:** Enriched via an NLP skill extractor tracking over 65 industry skills spanning SQL, Python, Cloud (AWS, Azure, GCP), Big Data (Spark, Kafka, dbt, Airflow), and AI/ML (PyTorch, LLMs, MLOps).
    - **Fresher Filter:** Identifies entry-level, junior, associate, and 0-2 year experience job postings with direct links.
    - **Current Dataset:** {'Live scraped postings' if is_live_data else 'Baseline dataset'}.
    """)