# -*- coding=utf8 -*-
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log

from news.items import NewsItem

class NewsSpider(CrawlSpider):
    name = 'sinanews'
    allowed_domains=['sina.com.cn']
    start_urls = ['http://roll.news.sina.com.cn/s/channel.php?ch=01#col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page=1']
    
    rules = [Rule(LinkExtractor(allow = '/.+/\d+.shtml', deny = '/171826152112.shtml'), 'parse_news'),
             Rule(LinkExtractor(restrict_xpaths = u"//a[@title='下一页']"), callback = 'parse_next')]

    def parse_news(self, response):
        news = NewsItem()

        news['url'] = response.url

        temp = response.xpath("//h1[@id='artibodyTitle']//text()").extract()
        news['title'] = temp[0] if temp else ''

        temp = response.xpath("//span[@id='media_name']//a//text()").extract()
        news['source'] = temp[0] if temp else ''
        if news['source'] == '':
            temp = response.xpath("//span[@data-sudaclick='media_name']//a//text()").extract()
            news['source'] = temp[0] if temp else ''

        temp =  response.xpath("//span[@id='pub_date']//text()").extract()
        news['public_time'] = temp[0] if temp else ''
        if news['public_time'] == '':
            temp =  response.xpath("//span[@class='time-source']//text()").extract()
            news['public_time'] = temp[0] if temp else ''

        temp = response.xpath("//div[@id='artibody']//p//text()").extract()
        news['content'] = '\n'.join(temp) if temp else ''

        cat = response.url.split('//')[1].split('.')[0]
        sub_cat = response.url.split('//')[1].split('/')[1]
        if cat == 'tech':
            news['category'] = '科技'
        elif cat == 'mil':
            news['category'] = '军事'
        elif cat == 'finance':
            news['category'] = '财经'
        elif cat == ['sports']:
            news['category'] = '体育'
        elif cat == 'ent':
            news['category'] = '娱乐'
        elif cat == 'news':
            if sub_cat == 's':
                news['category'] = '国内'
            elif sub_cat == 'w':
                news['category'] = '国际'
            elif sub_cat == 's':
                news['category'] = '社会'
            else:
                news['category'] = '其他'
        else:
            news['category'] = ''

        log.msg(': '.join([response.url, news['title']]), level=log.INFO)

        return news

    def parse_next(self, response):
        log.msg(response.url)
        return self.make_requests_from_url(response.url)
