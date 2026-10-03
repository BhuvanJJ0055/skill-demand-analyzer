# Skill-Demand Analyzer

Analyzes real job postings to identify in-demand skills across Data & AI roles (**Data Analyst**, **Data Scientist**, **Data Engineer**, **Machine Learning Engineer**, and **Business Intelligence Analyst**) and recommends a personalized learning roadmap based on skill gaps. Built with Python, NLP, and deployed as an interactive dashboard via Streamlit.

**Live demo:** https://skill-demand-analyzer.streamlit.app/  
**Tech stack:** Python · NLP Skill Extraction · Streamlit · Pandas · python-jobspy

---

## What it does
- **Multi-Role Coverage:** Analyzes real-world job postings across:
  - 📊 Data Analyst
  - 🔬 Data Scientist
  - 🏗️ Data Engineer
  - 🤖 Machine Learning / AI Engineer
  - 📈 Business Intelligence Analyst
- **Live Ingestion Pipeline:** Uses `python-jobspy` to pull fresh job postings from LinkedIn, Indeed, Glassdoor, and ZipRecruiter with zero API keys required.
- **Skill Extraction:** Extracts in-demand skills from full descriptions using a curated 60+ skill taxonomy spanning programming languages, cloud platforms, BI tools, data warehouses, and AI/ML frameworks.
- **Personalized Recommendations:** Calculates benchmark skill match percentages against the top in-demand skills for your chosen role and recommends the exact high-value skills you should learn next.

---

## How to Fetch Fresh Job Postings

To refresh your local data with the latest real-world job postings:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the batch scraper:**
   ```bash
   python src/fetch_jobs.py --results-wanted 40 --location "United States"
   ```
   *Options:*
   - `--roles`: specify custom search queries (e.g., `--roles "Data Analyst" "Data Scientist"`)
   - `--location`: target location (e.g., `"United States"`, `"Remote"`, `"London"`)
   - `--results-wanted`: number of postings per role query (default: 40)
   - `--hours-old`: job age filter in hours (default: 168 = 7 days)
   - `--sites`: specific sites to scrape (`linkedin`, `indeed`, `glassdoor`, `zip_recruiter`)

3. **Launch the Streamlit app:**
   ```bash
   streamlit run app/app.py
   ```
   The app automatically detects fresh postings in `data/processed/latest_jobs_with_skills.csv` (or falls back to the baseline dataset if you haven't fetched live jobs yet).

---

## Architecture

```
[Job Boards (LinkedIn, Indeed, Glassdoor, ZipRecruiter)]
                        │
                        ▼ (batch ingestion via python-jobspy)
             src/fetch_jobs.py
                        │
                        ▼ (raw data saved to data/raw/live_jobs_raw.csv)
            src/extract_skills.py
                        │
                        ▼ (skills extracted via NLP & taxonomy)
       data/processed/latest_jobs_with_skills.csv
                        │
                        ▼
                 app/app.py (Streamlit UI)
```
