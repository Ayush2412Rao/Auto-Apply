import json
import urllib.parse
import scrapy
from backend.app.discovery.scrapers.items import JobPostItem

class HiristSpider(scrapy.Spider):
    """Scrapy Spider for Hirist.tech - India's premium tech and engineering job portal."""
    name = "hirist"
    allowed_domains = ["hirist.tech", "www.hirist.tech", "hirist.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    }

    def __init__(self, queries: str = "python,ai,data engineer,software engineer",
                 locations: str = "Noida,Gurgaon,Bangalore,Delhi,Remote",
                 experience: str = "1",
                 max_items: str = "25", **kwargs):
        super().__init__(**kwargs)
        self.queries = [q.strip() for q in queries.split(",") if q.strip()]
        self.locations = [l.strip() for l in locations.split(",") if l.strip()]
        self.experience = str(experience)
        self.max_items = int(max_items)
        self.yielded_count = 0

        # Construct start URLs for tech searches
        urls = []
        for q in self.queries:
            encoded_q = urllib.parse.quote(q)
            # Hirist search endpoint
            urls.append(f"https://www.hirist.tech/c/{encoded_q}-jobs.html?exp={self.experience}")
            urls.append(f"https://www.hirist.tech/search?query={encoded_q}")
        self.start_urls = urls[:6]

    def parse(self, response):
        if self.yielded_count >= self.max_items:
            return

        # Check for HTML cards
        cards = response.css(".job-card, .job-item, .card-body, article.job, div[data-job-id]")
        if cards:
            for card in cards:
                if self.yielded_count >= self.max_items:
                    break

                title = card.css(".job-title::text, h2 a::text, h3 a::text, .title::text").get()
                if not title:
                    continue
                title = title.strip()

                company = card.css(".company-name::text, .recruiter-name::text, span.company::text").get() or "Top Tech Employer"
                company = company.strip()

                loc = card.css(".location::text, span.location::text, .loc::text").get() or "India"
                loc = loc.strip()

                exp = card.css(".experience::text, .exp::text, span.exp::text").get() or f"{self.experience} yrs"
                exp = exp.strip()

                rel_url = card.css("a::attr(href)").get() or ""
                full_url = response.urljoin(rel_url) if rel_url else response.url

                skills_list = card.css(".skills span::text, .tags span::text").getall()
                skills_str = ", ".join(s.strip() for s in skills_list if s.strip())

                item = JobPostItem()
                item["title"] = title
                item["company"] = company
                item["location"] = loc
                item["description"] = (
                    f"Hirist Tech Engineering Role: {title} at {company}.\n"
                    f"Location: {loc} | Experience: {exp}.\n"
                    f"Skills: {skills_str or 'Python, Backend, Cloud Systems'}."
                )
                item["url"] = full_url
                item["salary"] = None
                item["experience"] = exp
                item["skills"] = skills_str or "Python, Cloud, AI"
                item["is_remote"] = "remote" in loc.lower()
                item["source"] = "hirist"
                item["posted_at"] = None

                self.yielded_count += 1
                yield item

        # Also check for embedded JSON-LD or Next.js / React state
        next_data = response.css("script#__NEXT_DATA__::text").get()
        if next_data and self.yielded_count < self.max_items:
            try:
                state = json.loads(next_data)
                jobs = state.get("props", {}).get("pageProps", {}).get("jobs", [])
                for j in jobs:
                    if self.yielded_count >= self.max_items:
                        break
                    title = j.get("title") or "Software Engineer"
                    company = j.get("companyName") or "Tech Company"
                    loc = j.get("location") or "India"
                    url = j.get("jobUrl") or response.url

                    item = JobPostItem()
                    item["title"] = title
                    item["company"] = company
                    item["location"] = loc
                    item["description"] = f"Opportunity for {title} at {company}."
                    item["url"] = url
                    item["salary"] = j.get("salary")
                    item["experience"] = f"{self.experience} yrs"
                    item["skills"] = j.get("skills", "")
                    item["is_remote"] = "remote" in loc.lower()
                    item["source"] = "hirist"
                    item["posted_at"] = j.get("postedDate")

                    self.yielded_count += 1
                    yield item
            except Exception:
                pass
