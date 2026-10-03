"""
Learning Resources and Fresher Job Matcher
Provides curated YouTube channels, official documentation links,
and filters entry-level / fresher job postings.
"""

import urllib.parse
import re
import pandas as pd

# Curated catalog of top YouTube educators and official websites per skill
SKILL_RESOURCES = {
    # Programming Languages
    "SQL": {
        "official": "https://www.postgresql.org/docs/",
        "official_name": "PostgreSQL Official Documentation",
        "youtube": [
            {"name": "Alex The Analyst", "channel": "https://www.youtube.com/@AlexTheAnalyst"},
            {"name": "Luke Barousse", "channel": "https://www.youtube.com/@LukeBarousse"},
            {"name": "freeCodeCamp.org", "channel": "https://www.youtube.com/@freecodecamp"}
        ],
        "tip": "Master SELECT, JOINs, GROUP BY, Window Functions, and CTEs."
    },
    "Python": {
        "official": "https://docs.python.org/3/",
        "official_name": "Python 3 Official Docs",
        "youtube": [
            {"name": "Corey Schafer", "channel": "https://www.youtube.com/@coreyms"},
            {"name": "Programming with Mosh", "channel": "https://www.youtube.com/@programmingwithmosh"},
            {"name": "freeCodeCamp.org", "channel": "https://www.youtube.com/@freecodecamp"}
        ],
        "tip": "Focus on data structures, OOP, list comprehensions, and script automation."
    },
    "R": {
        "official": "https://www.r-project.org/other-docs.html",
        "official_name": "R Project Documentation",
        "youtube": [
            {"name": "R Programming 101", "channel": "https://www.youtube.com/@RProgramming101"},
            {"name": "StatQuest with Josh Starmer", "channel": "https://www.youtube.com/@statquest"}
        ],
        "tip": "Learn Tidyverse (dplyr, ggplot2) and statistical modeling."
    },

    # BI & Data Tools
    "Power BI": {
        "official": "https://learn.microsoft.com/en-us/power-bi/",
        "official_name": "Microsoft Power BI Documentation",
        "youtube": [
            {"name": "Guy in a Cube", "channel": "https://www.youtube.com/@GuyInACube"},
            {"name": "Chandoo", "channel": "https://www.youtube.com/@chandoo_"},
            {"name": "Curibal (Avi Singh)", "channel": "https://www.youtube.com/@AviSinghPowerBI"}
        ],
        "tip": "Focus on DAX, Power Query (M), and star schema data modeling."
    },
    "Tableau": {
        "official": "https://help.tableau.com/",
        "official_name": "Tableau Help & Documentation",
        "youtube": [
            {"name": "Tableau Tim", "channel": "https://www.youtube.com/@TableauTim"},
            {"name": "Alex The Analyst", "channel": "https://www.youtube.com/@AlexTheAnalyst"}
        ],
        "tip": "Learn Calculated Fields, Level of Detail (LOD) expressions, and dashboard actions."
    },
    "Excel": {
        "official": "https://support.microsoft.com/excel",
        "official_name": "Microsoft Excel Help Center",
        "youtube": [
            {"name": "Leila Gharani", "channel": "https://www.youtube.com/@LeilaGharani"},
            {"name": "Chandoo", "channel": "https://www.youtube.com/@chandoo_"},
            {"name": "Kevin Stratvert", "channel": "https://www.youtube.com/@KevinStratvert"}
        ],
        "tip": "Master XLOOKUP, INDEX/MATCH, Pivot Tables, and conditional formulas."
    },
    "Looker": {
        "official": "https://cloud.google.com/looker/docs",
        "official_name": "Google Cloud Looker Docs",
        "youtube": [
            {"name": "Google Cloud Tech", "channel": "https://www.youtube.com/@googlecloudtech"},
            {"name": "Luke Barousse", "channel": "https://www.youtube.com/@LukeBarousse"}
        ],
        "tip": "Learn LookML, views, models, and explores."
    },

    # ML & Data Science Libraries
    "Pandas": {
        "official": "https://pandas.pydata.org/docs/",
        "official_name": "Pandas Official Documentation",
        "youtube": [
            {"name": "Keith Galli", "channel": "https://www.youtube.com/@keithgalli"},
            {"name": "Corey Schafer", "channel": "https://www.youtube.com/@coreyms"}
        ],
        "tip": "Practice groupby, merge/concat, handling missing data, and lambda functions."
    },
    "NumPy": {
        "official": "https://numpy.org/doc/stable/",
        "official_name": "NumPy Official Documentation",
        "youtube": [
            {"name": "Keith Galli", "channel": "https://www.youtube.com/@keithgalli"},
            {"name": "freeCodeCamp.org", "channel": "https://www.youtube.com/@freecodecamp"}
        ],
        "tip": "Understand vectorization, broadcasting, array slicing, and matrix algebra."
    },
    "Scikit-learn": {
        "official": "https://scikit-learn.org/stable/",
        "official_name": "Scikit-Learn Documentation",
        "youtube": [
            {"name": "StatQuest with Josh Starmer", "channel": "https://www.youtube.com/@statquest"},
            {"name": "Krish Naik", "channel": "https://www.youtube.com/@krishnaik06"}
        ],
        "tip": "Master train/test split, cross-validation, pipelines, and model evaluation metrics."
    },
    "PyTorch": {
        "official": "https://pytorch.org/docs/stable/index.html",
        "official_name": "PyTorch Documentation",
        "youtube": [
            {"name": "Daniel Bourke", "channel": "https://www.youtube.com/@mrdbourke"},
            {"name": "Andrej Karpathy", "channel": "https://www.youtube.com/@AndrejKarpathy"}
        ],
        "tip": "Understand tensors, autograd, nn.Module, and custom training loops."
    },
    "TensorFlow": {
        "official": "https://www.tensorflow.org/api_docs",
        "official_name": "TensorFlow API Documentation",
        "youtube": [
            {"name": "Nicholas Renotte", "channel": "https://www.youtube.com/@NicholasRenotte"},
            {"name": "freeCodeCamp.org", "channel": "https://www.youtube.com/@freecodecamp"}
        ],
        "tip": "Learn tf.keras, layers, callbacks, and SavedModel deployment."
    },

    # Data Engineering & Cloud
    "Spark": {
        "official": "https://spark.apache.org/docs/latest/",
        "official_name": "Apache Spark Official Docs",
        "youtube": [
            {"name": "Darshil Parmar", "channel": "https://www.youtube.com/@DarshilParmar"},
            {"name": "Seattle Data Guy", "channel": "https://www.youtube.com/@SeattleDataGuy"}
        ],
        "tip": "Learn PySpark DataFrames, partitions, transformations, and actions."
    },
    "dbt": {
        "official": "https://docs.getdbt.com/",
        "official_name": "dbt Developer Documentation",
        "youtube": [
            {"name": "Seattle Data Guy", "channel": "https://www.youtube.com/@SeattleDataGuy"},
            {"name": "Kahan Data Solutions", "channel": "https://www.youtube.com/@kahandatasolutions"}
        ],
        "tip": "Master models, refs, sources, tests, and documentation."
    },
    "Airflow": {
        "official": "https://airflow.apache.org/docs/",
        "official_name": "Apache Airflow Documentation",
        "youtube": [
            {"name": "Marc Lamberti", "channel": "https://www.youtube.com/@marclamberti"},
            {"name": "Darshil Parmar", "channel": "https://www.youtube.com/@DarshilParmar"}
        ],
        "tip": "Understand DAGs, operators, tasks, sensors, and task execution."
    },
    "Kafka": {
        "official": "https://kafka.apache.org/documentation/",
        "official_name": "Apache Kafka Documentation",
        "youtube": [
            {"name": "Stephane Maarek", "channel": "https://www.youtube.com/@StephaneMaarek"},
            {"name": "Confluent", "channel": "https://www.youtube.com/@Confluent"}
        ],
        "tip": "Understand topics, partitions, producers, consumer groups, and brokers."
    },
    "AWS": {
        "official": "https://docs.aws.amazon.com/",
        "official_name": "AWS Official Documentation",
        "youtube": [
            {"name": "Stephane Maarek", "channel": "https://www.youtube.com/@StephaneMaarek"},
            {"name": "TechWorld with Nana", "channel": "https://www.youtube.com/@TechWorldwithNana"}
        ],
        "tip": "Start with S3, EC2, IAM, Lambda, and Glue / Athena."
    },
    "Snowflake": {
        "official": "https://docs.snowflake.com/",
        "official_name": "Snowflake Documentation",
        "youtube": [
            {"name": "Darshil Parmar", "channel": "https://www.youtube.com/@DarshilParmar"},
            {"name": "Kahan Data Solutions", "channel": "https://www.youtube.com/@kahandatasolutions"}
        ],
        "tip": "Learn virtual warehouses, micro-partitioning, time travel, and Snowpark."
    },
    "Docker": {
        "official": "https://docs.docker.com/",
        "official_name": "Docker Official Documentation",
        "youtube": [
            {"name": "TechWorld with Nana", "channel": "https://www.youtube.com/@TechWorldwithNana"},
            {"name": "NetworkChuck", "channel": "https://www.youtube.com/@NetworkChuck"}
        ],
        "tip": "Master Dockerfile creation, image building, container networking, and docker-compose."
    },

    # Modern AI & Concepts
    "LLMs": {
        "official": "https://huggingface.co/docs",
        "official_name": "Hugging Face Transformers Docs",
        "youtube": [
            {"name": "Andrej Karpathy", "channel": "https://www.youtube.com/@AndrejKarpathy"},
            {"name": "Krish Naik", "channel": "https://www.youtube.com/@krishnaik06"}
        ],
        "tip": "Understand self-attention, tokenization, prompt engineering, RAG, and fine-tuning."
    },
    "Generative AI": {
        "official": "https://platform.openai.com/docs/",
        "official_name": "OpenAI / Generative AI Docs",
        "youtube": [
            {"name": "Andrej Karpathy", "channel": "https://www.youtube.com/@AndrejKarpathy"},
            {"name": "AI Jason", "channel": "https://www.youtube.com/@AIJasonZ"}
        ],
        "tip": "Focus on embeddings, vector databases (Chroma, Pinecone), and agent frameworks."
    },
    "LangChain": {
        "official": "https://python.langchain.com/docs/",
        "official_name": "LangChain Python Documentation",
        "youtube": [
            {"name": "AI Jason", "channel": "https://www.youtube.com/@AIJasonZ"},
            {"name": "Krish Naik", "channel": "https://www.youtube.com/@krishnaik06"}
        ],
        "tip": "Learn LCEL, chains, document loaders, vector store retrievers, and tools."
    },
    "Statistics": {
        "official": "https://www.khanacademy.org/math/statistics-probability",
        "official_name": "Khan Academy Statistics & Probability",
        "youtube": [
            {"name": "StatQuest with Josh Starmer", "channel": "https://www.youtube.com/@statquest"},
            {"name": "zedstatistics", "channel": "https://www.youtube.com/@zedstatistics"}
        ],
        "tip": "Master mean/median/std, probability distributions, p-values, and hypothesis testing."
    },
    "A/B testing": {
        "official": "https://exp-platform.com/",
        "official_name": "Experimentation Platform Guidance",
        "youtube": [
            {"name": "Luke Barousse", "channel": "https://www.youtube.com/@LukeBarousse"},
            {"name": "StatQuest with Josh Starmer", "channel": "https://www.youtube.com/@statquest"}
        ],
        "tip": "Understand sample size calculation, statistical significance, null hypothesis, and variance."
    }
}

