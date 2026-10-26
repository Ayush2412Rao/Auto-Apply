import json
import urllib.parse
import scrapy
from backend.app.discovery.scrapers.items import JobPostItem

class InstahyreSpider(scrapy.Spider):
    name = "instahyre"
    allowed_domains = ["instahyre.com", "www.instahyre.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    }

    def __init__(self, queries: str = "Software Engineer,AI Engineer,Python,Data Engineer",
                 locations: str = "Noida,Gurgaon,Delhi,Bangalore,Remote",
                 experience: str = "1",
                 max_items: str = "30", **kwargs):
        super().__init__(**kwargs)
        self.queries = [q.strip() for q in queries.split(",") if q.strip()]
        self.locations = [l.strip() for l in locations.split(",") if l.strip()]
        self.experience = str(experience)
        self.max_items = int(max_items)
        self.yielded_count = 0

        urls = []
        for query in self.queries:
            for loc in self.locations:
                encoded_q = urllib.parse.quote(query)
                encoded_loc = urllib.parse.quote(loc)
                urls.append(
                    f"https://www.instahyre.com/api/v1/job_search"
                    f"?skills={encoded_q}&location={encoded_loc}"
                    f"&years_of_experience={self.experience}&job_type=0"
                )
        self.start_urls = urls

    def parse(self, response):
        if self.yielded_count >= self.max_items:
            return

        try:
            data = json.loads(response.text)
        except Exception:
            return

        objects = data.get("objects", [])
        for obj in objects:
            if self.yielded_count >= self.max_items:
                break

            title = obj.get("title") or obj.get("candidate_title") or "Software Engineer"
            employer_obj = obj.get("employer") or {}
            company = employer_obj.get("company_name") or "Unknown"
            raw_locations = obj.get("locations") or "India"
            
            if isinstance(raw_locations, list):
                loc_str = ", ".join(str(l) for l in raw_locations)
            else:
                loc_str = str(raw_locations)

            keywords = obj.get("keywords") or []
            skills_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

            public_url = obj.get("public_url")
            if not public_url:
                job_id = obj.get("id")
                public_url = f"https://www.instahyre.com/job-{job_id}/" if job_id else "https://www.instahyre.com"

            is_remote = bool(
                "remote" in loc_str.lower() or 
                "work from home" in loc_str.lower() or 
                obj.get("accept_outstation", False)
            )

            desc_lines = [
                f"Position: {title}",
                f"Company: {company}",
                f"Location: {loc_str}",
                f"Experience required: {self.experience} years",
            ]
            if skills_str:
                desc_lines.append(f"Required Skills & Competencies: {skills_str}")
            desc_lines.append(
                f"Role Summary: Opportunity for {title} at {company} based in {loc_str}. "
                f"Seeking skilled candidates with expertise in {skills_str or 'modern software development'}."
            )

            item = JobPostItem()
            item["title"] = title
            item["company"] = company
            item["location"] = loc_str
            item["description"] = "\n\n".join(desc_lines)
            item["url"] = public_url
            item["salary"] = None
            item["experience"] = f"{self.experience} yrs"
            item["skills"] = skills_str
            item["is_remote"] = is_remote
            item["source"] = "instahyre"
            item["posted_at"] = obj.get("reviewed_at")

            self.yielded_count += 1
            yield item
