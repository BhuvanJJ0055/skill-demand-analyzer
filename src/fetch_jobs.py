"""
Batch Job Ingestion Pipeline using python-jobspy
Fetches real-time job postings from LinkedIn, Indeed, Glassdoor, and ZipRecruiter
across modern Data & AI roles, deduplicates them, and enriches them with extracted skills.
"""

import os
import sys
import time
import argparse
import pandas as pd
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    from jobspy import scrape_jobs  # type: ignore
except ImportError:
    scrape_jobs = None

try:
    from src.extract_skills import enrich_dataframe, SKILLS_TAXONOMY
except ImportError:
    from extract_skills import enrich_dataframe, SKILLS_TAXONOMY  # type: ignore

DEFAULT_ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Machine Learning Engineer",
    "Business Intelligence Analyst"
]

DEFAULT_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]

def resolve_country_indeed(location):
    """
    Maps location string to JobSpy's country_indeed parameter.
    """
    loc_lower = str(location).lower()
    if 'india' in loc_lower:
        return 'India'
    elif any(k in loc_lower for k in ['uk', 'united kingdom', 'london']):
        return 'UK'
    elif 'canada' in loc_lower:
        return 'Canada'
    elif 'germany' in loc_lower:
        return 'Germany'
    elif 'australia' in loc_lower:
        return 'Australia'
    elif 'france' in loc_lower:
        return 'France'
    return 'USA'

def fetch_role_postings(role, location="United States", results_wanted=25, hours_old=168, sites=DEFAULT_SITES):
    """
    Fetches job postings for a single role query across selected job sites.
    """
    if scrape_jobs is None:
        raise ImportError(
            "python-jobspy is not installed.\n"
            "Please install it using: pip install python-jobspy"
        )
    
    country_indeed = resolve_country_indeed(location)
    print(f"\n🔍 Searching for '{role}' in '{location}' (Country: {country_indeed}) across {sites} (target: {results_wanted} per site)...")
    
    try:
        jobs = scrape_jobs(
            site_name=sites,
            search_term=role,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country_indeed,
            linkedin_fetch_description=True,
            description_format="markdown"
        )
        print(f"   ✅ Retrieved {len(jobs)} total postings for '{role}'")
        return jobs
    except Exception as e:
        print(f"   ⚠️ Warning: Encountered error while scraping '{role}': {e}")
        return pd.DataFrame()

