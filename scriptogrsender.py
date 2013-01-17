import httplib
import json
import StringIO
import os
import urllib
import urllib2
import threading
import re
import sublime
import sublime_plugin

app_key = ''
user_id = ''
base_url = 'http://scriptogr.am/api/article/'
posturl = 'http://scriptogr.am/api/article/post/'
delurl = 'http://scriptogr.am/api/article/delete/'
proxy_server = ''
proxy = urllib2.ProxyHandler(proxies={'http': ''})

# Operations definitions
base_opr = {'app_key': app_key, 'user_id': user_id}
do_upload = {'app_key': app_key, 'user_id': user_id, 'name': 'foo.md', 'text': 'foo'}
do_delete = {'app_key': app_key, 'user_id': user_id, 'filename': 'foomd.md'}


def handle_threads(self, edit, threads):
    next_threads = []
    for thread in threads:
        if thread.is_alive():
            next_threads.append(thread)
        if thread.result == False:
            continue
    return


# Post
class PostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        io = StringIO.StringIO(self.uppost(posturl, do_upload))
        rep = json.load(io)
        print rep


# Delete
class DelPostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        io = StringIO.StringIO(self.delpost(delurl, do_delete))
        rep = json.load(io)
        print rep


# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, operation, timeout):
        self.original = operation
        self.timeout = timeout
        self.result = None
        threading.Thread.__init__(self)

    # def uppost(self, url, data):
    #     upload_post = urllib.urlencode(data)
    #     opener = urllib2.build_opener(proxy)
    #     response = opener.open(url, upload_post)
    #     return response.read()

    # def delpost(self, url, data):
    #     delete_post = urllib.urlencode(data)
    #     opener = urllib2.build_opener()
    #     response = opener.open(url, delete_post)
    #     return response.read()

    def run(self):
        try:
            data = urllib.urlencode(do_upload)
            request = urllib2.Request(base_url + self.original + '/', data)
            http_file = urllib2.urlopen(request, timeout=self.timeout)
            self.result = http_file.read()
            return
        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(err)
        self.result = False

    # def run(self):
    #   try:
    #       data = urllib.urlencode()

    #