def get_skill_learning_info(skill):
    """
    Returns learning metadata for a given skill.
    If the skill is not in the curated list, generates dynamic search links.
    """
    cleaned = skill.strip()
    if cleaned in SKILL_RESOURCES:
        info = SKILL_RESOURCES[cleaned].copy()
    else:
        # Check case-insensitive match
        matched_key = next((k for k in SKILL_RESOURCES if k.lower() == cleaned.lower()), None)
        if matched_key:
            info = SKILL_RESOURCES[matched_key].copy()
        else:
            # Fallback dynamic generator
            encoded = urllib.parse.quote(f"{cleaned} programming tutorial")
            info = {
                "official": f"https://www.google.com/search?q={urllib.parse.quote(cleaned + ' official documentation')}",
                "official_name": f"{cleaned} Documentation",
                "youtube": [
                    {"name": "freeCodeCamp.org", "channel": "https://www.youtube.com/@freecodecamp"},
                    {"name": "Search on YouTube", "channel": f"https://www.youtube.com/results?search_query={encoded}"}
                ],
                "tip": f"Study the fundamentals of {cleaned} and build a portfolio project."
            }

    # Add quick YouTube tutorial search link
    search_q = urllib.parse.quote(f"{cleaned} full course tutorial beginner")
    info["youtube_search_url"] = f"https://www.youtube.com/results?search_query={search_q}"
    return info

