# -*- coding: utf-8 -*-
import scrapy

from urllib.parse import parse_qsl, urlparse


class KickstarterSpider(scrapy.Spider):
    name = "kickstarter"
    allowed_domains = ["www.kickstarter.com"]
    start_urls = ["https://www.kickstarter.com"]

    api_url = "https://www.kickstarter.com/discover/advanced?google_chrome_workaround&sort=popularity&ref=discovery_overlay&seed=2778165&page={page}"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'crawlers_collection.middlewares.CloudFlareBypassMiddleware': 900,
        },
    }

    headers = {
        'authority': 'www.kickstarter.com',
        'accept': 'application/json, text/javascript',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.api_url.format(page='1'), headers=self.headers)

    def parse(self, response, **kwargs):
        js_data = response.json()
        for project in js_data['projects']:
            name = project['name']
            blurb = project['blurb']
            country = project['country']
            goal = project['goal']

            yield {
                'name': name,
                'blurb': blurb,
                'country': country,
                'goal': goal
            }

        if js_data.get('has_more'):
            parsed = urlparse(response.url)
            current_page = dict(parse_qsl(parsed.query)).get("page")
            yield scrapy.Request(url=self.api_url.format(page=int(current_page)+1),
                                 headers=self.headers,
                                 callback=self.parse)
