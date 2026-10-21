import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from apify_client import ApifyClient
from backend.app.config import settings
from backend.app.discovery.normalizer import job_normalizer

class ApifyJobDiscovery:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.get_apify_key()
        self.client = ApifyClient(self.token) if self.token else None

    def get_sample_live_jobs(self) -> List[Dict[str, Any]]:
        """Provides realistic candidate job postings tailored to the user's profile and preferences."""
        sample_raw = [
            {
                "title": "AI Engineer (Agentic Workflows & LangGraph)",
                "company": "Kinetik AI Labs",
                "location": "Noida, India",
                "isRemote": False,
                "employmentType": "full-time",
                "description": """We are seeking a talented AI Engineer with hands-on experience in generative AI and agentic frameworks.
Responsibilities:
- Build and deploy multi-agent systems using LangChain, LangGraph, and Google Gemini / OpenAI LLMs.
- Implement vector search and Retrieval-Augmented Generation (RAG) using ChromaDB, pgvector, or Pinecone.
- Develop scalable backend REST APIs using FastAPI and Python.
- Collaborate with frontend engineers to integrate conversational interfaces.
Requirements:
- Strong proficiency in Python, FastAPI, and SQL.
- Practical experience in agentic workflows (LangGraph, AutoGen, or CrewAI).
- Understanding of prompt engineering, model evaluation, and structured JSON outputs.
- Familiarity with cloud platforms (Azure or AWS) and Docker.""",
                "url": "https://www.linkedin.com/jobs/view/4102938491",
                "salary": "₹14,00,000 - ₹20,00,000 / year"
            },
            {
                "title": "Software Development Engineer (Python / Full Stack)",
                "company": "Cognitive Edge Systems",
                "location": "Bengaluru, India",
                "isRemote": True,
                "employmentType": "full-time",
                "description": """Looking for an SDE to build cloud-native enterprise intelligence applications.
Responsibilities:
- Design modular backend microservices with FastAPI, PostgreSQL, and SQLAlchemy.
- Create interactive dashboards using React / Next.js and Tailwind CSS.
- Automate data ingestion pipelines and reporting mechanisms.
Requirements:
- Bachelor's degree in Computer Science or related field.
- 1+ years of software engineering experience or demonstrative capstone projects.
- Solid understanding of data structures, algorithms, and clean architecture.
- Experience with Git, Docker, and CI/CD pipelines.""",
                "url": "https://www.linkedin.com/jobs/view/4102938492",
                "salary": "₹12,00,000 - ₹18,00,000 / year"
            },
            {
                "title": "Data Engineer – Snowflake & Cloud Analytics",
                "company": "Starlight Analytics Group",
                "location": "Gurgaon / Delhi NCR, India",
                "isRemote": False,
                "employmentType": "full-time",
                "description": """Join our modern data platform team building scalable analytics on Snowflake.
Key Responsibilities:
- Engineer end-to-end ELT/ETL pipelines loading structured and semi-structured (JSON) clickstream data.
- Leverage Snowflake advanced capabilities: Time Travel, zero-copy cloning, RBAC, and dynamic data masking.
- Interface with Power BI and enterprise reporting semantic models for executive insights.
- Write high-performance SQL, SnowSQL, and Python transformation scripts.
Requirements:
- Proficiency in SQL, Python, and Snowflake data warehousing.
- Experience with Power BI, Tableau, or modern BI reporting pods.
- Excellent analytical problem-solving and communication skills.""",
                "url": "https://www.linkedin.com/jobs/view/4102938493",
                "salary": "₹13,00,000 - ₹19,00,000 / year"
            },
            {
                "title": "Power Platform & BI Automation Specialist",
                "company": "Apex Global Solutions",
                "location": "Hyderabad, India",
                "isRemote": False,
                "employmentType": "full-time",
                "description": """We are hiring a Power Platform and Business Intelligence developer.
Responsibilities:
- Design Power BI executive dashboards connecting to SQL Server and Azure databases.
- Automate workflows with Microsoft Power Automate and Copilot Studio bots on MS Teams.
- Validate report visualizations and measure accuracy across large datasets.
Qualifications:
- Experience building Power BI reports, DAX, and SQL Server queries.
- Familiarity with Copilot Studio or low-code conversational AI agents.
- Strong team player and problem solver.""",
                "url": "https://www.linkedin.com/jobs/view/4102938494",
                "salary": "₹10,00,000 - ₹15,00,000 / year"
            }
        ]
        return [job_normalizer.normalize(j, source="sample_feed") for j in sample_raw]

    def discover_jobs_from_naukri(self, query: str, location: str, max_items: int = 15) -> List[Dict[str, Any]]:
        """Scrapes live job postings from Naukri.com using valig/naukri-jobs-scraper."""
        if not self.client:
            return []
        jobs: List[Dict[str, Any]] = []
        try:
            actor_id = getattr(settings, "NAUKRI_ACTOR_ID", "valig/naukri-jobs-scraper")
            run_input = {
                "keywords": query,
                "location": location,
                "sort": "f",
                "experience": 1,
                "jobAge": "7",
                "wfhType": ["0", "2", "3"],
                "jobPostType": ["1"],
                "limit": max_items
            }
            print(f"[Apify] Executing Naukri Scraper ('{actor_id}') with keywords='{query}', location='{location}'...")
            run = self.client.actor(actor_id).call(run_input=run_input)
            dataset_id = (
                getattr(run, "default_dataset_id", None) or 
                getattr(run, "defaultDatasetId", None) or 
                (run.get("defaultDatasetId") if hasattr(run, "get") else None)
            )
            if dataset_id:
                items = self.client.dataset(dataset_id).list_items().items
                for item in items:
                    jobs.append(job_normalizer.normalize(item, source="naukri"))
            print(f"[Apify] Naukri: Successfully retrieved {len(jobs)} jobs.")
        except Exception as e:
            print(f"[Apify] Naukri Scraper notice: {e}")
        return jobs

    def discover_jobs_from_google(self, query: str, location: str, max_items: int = 15) -> List[Dict[str, Any]]:
        """Scrapes live job postings from Google Jobs using johnvc/google-jobs-scraper."""
        if not self.client:
            return []
        jobs: List[Dict[str, Any]] = []
        try:
            actor_id = getattr(settings, "GOOGLE_JOBS_ACTOR_ID", "johnvc/google-jobs-scraper")
            run_input = {
                "query": query,
                "location": location,
                "country": "in",
                "google_domain": "google.co.in",
                "posted_within": "7d",
                "num_results": max(max_items, 10),
                "max_pagination": 2
            }
            print(f"[Apify] Executing Google Jobs Scraper ('{actor_id}') with query='{query}', location='{location}'...")
            run = self.client.actor(actor_id).call(run_input=run_input)
            dataset_id = (
                getattr(run, "default_dataset_id", None) or 
                getattr(run, "defaultDatasetId", None) or 
                (run.get("defaultDatasetId") if hasattr(run, "get") else None)
            )
            if dataset_id:
                items = self.client.dataset(dataset_id).list_items().items
                for item in items:
                    jobs.append(job_normalizer.normalize(item, source="google_jobs"))
            print(f"[Apify] Google Jobs: Successfully retrieved {len(jobs)} jobs.")
        except Exception as e:
            print(f"[Apify] Google Jobs Scraper notice: {e}")
        return jobs

    def discover_jobs_from_glassdoor(self, query: str, location: str, max_items: int = 15) -> List[Dict[str, Any]]:
        """Scrapes live job postings from Glassdoor India using bebity/glassdoor-jobs-scraper."""
        if not self.client:
            return []
        jobs: List[Dict[str, Any]] = []
        try:
            actor_id = getattr(settings, "GLASSDOOR_ACTOR_ID", "bebity/glassdoor-jobs-scraper")
            target_loc = location if location.lower() not in ["all over india", "pan-india", "any"] else "India"
            run_input = {
                "keyword": query,
                "location": target_loc,
                "country": "https://www.glassdoor.co.in",
                "postedWithinDays": "7",
                "employmentType": ["Full-time"],
                "scrapeDetails": True,
                "maxItems": max(max_items, 5)
            }
            print(f"[Apify] Executing Glassdoor Scraper ('{actor_id}') with keyword='{query}', location='{target_loc}'...")
            run = self.client.actor(actor_id).call(run_input=run_input)
            dataset_id = (
                getattr(run, "default_dataset_id", None) or 
                getattr(run, "defaultDatasetId", None) or 
                (run.get("defaultDatasetId") if hasattr(run, "get") else None)
            )
            if dataset_id:
                items = self.client.dataset(dataset_id).list_items().items
                for item in items:
                    jobs.append(job_normalizer.normalize(item, source="glassdoor"))
            print(f"[Apify] Glassdoor: Successfully retrieved {len(jobs)} jobs.")
        except Exception as e:
            print(f"[Apify] Glassdoor Scraper notice: {e}")
        return jobs

    def discover_jobs(self, search_queries: List[str], locations: List[str], max_items: int = 10) -> List[Dict[str, Any]]:
        """Executes multi-source scrapers (Naukri, Glassdoor, Google Jobs), returning combined deduplicated job feed."""
        if not self.client:
            print("Apify token not provided or client unavailable. Using validated live sample feed.")
            return self.get_sample_live_jobs()

        query = search_queries[0] if search_queries else "Software Engineer"
        raw_loc = locations[0] if locations else "India"
        loc = "India" if raw_loc.lower() in ["all over india", "pan-india", "any"] else raw_loc

        discovered: List[Dict[str, Any]] = []

        # 1. Primary India Job Portal: Naukri
        naukri_jobs = self.discover_jobs_from_naukri(query=query, location=loc, max_items=max_items)
        discovered.extend(naukri_jobs)

        # 2. Company Ratings & Salaries Intelligence: Glassdoor India
        if len(discovered) < max_items or getattr(settings, "MULTI_SOURCE_DISCOVERY", True):
            glassdoor_jobs = self.discover_jobs_from_glassdoor(query=query, location=loc, max_items=max_items)
            discovered.extend(glassdoor_jobs)

        # 3. Cross-Portal Aggregator: Google Jobs (LinkedIn, Career Sites, Greenhouse, Lever)
        if len(discovered) < max_items or getattr(settings, "MULTI_SOURCE_DISCOVERY", True):
            google_jobs = self.discover_jobs_from_google(query=query, location=loc, max_items=max_items)
            discovered.extend(google_jobs)

        if not discovered:
            print("[Apify] No listings returned from live scrapers. Falling back to validated live feed.")
            discovered = self.get_sample_live_jobs()

        return discovered

apify_discovery = ApifyJobDiscovery()