def run_ingestion_pipeline(
    roles=DEFAULT_ROLES,
    location="United States",
    results_wanted=25,
    hours_old=168,
    sites=DEFAULT_SITES,
    output_raw=None,
    output_processed=None,
    enrich=True
):
    """
    Orchestrates batch ingestion:
    1. Iterates through all target roles
    2. Combines, deduplicates, and cleans records
    3. Saves raw data to disk
    4. Automatically enriches data with skill extraction
    """
    if scrape_jobs is None:
        print("\n❌ Error: python-jobspy is required for batch ingestion.")
        print("Run: pip install python-jobspy\n")
        sys.exit(1)

    all_jobs = []
    
    for i, role in enumerate(roles):
        df_role = fetch_role_postings(
            role=role,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            sites=sites
        )
        if not df_role.empty:
            df_role['search_query_role'] = role
            all_jobs.append(df_role)
            
        # Brief pause between queries
        if i < len(roles) - 1:
            time.sleep(2)
            
    if not all_jobs:
        print("❌ No job postings were retrieved. Check your network connection or parameters.")
        return None

    combined_df = pd.concat(all_jobs, ignore_index=True)
    initial_count = len(combined_df)
    print(f"\n📦 Aggregated {initial_count} raw records from job boards.")

    # Standardize column names if needed
    rename_map = {
        'site': 'source',
        'job_url': 'link'
    }
    for old_col, new_col in rename_map.items():
        if old_col in combined_df.columns and new_col not in combined_df.columns:
            combined_df[new_col] = combined_df[old_col]

    # Ensure required columns exist
    if 'date_posted' not in combined_df.columns:
        combined_df['date_posted'] = datetime.today().strftime('%Y-%m-%d')
    else:
        combined_df['date_posted'] = combined_df['date_posted'].fillna(datetime.today().strftime('%Y-%m-%d'))

    # Fill empty/null descriptions with title to avoid dropping postings
    if 'description' not in combined_df.columns:
        combined_df['description'] = combined_df['title'].fillna('')
    else:
        combined_df['description'] = combined_df['description'].fillna('')
        # If description is blank, fallback to title so row is retained
        blank_desc_mask = combined_df['description'].str.strip() == ''
        combined_df.loc[blank_desc_mask, 'description'] = combined_df.loc[blank_desc_mask, 'title'].fillna('')

    # Deduplicate safely on (title, company) if available
    if 'title' in combined_df.columns and 'company' in combined_df.columns:
        # Filter out obvious empty titles
        combined_df = combined_df[combined_df['title'].str.strip() != '']
        combined_df = combined_df.drop_duplicates(subset=['title', 'company'], keep='first')

    # Deduplicate non-empty links
    if 'link' in combined_df.columns:
        has_link = combined_df['link'].notna() & (combined_df['link'].astype(str).str.strip() != '')
        with_links = combined_df[has_link].drop_duplicates(subset=['link'], keep='first')
        without_links = combined_df[~has_link]
        combined_df = pd.concat([with_links, without_links], ignore_index=True)

    print(f"📊 Deduplicated to {len(combined_df)} unique postings.")

    # Save raw data
    if output_raw is None:
        output_raw = os.path.normpath(os.path.join(script_dir, "../data/raw/live_jobs_raw.csv"))
    
    os.makedirs(os.path.dirname(output_raw), exist_ok=True)
    combined_df.to_csv(output_raw, index=False)
    print(f"💾 Raw jobs saved to: {output_raw}")

    # Enrich with skills if requested
    if enrich:
        if output_processed is None:
            output_processed = os.path.normpath(os.path.join(script_dir, "../data/processed/latest_jobs_with_skills.csv"))
            
        print("\n⚡ Running NLP skill extraction on live postings...")
        enriched_df = enrich_dataframe(combined_df, SKILLS_TAXONOMY)
        
        os.makedirs(os.path.dirname(output_processed), exist_ok=True)
        enriched_df.to_csv(output_processed, index=False)
        print(f"🎉 Enriched dataset saved to: {output_processed}")
        
        print("\nDetected Role Distribution:")
        print(enriched_df['role_category'].value_counts())
        return enriched_df

    return combined_df

def main():
    parser = argparse.ArgumentParser(description="Batch Job Ingestion using python-jobspy")
    parser.add_argument(
        "--roles",
        nargs="+",
        default=DEFAULT_ROLES,
        help="List of role search terms to fetch"
    )
    parser.add_argument(
        "--location",
        type=str,
        default="India",
        help="Target location / country (e.g. 'India', 'United States', 'Remote', 'London', etc.)"
    )
    parser.add_argument(
        "--results-wanted",
        type=int,
        default=25,
        help="Target number of results per role query per site"
    )
    parser.add_argument(
        "--hours-old",
        type=int,
        default=168,
        help="Filter jobs posted within the last N hours (default 168 = 7 days)"
    )
    parser.add_argument(
        "--sites",
        nargs="+",
        default=DEFAULT_SITES,
        help="Job boards to query: linkedin, indeed, glassdoor, zip_recruiter"
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Skip automatic skill extraction after scraping"
    )

    args = parser.parse_args()

    run_ingestion_pipeline(
        roles=args.roles,
        location=args.location,
        results_wanted=args.results_wanted,
        hours_old=args.hours_old,
        sites=args.sites,
        enrich=not args.no_enrich
    )

if __name__ == '__main__':
    main()
