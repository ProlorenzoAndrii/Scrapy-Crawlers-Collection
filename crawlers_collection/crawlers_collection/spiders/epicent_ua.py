# -*- coding: utf-8 -*-
import json
import re
import scrapy
from parsel import Selector


class EpicentrSpider(scrapy.Spider):
    name = "epicentr_ua"
    allowed_domains = ["epicentrk.ua"]
    start_urls = ["https://epicentrk.ua/"]

    api_url = "https://epicentrk.ua/ajax/listing/list.php"

    def start_requests(self):
        payload = json.dumps({"location": "/ua/shop/unitazy-i-kompakty/",
                              "lang": "ua",
                              "sectionId": "974",
                              "merchantId": "974",
                              "preload": "true",
                              "sort": "rating",
                              "page": "1"})

        yield scrapy.Request(self.api_url, method="POST", body=payload)

    def parse(self, response, **kwargs):
        js_data = response.json()
        category_name = js_data['h1']
        next_page = js_data['pagination']['next']['name']
        products = js_data['products']
        resp = Selector(text=products)
        for prod in resp.xpath("//a[@class='card__photo']/@href").getall():
            yield scrapy.Request(url=prod,
                                 callback=self.parse_product,
                                 priority=10)

        payload = json.dumps({"location": "/ua/shop/unitazy-i-kompakty/",
                              "lang": "ua",
                              "sectionId": "974",
                              "merchantId": "974",
                              "preload": "true",
                              "sort": "rating",
                              "page": next_page})

        yield scrapy.Request(self.api_url,
                             method="POST",
                             body=payload,
                             callback=self.parse)

    def parse_product(self, response):
        name = response.xpath("//h1[@class='p-header__title nc']/text()").get()
        price = response.xpath("//div[@class='p-price__main']/@title").get()

        yield {
            "name": name,
            "price": price
        }
