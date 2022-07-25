# -*- coding: utf-8 -*-
import re
import scrapy


class ClutchCoSpider(scrapy.Spider):
    name = "clutch_co"
    allowed_domains = ["clutch.co"]
    start_urls = ["https://clutch.co/sitemap.xml"]

    def parse(self, response, **kwargs):
        sitemaps = re.findall('<loc>(https:\/\/.+?)<\/loc>', response.text)
        for sitemap in sitemaps:
            yield scrapy.Request(url=sitemap, callback=self.parse_sub_sitemap)

    def parse_sub_sitemap(self, response):
        profiles = re.findall('<loc>(https:\/\/.+?)<\/loc>', response.text)
        for profile in profiles:
            if 'https://clutch.co/profile/' in profile:
                yield scrapy.Request(url=profile, callback=self.parse_profile)

    def parse_profile(self, response):
        name = response.xpath("normalize-space(//h1[contains (@class, 'header-company')]/a/text())").get()
        phone = response.xpath("normalize-space(//a[@class='contact phone_icon']/text())") .get("")
        website = response.xpath("//li[@class='website-link-a']/a/@href").get("").split("?utm_source", 1)[0]
        if not website:  # Skipping companies without website urls
            return
        description = ' '.join(response.xpath("//div[@class='field-name-profile-summary']/p/text()").getall()).strip()
        employees = response.xpath("//div[@data-content='<i>Employees</i>']/span/text()").get()
        founded = response.xpath("//div[@data-content='<i>Founded</i>']/span/text()").get("")
        address = response.xpath("normalize-space(//span[@class='location-name']/text())").get()
        logo = response.xpath("//img[@class='header-company--logotype']/@src").get()

        yield {
            'name': name,
            'phone': phone,
            'website': website,
            'description': description,
            'employees': employees,
            'founded': founded,
            'address': address,
            'logo': logo
        }

