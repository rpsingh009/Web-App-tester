from django.shortcuts import render
import requests,json
from django import template
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.item import Item, Field
import os
from django.contrib.auth.models import User
import scrapy
from scrapy.crawler import CrawlerProcess
# Create your views here.
import subprocess
import os 
from django.contrib.auth import login as auth_login
from django.contrib.auth import login, authenticate, logout
from random import randint
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
register = template.Library()


def index(request):
	return render(request,'search.html')

def login(request):
	if not request.user.is_authenticated:
		if request.method == 'POST':

			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(request, username=username, password=password)
			if user:
				auth_login(request,user)
				return render(request, 'search.html')         
	return render(request, 'login.html')
def signup(request):
	if not request.user.is_authenticated:
		if request.method == 'POST':
			
			username = request.POST['username']
			first_name = request.POST['fname']
			last_name = request.POST['lname']
			email = request.POST['email']
			password=request.POST['password']
			user_obj=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password)
			user_obj.save()

			auth_login(request, user_obj)
			return render(request,'search.html')
		context=dict()
		auser=User.objects.all()
		context['auser']=auser
		return render(request,'login.html',context)
	return render(request,'search.html')
def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def validate(request):
	if request.method=='POST':
		if request.user.is_authenticated:
			requested_url=request.POST.get('url')
			#requested_url='http://rinkworks.com/slapdash/broken.shtml'#'w3schools.com'
			payload = {'uri': requested_url,'output':'json'}
			r=requests.get('http://validator.w3.org/check',payload)
			context=dict(r.json())
			r2=requests.get('http://jigsaw.w3.org/css-validator/validator',payload)

			if 'http' not in requested_url:
				link='http://'+requested_url
			else:
				link=requested_url

			#link='http://rinkworks.com/slapdash/broken.shtml'
			try:
				os.remove("media/master/master_link.txt")
			except OSError:
				pass
			f = open("media/master/master_link.txt", "w")
			val=randint(1000,9999)
			f.write("{0}_media/links/{1}.csv".format(link,str(val)))
			f.close()
			context['links']="/media/links/{0}.csv".format(str(val))
			#context['loop_cycle']=range(0,10)
			if 'errors' in dict(r2.json())['cssvalidation']:
				context['css_error']=dict(r2.json())['cssvalidation']['errors']
				context['css_source']=dict(r2.json())['cssvalidation']['errors'][0]['source']
			context['qlink']=link
			request.session['val_data']=context

			return render(request,'validate_new.html',context)
		else: 
			return HttpResponseRedirect(reverse('login'))


def validate_1(request):
	
	context=request.session['val_data'] #"media/links/{0}.csv".format(str(val))
	return render(request,'validate.html',context)


class MyItems(Item):
	referer =Field() # where the link is extracted
	response= Field() # url that was requested
	status = Field() # status code received


class MySpider(CrawlSpider):
	name = "test-crawler"
	target_domains = ["rinkworks.com/slapdash/broken.shtml"] # list of domains that will be allowed to be crawled
	start_urls = ["http://rinkworks.com/slapdash/broken.shtml"] # list of starting urls for the crawler
	handle_httpstatus_list = [404,410,301,500] # only 200 by default. you can add more status to list

	# Throttle crawl speed to prevent hitting site too hard
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
	  # list of response codes that we want to include on the report, we know that 404
	  report_if = [404,500,410,301] 
	  if response.status in report_if: # if the response matches then creates a MyItem
		  item = MyItems()
		  item['referer'] = response.request.headers.get('Referer', None)
		  item['status'] = response.status
		  item['response']= response.url
		  yield item
	  yield None # if the response did not match return empty