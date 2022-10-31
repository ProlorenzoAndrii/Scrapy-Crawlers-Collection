# -*- coding: utf-8 -*-
"""
    Main task is to scrape user profiles
    Second task is to save it in Excel
"""

import datetime
import json
import scrapy


class WeFunderComSpider(scrapy.Spider):
    name = 'wefunder_com'
    allowed_domains = ['wefunder.com']
    start_urls = ["https://wefunder.com/sitemap"]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    custom_settings = {
        "DOWNLOAD_DELAY": 0.2,
        'FEEDS': {
            f'./../results/{name}_{timestamp}.xlsx': {
                'format': 'xlsx',
                'encoding': 'utf8',
                'indent': 4,
                'item_export_kwargs': {
                    'export_empty_fields': True,
                },
            },
        },
    }

    def start_requests(self):
        sorting = ['trending', 'funding_amount_past_week']  # Add other sorting types
        for v in sorting:
            url = "https://wefunder.com/-/companies/explore?index=Company_sorted_by_{v}_desc&tagFilters=[]&hitsPerPage=6541&page=0&filters=".format(v=v)  # returns 1000 results at 1 filter
            headers = {
                'authority': 'wefunder.com',
                'accept': 'application/json, text/plain, */*',
                'referer': 'https://wefunder.com/explore',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'x-csrf-token': 'LrtRNjep0s1yjswvhxljDKyzwy/8mkHB6jY3xBodgvSQ7TcV3eR+yQy/QIzITyScrs8h9RsNUmkubIBpTRaSDA==',
                'x-newrelic-id': 'VQMOVldVGwQIU1BbBA==',
                'x-requested-with': 'XMLHttpRequest'
            }
            yield scrapy.Request(url, headers=headers, callback=self.parse_json)

    # Another way to get profiles, but seems sitemap are little old

    # def parse(self, response):
    #     links = re.findall(r"<loc>(.*?)</loc>", response.body.decode('UTF-8'), re.DOTALL)
    #     extensionsToCheck = ['updates', 'ask', 'buzz', 'about']
    #     for link in links:
    #         if any(ext in link for ext in extensionsToCheck):
    #             continue
    #         yield scrapy.Request(url=link, callback=self.parse_profile)

    def parse_json(self, response):
        js_data = response.json()
        for profile in js_data['companies']:
            url = profile.get("url")
            yield scrapy.Request(f'https://wefunder.com/{url}', callback=self.parse_company)

    def parse_company(self, response):
        team_members = response.xpath("//div[@data-react-class='company_profile/wf_team_bio/wf_team_bio']/@data-react-props").getall()
        for team_member in team_members:
            team_json = json.loads(team_member)
            userName = team_json.get("userName")
            if userName:
                yield scrapy.Request(f'https://wefunder.com/{userName}', callback=self.parse_profile)

    def parse_profile(self, response):
        if response.xpath("//html[@controller='users']"):
            first_name = response.xpath("//div[@class='fix-user-sidebar']//h1/text()").get()
            last_name = response.xpath("//div[@class='fix-user-sidebar']//h2/text()").get()
            linkedin_url = response.xpath("//a[@rel='me']/@href").get()
            location = ''.join(response.xpath("//div[@class='location']/text()").getall()).strip()

            yield {
                'WeFunder Profile URL': response.url,
                'Full name': ' '.join(list(filter(None, [first_name, last_name]))),
                'Location': location,
                'LinkedIn URL': linkedin_url
            }
