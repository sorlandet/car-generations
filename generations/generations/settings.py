# -*- coding: utf-8 -*-

# Scrapy settings for generations project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'generations'

SPIDER_MODULES = ['generations.spiders']
NEWSPIDER_MODULE = 'generations.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'generations (+http://www.yourdomain.com)'


ITEM_PIPELINES = {
    'generations.pipelines.BodyWriterPipeline': 300
}

DATABASE = {
    'drivername': 'mysql',
    'host': '',
    'port': '3306',
    'username': 'root',
    'password': 'pswd1234',
    'database': 'generations'
}