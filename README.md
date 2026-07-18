# Skill-Demand Analyzer

Analyzes real job postings to identify in-demand Data Analyst & Data Scientist skills and recommends a personalized learning path based on skill gaps. Built with Python, SQL, NLP, and deployed as a live app via Streamlit.

**Live demo:** https://skill-demand-analyzer.streamlit.app/
**Tech stack:** Python · SQL · NLP (regex-based skill extraction) · Streamlit · Pandas

## What it does
- Analyzes 453 real Data Analyst/Data Scientist job postings (LinkedIn, Apr-Jun 2025)
- Extracts required skills from job descriptions using a curated 51-skill taxonomy
- Recommends personalized "skills to learn next" based on your current skillset and target role
- Shows a skill-match percentage against the top 8 in-demand skills for that role

## Why this dataset
I compared four datasets and picked this one because it was already focused on Data Analyst/Scientist roles, recent (mid-2025), came from real companies, and was the right size to iterate quickly — versus alternatives that were either too broad, too old, too small after filtering, or partially synthetic.

## Limitations
- Snapshot data (Apr-Jun 2025) — doesn't reflect real-time market changes
- Skill extraction uses keyword matching; may miss unusually-phrased skill mentions
- ~90% of postings contain a "Show more" marker suggesting possible truncation; 8/453 postings returned no detected skills
