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
    page_url = None
    car = None
    make = None
    model = None

    def __init__(self, filename=None, *args, **kwargs):
        super(AutoruSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                url = 'http://omsk.auto.ru%s' % line.strip()
                self.start_urls.append(url)

        # self.start_urls = ['http://omsk.auto.ru/cars/%s/' % make]
        # self.output_path = 'output/%s/' % make
        # if not os.path.exists(self.output_path):
        #     os.makedirs(self.output_path)

    def parse(self, response):
        models = set()
        regex = re.compile("/cars/([\w-]+)/([\w-]+)/")
        for el in regex.findall(response.body):
            models.add('http://omsk.auto.ru/cars/%s/%s/' % el)

        for link in models:
            yield Request(link, self.parse_item)
        # yield Request('http://omsk.auto.ru/cars/chevrolet/malibu/', self.parse_item)
        # yield Request('http://omsk.auto.ru/cars/chevrolet/alero/', self.parse_item)
        # yield Request('http://omsk.auto.ru/cars/chevrolet/astra/', self.parse_item)
        # yield Request('http://omsk.auto.ru/cars/buick/enclave/', self.parse_item)

    def parse_item(self, response):
        self.page_url = response.url

        if 'auth.auto.ru' in self.page_url:
            return

        # self.log('page_url = "%s"' % self.page_url)
        parts = self.page_url.split("/")
        model = parts[-2]
        page_parse_method = 'process_generations_page'
        wrong = (
            'group-sedan', 'group-compactvan', 'group-coupe', 'group-hatchback_3d', 'group-hatchback_5d',
            'group-minivan', 'group-offroad_5d', 'group-pickup_2dr', 'group-sedan', 'group-wagon_5'
        )

        if model in wrong:
            page_parse_method = 'process_body_page'
            model = parts[-3]

        if model in ('all', 'add'):
            model = None

        if model:
            # filename = self.output_path + model + '.html'
            # with open(filename, 'wb') as f:
            #     f.write(response.body)

            hxs = Selector(response)
            for el in getattr(self, page_parse_method)(hxs):
                yield el

    def process_body_page(self, hxs):
        # <ul class="breadcrumbs-w">
        #   <li class="breadcrumbs-i">
        #     <a href="/cars/chevrolet/" class="breadcrumbs-l">Chevrolet</a>
        #     <span class="breadcrumbs-level"></span>
        #   </li>
        #   <li class="breadcrumbs-i">
        #     <span class="breadcrumbs-l breadcrumbs-l_text">Alero</span>
        #     <span class="breadcrumbs-level"></span>
        #   </li>
        # </ul>
        # /a[@class='breadcrumbs-l']/text()
        make = hxs.xpath("//ul[@class='breadcrumbs-w']/li[@class='breadcrumbs-i']/a[@class='breadcrumbs-l']/text()").extract()[0]
        model = hxs.xpath("//ul[@class='breadcrumbs-w']/li[@class='breadcrumbs-i']/span[@class='breadcrumbs-l breadcrumbs-l_text']/text()").extract()[0]

        trs = hxs.xpath("//table[@class='showcase-list showcase-list_no-fixed']/tr")
        years = set()
        for tr in trs:
            td = tr.xpath("td[@class='showcase-list-cell showcase-list-cell_v2_releaseperiod']/text()").extract()
            for el in td:

                for year in removeNonAsciiFromYears(el).split(' '):
                    try:
                        year = int(year)
                    except ValueError:
                        year = 9999
                    years.add(year)

        parts = self.page_url.split("/")
        body_name = parts[-2].replace('group-', '')

        generation = ''
        start = min(years)
        end = max(years)
        body_image = hxs.xpath("//div[@class='modifications-list-photo']/img[@class='modifications-list-img']/@src").extract()[0]


        item = BodyItem()
        item["page_url"] = self.page_url
        item["make"] = make
        item["model"] = model
        item["generation"] = generation
        item["start"] = start
        item["end"] = end
        item["body_name"] = body_name
        item["body_image"] = body_image

        return [item]

    def process_generations_page(self, hxs):
        self.make = hxs.xpath("//ul[@class='breadcrumbs-w']/li[@class='breadcrumbs-i']/a[@class='breadcrumbs-l']/text()").extract()[0]
        self.model = hxs.xpath("//ul[@class='breadcrumbs-w']/li[@class='breadcrumbs-i']/span[@class='breadcrumbs-l breadcrumbs-l_text']/text()").extract()[0]
        self.car = '%s %s' % (self.make, self.model)
        self.log('car: %s' % self.car)

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
        try:
            value = hxs.xpath("h3[@class='showcase-generation-title']/a/text()").extract()[0].strip()
            generation = value.replace(self.car, '').strip()
            # self.log('value = "%s"' % value)
            # self.log('generation = "%s"' % generation)
            years = removeNonAsciiFromYears(hxs.xpath("h3[@class='showcase-generation-title']/a/span/text()").extract()[0]).strip().split('   ')
        except IndexError:
            value = hxs.xpath("h3[@class='showcase-generation-title']/text()").extract()[0].strip()
            generation = value.replace(self.car, '').strip()
            # self.log('value = "%s"' % value)
            # self.log('generation = "%s"' % generation)
            years = removeNonAsciiFromYears(hxs.xpath("h3[@class='showcase-generation-title']/span/text()").extract()[0]).strip().split('   ')

        try:
            start, end = years
        except ValueError:
            start = years[0]
            end = '9999'
        # self.log('years = "%s"' % unicode(years))
        # self.log('start = "%s", end = "%s"' % (start, end))
        # item["link"] = hxs.select("div[@class='bodytext']/h2/a/@href").extract()
        # item["content"] = hxs.select("div[@class='bodytext']/p/text()").extract()

        bodies = hxs.xpath("ul[@class='clearfix']/li[@class='showcase-modify showcase-modify_hide-price']")
        for body in bodies:

            body_name = body.xpath("div[@class='showcase-modify-pic-w']/a[@class='showcase-link-item']/@href").extract()[0].split('/')[-2].replace('group-', '')
            body_image = body.xpath("div/a/img[@class='showcase-modify-pic']/@src").extract()[0]
            # self.log('body_name = "%s"' % body_name)
            # self.log('body_image = "%s"' % body_image)

            item = BodyItem()
            item["page_url"] = self.page_url
            item["make"] = self.make
            item["model"] = self.model
            item["generation"] = generation
            item["start"] = start
            item["end"] = end
            item["body_name"] = body_name
            item["body_image"] = body_image

            ret.append(item)

        return ret