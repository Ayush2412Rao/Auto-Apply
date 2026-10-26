import json
import scrapy
from backend.app.discovery.scrapers.items import JobPostItem

class RemoteJobsSpider(scrapy.Spider):
    name = "remote_jobs"
    allowed_domains = ["jobicy.com", "remotive.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
    }

    def __init__(self, queries: str = "software engineer,ai engineer,python,data engineer",
                 max_items: str = "30", **kwargs):
        super().__init__(**kwargs)
        self.queries = [q.strip().lower() for q in queries.split(",") if q.strip()]
        self.max_items = int(max_items)
        self.yielded_count = 0

        urls = []
        # 1. Jobicy tags
        tags = ["dev", "engineering", "data-science", "python"]
        for tag in tags:
            urls.append(f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={tag}")

        # 2. Remotive search queries
        for q in self.queries:
            clean_q = q.replace(" ", "%20")
            urls.append(f"https://remotive.com/api/remote-jobs?search={clean_q}&limit=25")

        self.start_urls = urls

    def parse(self, response):
        if self.yielded_count >= self.max_items:
            return

        try:
            data = json.loads(response.text)
        except Exception:
            return

        if "jobicy.com" in response.url:
            yield from self._parse_jobicy(data, response)
        else:
            yield from self._parse_remotive(data, response)

    def _parse_jobicy(self, data, response):
        jobs = data.get("jobs", [])
        for j in jobs:
            if self.yielded_count >= self.max_items:
                break

            title = j.get("jobTitle") or "Software Engineer"
            title_lower = title.lower()
            if self.queries and not any(q in title_lower or any(word in title_lower for word in q.split()) for q in self.queries):
                continue

            company = j.get("companyName") or "Unknown"
            geo = j.get("jobGeo") or "Remote / Anywhere"
            desc = j.get("jobDescription") or ""
            url = j.get("url") or ""

            salary_min = j.get("annualSalaryMin")
            salary_max = j.get("annualSalaryMax")
            currency = j.get("salaryCurrency") or "USD"
            salary_str = None
            if salary_min and salary_max:
                salary_str = f"{salary_min} - {salary_max} {currency}"
            elif salary_min:
                salary_str = f"{salary_min} {currency}"

            item = JobPostItem()
            item["title"] = title
            item["company"] = company
            item["location"] = f"Remote ({geo})"
            item["description"] = desc
            item["url"] = url
            item["salary"] = salary_str
            item["experience"] = "1-3 yrs"
            item["skills"] = ", ".join(j.get("jobIndustry") or ["Engineering"])
            item["is_remote"] = True
            item["source"] = "jobicy"
            item["posted_at"] = j.get("pubDate")

            self.yielded_count += 1
            yield item

    def _parse_remotive(self, data, response):
        jobs = data.get("jobs", [])
        for j in jobs:
            if self.yielded_count >= self.max_items:
                break

            title = j.get("title") or "Software Engineer"
            company = j.get("company_name") or "Unknown"
            location = j.get("candidate_required_location") or "Worldwide / Remote"
            desc = j.get("description") or ""
            url = j.get("url") or ""
            salary = j.get("salary") or None
            tags = j.get("tags") or []

            item = JobPostItem()
            item["title"] = title
            item["company"] = company
            item["location"] = location
            item["description"] = desc
            item["url"] = url
            item["salary"] = salary
            item["experience"] = "1-3 yrs"
            item["skills"] = ", ".join(tags)
            item["is_remote"] = True
            item["source"] = "remotive"
            item["posted_at"] = j.get("publication_date")

            self.yielded_count += 1
            yield item
