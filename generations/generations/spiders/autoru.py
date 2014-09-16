# coding=utf8

import os
import re

import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from generations.items import GenerationsItem


def removeNonAsciiFromYears(s):
    # return "".join(filter(lambda x: ord(x) < 128, s))
    ret = []
    for i in s:
        if ord(i) > 128 or i == '.':
            i = ' '
        ret.append(i)
    return "".join(ret)


class AutoruSpider(scrapy.Spider):
    name = "autoru"
    allowed_domains = ["omsk.auto.ru"]

    def __init__(self, make=None, *args, **kwargs):
        super(AutoruSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://omsk.auto.ru/cars/%s/' % make]
        self.output_path = 'output/%s/' % make
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def parse(self, response):
        models = set()
        regex = re.compile("/cars/([\w.]+)/([\w.]+)/")
        for el in regex.findall(response.body):
            models.add('http://omsk.auto.ru/cars/%s/%s/' % el)

        # for link in models:
        #     yield Request(link, self.parse_item)
        yield Request('http://omsk.auto.ru/cars/chevrolet/malibu/', self.parse_item)

    def parse_item(self, response):
        parts = response.url.split("/")
        model = parts[-2]
        if model in (
            'group-sedan', 'group-compactvan', 'group-coupe', 'group-hatchback_3d', 'group-hatchback_5d',
            'group-minivan', 'group-offroad_5d', 'group-pickup_2dr', 'group-sedan', 'group-wagon_5'
        ):
            model = parts[-3]
        elif model in ('all', 'add'):
            return

        filename = self.output_path + model + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        hxs = Selector(response)
        self.process_page(hxs)

    def process_page(self, hxs):
        generations = hxs.xpath("//div[@class='showcase-generation']")
        items = []
        for generation in generations:
            item = self.process_generation(generation)
            items.append(item)

        # for item in items:
        #     yield item

    def process_generation(self, hxs):
        item = GenerationsItem()
        name = hxs.xpath("h3[@class='showcase-generation-title']/a/text()").extract()[0].strip()
        years = removeNonAsciiFromYears(hxs.xpath("h3[@class='showcase-generation-title']/a/span/text()").extract()[0]).strip().split('   ')
        bodies = hxs.xpath("ul[@class='clearfix']/li[@class='showcase-modify showcase-modify_hide-price']")
        for body in bodies:
            body_name = body.xpath("strong/a/text()").extract()[0]
            body_image = body.xpath("div/a/img[@class='showcase-modify-pic']/@src").extract()[0]
            self.log('body_name = "%s"' % body_name)
            self.log('body_image = "%s"' % body_image)
        try:
            start, end = years
        except ValueError:
            start = years[0]
            end = '2015'

        # self.log('name = "%s"' % name)
        # self.log('years = "%s"' % unicode(years))
        # self.log('start = "%s", end = "%s"' % (start, end))
        item["name"] = name
        item["start"] = start
        item["end"] = end

        # item["link"] = hxs.select("div[@class='bodytext']/h2/a/@href").extract()
        # item["content"] = hxs.select("div[@class='bodytext']/p/text()").extract()
        return item