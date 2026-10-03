"""
Skills Taxonomy for Data & AI Roles:
- Data Analyst
- Data Scientist
- Data Engineer
- Machine Learning Engineer / AI Engineer
- Business Intelligence Analyst
"""

SKILLS_TAXONOMY = [
    # Programming languages
    "Python", "R", "SQL", "Java", "Scala", "C++", "Julia", "Go", "Bash",

    # Data tools & BI
    "Excel", "Power BI", "Tableau", "Looker", "Google Sheets", "Qlik", "Alteryx", "SAS", "VBA", "SAP", "PowerPoint",

    # Databases & Data Warehouses
    "MySQL", "PostgreSQL", "MongoDB", "Snowflake", "BigQuery", "Redshift", "DynamoDB", "Cassandra", "Redis", "Elasticsearch",

    # Data Engineering & Pipelines
    "Spark", "Hadoop", "Airflow", "Kafka", "dbt", "Databricks", "ETL", "Flink", "PySpark", "Delta Lake",

    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "CI/CD", "Linux", "Terraform",

    # ML/Data Science & Deep Learning Frameworks
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Polars", "XGBoost", "LightGBM", "OpenCV", "Hugging Face",

    # Statistics, AI & Analytics concepts
    "A/B testing", "Statistics", "Regression", "Machine Learning", 
    "Deep Learning", "NLP", "Hypothesis Testing", "Data Visualization",
    "Computer Vision", "LLMs", "Generative AI", "LangChain", "MLOps", "MLflow",

    # Project / Collaboration tools
    "Jira", "Jupyter"
]

if __name__ == '__main__':
    print(f"Total skills in taxonomy: {len(SKILLS_TAXONOMY)}")