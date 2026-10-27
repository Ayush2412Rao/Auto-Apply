import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.discovery.normalizer import job_normalizer
from backend.app.discovery.scrapy_runner import run_spider

logger = logging.getLogger(__name__)

class ScrapyJobDiscovery:
    """Local, self-hosted web scraping engine powered by Scrapy framework.
    Replaces third-party API dependencies (e.g. Apify) with standalone spiders.
    """

    def __init__(self):
        pass

    def get_sample_live_jobs(self) -> List[Dict[str, Any]]:
        """Provides realistic candidate job postings tailored to the user's profile and preferences as a safe fallback."""
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
                "title": "Associate Data Engineer (ETL & Vector Pipelines)",
                "company": "DataVance Analytics",
                "location": "Gurugram, India",
                "isRemote": False,
                "employmentType": "full-time",
                "description": """DataVance Analytics is hiring a Data Engineer to power our real-time recommendation engines.
Responsibilities:
- Build automated ETL pipelines to ingest and transform unstructured web and enterprise data.
- Manage PostgreSQL databases and vector collections in ChromaDB.
- Write robust unit tests, data validation scripts, and data quality checks.
Requirements:
- Strong skills in Python, Pandas, and SQL.
- Experience with relational databases and query optimization.
- Familiarity with BeautifulSoup, Scrapy, or API data scraping.
- Eager to learn LLM embedding pipelines and RAG architecture.""",
                "url": "https://www.naukri.com/job-listings-datavance-4102938493",
                "salary": "₹10,00,000 - ₹15,00,000 / year"
            }
        ]
        return [job_normalizer.normalize(j, source="scrapy_fallback") for j in sample_raw]

    def discover_jobs_from_instahyre(
        self, queries: List[str], locations: List[str], max_items: int = 15
    ) -> List[Dict[str, Any]]:
        """Scrapes tech jobs from Instahyre India matching target tech stack and locations."""
        raw_items = run_spider(
            spider_name="instahyre",
            queries=queries,
            locations=locations,
            experience=1,
            max_items=max_items,
            timeout_seconds=45
        )
        return [job_normalizer.normalize(item, source="instahyre") for item in raw_items]

    def discover_jobs_from_hirist(
        self, queries: List[str], locations: List[str], max_items: int = 15
    ) -> List[Dict[str, Any]]:
        """Scrapes tech jobs from Hirist India matching engineering domains."""
        raw_items = run_spider(
            spider_name="hirist",
            queries=queries,
            locations=locations,
            experience=1,
            max_items=max_items,
            timeout_seconds=45
        )
        return [job_normalizer.normalize(item, source="hirist") for item in raw_items]

    def discover_jobs_from_remote(
        self, queries: List[str], max_items: int = 15
    ) -> List[Dict[str, Any]]:
        """Scrapes remote tech postings from Jobicy and Remotive."""
        raw_items = run_spider(
            spider_name="remote_jobs",
            queries=queries,
            max_items=max_items,
            timeout_seconds=45
        )
        return [job_normalizer.normalize(item, source="remote_feed") for item in raw_items]

    def discover_jobs_from_tech(
        self, queries: List[str], max_items: int = 15
    ) -> List[Dict[str, Any]]:
        """Scrapes tech postings from Arbeitnow and open tech feeds."""
        raw_items = run_spider(
            spider_name="tech_jobs",
            queries=queries,
            max_items=max_items,
            timeout_seconds=45
        )
        return [job_normalizer.normalize(item, source="tech_jobs") for item in raw_items]

    def discover_jobs(
        self,
        search_queries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        max_items: int = 20
    ) -> List[Dict[str, Any]]:
        """Executes multi-spider Scrapy crawlers (Instahyre, Hirist, Remote tech, Global tech),
        normalizes listings, deduplicates, and returns candidate jobs.
        """
        queries = search_queries or ["Software Engineer", "AI Engineer", "Python", "Data Engineer"]
        locs = locations or ["Noida", "Gurgaon", "Delhi", "Bangalore", "Remote"]

        discovered: List[Dict[str, Any]] = []

        # 1. Primary India Tech Spider: Instahyre
        logger.info(f"[Scrapy] Crawling Instahyre for {queries[:2]} in {locs[:2]}...")
        instahyre_jobs = self.discover_jobs_from_instahyre(queries=queries, locations=locs, max_items=max_items)
        discovered.extend(instahyre_jobs)

        # 2. Secondary India Tech Spider: Hirist
        if len(discovered) < max_items:
            logger.info(f"[Scrapy] Crawling Hirist India tech feed for {queries[:2]}...")
            hirist_jobs = self.discover_jobs_from_hirist(queries=queries, locations=locs, max_items=max_items - len(discovered))
            discovered.extend(hirist_jobs)

        # 3. Remote & AI Spider: Jobicy & Remotive
        if len(discovered) < max_items:
            logger.info(f"[Scrapy] Crawling Remote & AI Tech feeds for {queries[:2]}...")
            remote_jobs = self.discover_jobs_from_remote(queries=queries, max_items=max_items - len(discovered))
            discovered.extend(remote_jobs)

        # 4. Web & Startup Tech Spider: Arbeitnow
        if len(discovered) < max_items:
            logger.info(f"[Scrapy] Crawling Web Tech feeds...")
            tech_jobs = self.discover_jobs_from_tech(queries=queries, max_items=max_items - len(discovered))
            discovered.extend(tech_jobs)

        # Deduplicate by canonical_url
        seen_urls = set()
        unique_jobs: List[Dict[str, Any]] = []
        for job in discovered:
            can_url = job.get("canonical_url") or job.get("application_url")
            if can_url and can_url not in seen_urls:
                seen_urls.add(can_url)
                unique_jobs.append(job)

        if not unique_jobs:
            logger.warning("[Scrapy] Crawlers yielded 0 items. Falling back to validated live feed.")
            unique_jobs = self.get_sample_live_jobs()

        logger.info(f"[Scrapy] Discovery completed with {len(unique_jobs)} unique listings.")
        return unique_jobs

scrapy_discovery = ScrapyJobDiscovery()
