# -*- coding: utf-8 -*-
import math
import scrapy
import urllib.parse


class FfxCoUkSpider(scrapy.Spider):
    name = "ffx_co_uk"
    allowed_domains = ["ffx.co.uk"]
    start_urls = ["https://ffx.co.uk/Search/Refine/_STCKO=0"]

    unique_urls = set()

    def parse(self, response, **kwargs):
        categories = response.xpath("//div[@id='refineCategories']//input/@value").getall()
        for category in categories:
            yield scrapy.Request(
                url=f"https://ffx.co.uk/Search/Refine/_STCKO=0_C={urllib.parse.quote(category, safe=',')}_S=1",
                callback=self.parse_brands,
                meta={'category': category}
                )

    def parse_brands(self, response):
        brands = response.xpath("//div[@id='refineBrands']//input/@value").getall()
        for brand in brands:
            yield scrapy.Request(
                url=f"https://ffx.co.uk/Search/Refine/_STCKO=0_C={urllib.parse.quote(response.meta.get('category'), safe=',')}_B={urllib.parse.quote(brand, safe=',')}_S=1",
                callback=self.pagination,
                meta={'category': response.meta.get('category'),
                      'brand': brand}
                )

    def pagination(self, response):
        total_products = response.xpath("//span[@id='TotalProductsCount']/text()").get()
        if total_products and int(total_products) > 48:
            for page in range(0, math.ceil(int(total_products) / 48)):
                url = "https://ffx.co.uk/Search/InfiniteScroll?id=_STCKO=0_C={category}_B={brand}_S=1&page={page}".format(
                    category=urllib.parse.quote(response.meta['category'], safe=','),
                    brand=urllib.parse.quote(response.meta['brand'], safe=','),
                    page=page
                )
                yield scrapy.Request(url=url,
                                     callback=self.parse_products,
                                     meta={'category': response.meta.get('category'),
                                           'brand': response.meta.get('brand')}
                                     )
        else:
            yield self.parse_products(response)

    def parse_products(self, response):
        products = response.xpath("//div[@class='product-grid']/a/@href").getall()
        for product in products:
            self.unique_urls.add(response.urljoin(product))

        print("Founded urls:", len(self.unique_urls))
