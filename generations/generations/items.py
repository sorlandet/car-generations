# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BodyItem(scrapy.Item):
    # define the fields for your item here like:
    page_url = scrapy.Field()

    make = scrapy.Field()
    model = scrapy.Field()
    generation = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    body_name = scrapy.Field()
    body_image = scrapy.Field()
