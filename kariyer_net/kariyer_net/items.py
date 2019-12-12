# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KariyerNetItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    experience = scrapy.Field()
    military_obligation = scrapy.Field()
    education = scrapy.Field()
    industry = scrapy.Field()
    department = scrapy.Field()
    job_type = scrapy.Field() #part-time full-time
    position = scrapy.Field()
    personel_count = scrapy.Field()
    application_count = scrapy.Field()

