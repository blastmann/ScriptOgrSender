import httplib
import json
import StringIO
import os
import urllib  
import urllib2
import sublime, sublime_plugin

app_key = ''
user_id = ''
posturl = 'http://scriptogr.am/api/article/post/'
delurl = 'http://scriptogr.am/api/article/delete/'
proxy_server = ''
proxy = urllib2.ProxyHandler(proxies = {'http' : ''})
data = {'app_key':app_key, 'user_id': user_id, 'name':'foo.md', 'text':'foo'}  

class PostScrCommand(sublime_plugin.TextCommand):
	def post(url, data):  
	    # data = urllib.urlencode(data)
	    opener = urllib2.build_opener(proxy)
	    response = opener.open(url, data)  
	    return response.read()

	def run(self, edit):
		io = StringIO.StringIO(post(url, data))
		rep = json.load(io)
		print rep

class DelPostScrCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print 'deleted'
		