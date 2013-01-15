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

# Operations definitions
do_upload = {'app_key':app_key, 'user_id': user_id, 'name':'foo.md', 'text':'foo'}  
do_delete = {'app_key':app_key, 'user_id': user_id, 'filename':'foomd.md'}

def handle_threads():
	return

class PostScrCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		io = StringIO.StringIO(self.uppost(posturl, do_upload))
		rep = json.load(io)
		print rep

	def uppost(self, url, data):  
	    upload_post = urllib.urlencode(data)
	    opener = urllib2.build_opener(proxy)
	    response = opener.open(url, upload_post)
	    return response.read()

class DelPostScrCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		io = StringIO.StringIO(self.delpost(delurl, do_delete))
		rep = json.load(io)
		print rep

	def delpost(self, url, data):
		delete_post = urllib.urlencode(data)
		opener = urllib2.build_opener()
		response = opener.open(url, delete_post)
		return response.read()
		