import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cajamar.items import Article


class CajamarSpider(scrapy.Spider):
    name = 'cajamar'
    start_urls = ['https://compromisosocial.es/blog/']

    def parse(self, response):
        links = response.xpath('//a[@class="entire-meta-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="meta-date date updated"]/text()').get() or \
               response.xpath('//span[@class="meta-date date published"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="content-inner"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
