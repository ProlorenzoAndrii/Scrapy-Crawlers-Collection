# -*- coding: utf-8 -*-
import re
import scrapy


class FitnessOrgAuSpider(scrapy.Spider):
    name = "fitness_org_au"
    allowed_domains = ["fitness.org.au"]
    start_urls = ["https://fitness.org.au/directory/business/2"]

    def parse(self, response, **kwargs):
        urls = response.xpath("//div[@class='search-item']//div[@id='business-data']/a/@href").getall()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_profile)
        next_page = response.xpath("//a[@rel='next']/@href").get()
        yield scrapy.Request(response.urljoin(next_page), callback=self.parse) if next_page else None


    def parse_profile(self, response):
        title = response.xpath("//h1/text()").get()
        loc = response.xpath("//span[@class='location']/a/text()").get()
        phone = response.xpath("//dt[contains (text(), 'Phone number: ')]/following-sibling::dd/text()").get()
        website = response.xpath("//a[@target='_new']/@href").get()
        yield {
            'title': title.strip() if title else None,
            'location': loc if loc else None,
            'website': website if website else None,
            'phone': phone.strip() if phone else None,
            'url': response.url
        }

