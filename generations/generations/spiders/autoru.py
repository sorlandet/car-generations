# coding=utf8

import os
import re

import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector

from generations.items import BodyItem


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

        for link in models:
            yield Request(link, self.parse_item)
        # yield Request('http://omsk.auto.ru/cars/chevrolet/malibu/', self.parse_item)

    def parse_item(self, response):
        self.page_url = response.url
        # self.log('page_url = "%s"' % self.page_url)
        parts = response.url.split("/")
        model = parts[-2]

        wrong = (
            'group-sedan', 'group-compactvan', 'group-coupe', 'group-hatchback_3d', 'group-hatchback_5d',
            'group-minivan', 'group-offroad_5d', 'group-pickup_2dr', 'group-sedan', 'group-wagon_5'
        )

        if model in wrong:
            model = parts[-3]

        if model in ('all', 'add'):
            model = None

        if model:
            filename = self.output_path + model + '.html'
            with open(filename, 'wb') as f:
                f.write(response.body)

            hxs = Selector(response)
            # self.log('start')
            for el in self.process_page(hxs):
                yield el
            # self.log('finish')

    def process_page(self, hxs):
        title = hxs.xpath('//title')
        self.page_title = title.extract()[0].replace('<title>', '').replace('</title>', '')
        # self.log('page_title = "%s"' % self.page_title)

        generations = hxs.xpath("//div[@class='showcase-generation']")
        items = []

        for generation in generations:
            bodies = self.process_generation(generation)
            for body in bodies:
                items.append(body)

        # self.log('bodies found: "%s"' % len(items))

        return items

    def process_generation(self, hxs):
        ret = []
        car = self.page_title[10:].split(':')[0]
        make, model = car.split(' ', 1)
        value = hxs.xpath("h3[@class='showcase-generation-title']/a/text()").extract()[0].strip()
        generation = value.replace(car, '').strip()
        # self.log('value = "%s"' % value)
        # self.log('generation = "%s"' % generation)
        years = removeNonAsciiFromYears(hxs.xpath("h3[@class='showcase-generation-title']/a/span/text()").extract()[0]).strip().split('   ')

        try:
            start, end = years
        except ValueError:
            start = years[0]
            end = ''
        # self.log('years = "%s"' % unicode(years))
        # self.log('start = "%s", end = "%s"' % (start, end))
        # item["link"] = hxs.select("div[@class='bodytext']/h2/a/@href").extract()
        # item["content"] = hxs.select("div[@class='bodytext']/p/text()").extract()

        bodies = hxs.xpath("ul[@class='clearfix']/li[@class='showcase-modify showcase-modify_hide-price']")
        for body in bodies:

            body_name = body.xpath("strong/a/text()").extract()[0]
            body_image = body.xpath("div/a/img[@class='showcase-modify-pic']/@src").extract()[0]
            # self.log('body_name = "%s"' % body_name)
            # self.log('body_image = "%s"' % body_image)

            item = BodyItem()
            item["page_url"] = self.page_url
            item["page_title"] = self.page_title
            item["make"] = make
            item["model"] = model
            item["generation"] = generation
            item["start"] = start
            item["end"] = end
            item["body_name"] = body_name
            item["body_image"] = body_image

            ret.append(item)

        return ret