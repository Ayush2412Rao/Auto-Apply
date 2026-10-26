# Scrapy settings for auto_apply_scrapers project

BOT_NAME = "auto_apply_scrapers"

SPIDER_MODULES = ["backend.app.discovery.scrapers.spiders"]
NEWSPIDER_MODULE = "backend.app.discovery.scrapers.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure download delay
DOWNLOAD_DELAY = 0.5
DOWNLOAD_DELAY_JITTER = 0.5

# Download timeout
DOWNLOAD_TIMEOUT = 15

# Cookies
COOKIES_ENABLED = True

# Default request headers to emulate standard browser requests
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
}

# Clean logging level
LOG_LEVEL = "WARNING"
FEED_EXPORT_ENCODING = "utf-8"