def filter_fresher_jobs(df, role_choice, top_n=5):
    """
    Finds job postings in df suitable for freshers / entry-level candidates
    for the selected role.
    """
    if df.empty:
        return []

    # Filter to selected role if possible
    if 'role_category' in df.columns:
        role_df = df[df['role_category'] == role_choice]
        if role_df.empty:
            role_df = df
    else:
        role_df = df

    fresher_title_keywords = [
        'fresher', 'entry', 'junior', 'jr', 'associate', 
        'intern', 'trainee', 'graduate', 'level 1', 'l1', 'entry-level'
    ]
    
    fresher_desc_phrases = [
        r'\b0\s*-\s*1\s*years?\b', r'\b0\s*-\s*2\s*years?\b', 
        r'\b0\s*to\s*1\s*years?\b', r'\b0\s*to\s*2\s*years?\b',
        r'\bentry[\s-]level\b', r'\bfreshers?\b', r'\brecent\s+graduate\b',
        r'\bno\s+prior\s+experience\b', r'\bno\s+experience\s+required\b',
        r'\bbachelor\'?s?\s+degree\b'
    ]

    desc_regex = re.compile('|'.join(fresher_desc_phrases), re.IGNORECASE)

    matched_jobs = []

    for _, row in role_df.iterrows():
        title = str(row.get('title', ''))
        title_lower = title.lower()
        desc = str(row.get('description', ''))
        job_level = str(row.get('job_level', '')).lower()

        score = 0
        reasons = []

        # Check title
        if any(kw in title_lower for kw in fresher_title_keywords):
            score += 3
            reasons.append("Title specifies entry / junior / fresher level")

        # Check job_level column from job boards
        if any(lvl in job_level for lvl in ['entry', 'intern', 'associate']):
            score += 3
            reasons.append("Platform tagged as Entry Level / Associate")

        # Check description
        match = desc_regex.search(desc)
        if match:
            score += 2
            reasons.append(f"Mentions: '{match.group(0)}'")

        if score > 0:
            link = str(row.get('link', '')) or str(row.get('job_url', ''))
            matched_jobs.append({
                'id': row.get('id', ''),
                'title': title,
                'company': row.get('company', 'Not specified'),
                'location': row.get('location', 'Remote / Not specified'),
                'link': link if link.startswith('http') else None,
                'source': row.get('source', row.get('site', 'Job Board')),
                'score': score,
                'reason': reasons[0] if reasons else "Entry-level friendly",
                'skills': row.get('extracted_skills', [])
            })

    # Sort by relevance score
    matched_jobs.sort(key=lambda x: x['score'], reverse=True)

    # Fallback: if no strict fresher markers found, pick lowest experience / associate jobs
    if not matched_jobs:
        for _, row in role_df.head(top_n).iterrows():
            link = str(row.get('link', '')) or str(row.get('job_url', ''))
            matched_jobs.append({
                'id': row.get('id', ''),
                'title': row.get('title', 'Job Opening'),
                'company': row.get('company', 'Company'),
                'location': row.get('location', 'Location'),
                'link': link if link.startswith('http') else None,
                'source': row.get('source', row.get('site', 'Job Board')),
                'score': 1,
                'reason': "Recent posting for target role",
                'skills': row.get('extracted_skills', [])
            })

    return matched_jobs[:top_n]
