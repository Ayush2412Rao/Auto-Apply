import json
import scrapy
from backend.app.discovery.scrapers.items import JobPostItem

class TechJobsSpider(scrapy.Spider):
    name = "tech_jobs"
    allowed_domains = ["arbeitnow.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
    }

    def __init__(self, queries: str = "software,engineer,developer,python,ai,data",
                 max_items: str = "30", **kwargs):
        super().__init__(**kwargs)
        self.queries = [q.strip().lower() for q in queries.split(",") if q.strip()]
        self.max_items = int(max_items)
        self.yielded_count = 0
        self.start_urls = ["https://www.arbeitnow.com/api/job-board-api"]

    def parse(self, response):
        if self.yielded_count >= self.max_items:
            return

        try:
            data = json.loads(response.text)
        except Exception:
            return

        jobs = data.get("data", [])
        for j in jobs:
            if self.yielded_count >= self.max_items:
                break

            title = j.get("title") or "Software Engineer"
            title_lower = title.lower()
            tags = j.get("tags") or []
            tags_lower = [t.lower() for t in tags]

            matches = any(
                q in title_lower or any(q in t for t in tags_lower)
                for q in self.queries
            )
            if not matches:
                continue

            company = j.get("company_name") or "Unknown"
            location = j.get("location") or "Remote"
            desc = j.get("description") or ""
            url = j.get("url") or ""
            is_remote = bool(j.get("remote", False) or "remote" in location.lower())

            item = JobPostItem()
            item["title"] = title
            item["company"] = company
            item["location"] = location
            item["description"] = desc
            item["url"] = url
            item["salary"] = None
            item["experience"] = "1-3 yrs"
            item["skills"] = ", ".join(tags)
            item["is_remote"] = is_remote
            item["source"] = "arbeitnow"
            item["posted_at"] = j.get("created_at")

            self.yielded_count += 1
            yield item
