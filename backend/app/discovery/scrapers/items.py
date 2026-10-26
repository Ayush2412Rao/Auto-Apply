import scrapy

class JobPostItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    salary = scrapy.Field()
    experience = scrapy.Field()
    skills = scrapy.Field()
    is_remote = scrapy.Field()
    source = scrapy.Field()
    posted_at = scrapy.Field()
