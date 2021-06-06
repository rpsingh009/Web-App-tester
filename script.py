from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.item import Item, Field
import os
from scrapyscript import Job, Processor
import scrapy
from scrapy.crawler import CrawlerProcess
import sys



print(sys.argv,'-----------------------') 
start_urls = [sys.argv[1].split('_')[0]] 
file_path=sys.argv[1].split('_')[1]
target_domains = [start_urls[0].split('//')[1]]
class MyItems(Item):
	referer =Field() # where the link is extracted
	response= Field() # url that was requested
	status = Field() # status code received


class MySpider(CrawlSpider):
	name = "test-crawler"
	start_urls=start_urls
	handle_httpstatus_list = [404,410,301,500] 

	custom_settings = {
		'CONCURRENT_REQUESTS': 2, # only 2 requests at the same time
		'DOWNLOAD_DELAY': 0.5 # delay between requests
	}

	rules = [
		Rule(
			LinkExtractor( allow_domains=target_domains, deny=('patterToBeExcluded'), unique=('Yes')), 
			callback='parse_my_url', # method that will be called for each request
			follow=True),
		# crawl external links but don't follow them
		Rule(
			LinkExtractor( allow=(''),deny=("patterToBeExcluded"),unique=('Yes')),
			callback='parse_my_url',
			follow=False
		)
	]


	def parse_my_url(self, response):
	  
	  report_if = [404,500,410] 
	  if response.status in report_if: 
		  item = MyItems()
		  item['referer'] = response.request.headers.get('Referer', None)
		  item['status'] = response.status
		  item['response']= response.url
		  yield item
	  yield None # if the response did not match return empty



def spider_results():
	

	process = CrawlerProcess({
		'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
		'FEED_FORMAT': 'csv',
		'FEED_URI': 'media/links/data.csv'
		})
	process.crawl(MySpider)
	process.start(stop_after_crawl=True)  # the script will block here until the crawling is finished

	print('------------------------------------------------------------')
	os.rename('media/links/data.csv',file_path) 
	return True



spider_results()