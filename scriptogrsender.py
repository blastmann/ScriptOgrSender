import sublime
import sublime_plugin
import httplib
import json
import StringIO
import os
import urllib
import urllib2
import threading
import re

app_key      = ''
user_id      = ''
proxy_server = ''
base_url     = 'http://scriptogr.am/api/article/'

# Operations definitions
# base_opr = {'app_key': app_key, 'user_id': user_id}
# do_upload = {'app_key': app_key, 'user_id': user_id, 'name': 'foo.md', 'text': 'foo'}
# do_delete = {'app_key': app_key, 'user_id': user_id, 'filename': 'foomd.md'}

# Load settings
def get_settings():
    global user_id, proxy_server
    settings = sublime.load_settings('ScriptOgrSender.sublime-settings')
    user_id = settings.get('user_id')
    proxy_server = settings.get('proxy_server')
    # base_opr['user_id'] = user_id

def init_settings():
    get_settings()
    sublime.load_settings('ScriptOgrSender.sublime-settings').add_on_change('get_settings', get_settings)


# Debug
class PrintInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if user_id == '':
            init_settings()
        print user_id
        print proxy_server
        base_opr = {'app_key': app_key, 'user_id': user_id}
        base_opr['name'] = 'foo'
        print base_opr
        filename = os.path.basename(self.view.file_name())
        upload_opr = base_opr
        upload_opr['name'] = filename
        print upload_opr
        print os.path.basename(self.view.file_name())
        return

# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, filedata, operation, timeout):
        self.original = operation
        self.timeout = timeout
        self.result = None
        threading.Thread.__init__(self)

    def post(self, method, data):
        dataenc = urllib.urlencode(data)
        request = urllib2.Request(base_url + self.original + '/', dataenc)
        http_file = urllib2.urlopen(request, timeout=self.timeout)
        self.result = http_file.read()

    def run(self):
        try:
            if self.operation == 'post':
                filename = os.path.basename(self.view.file_name())
                upload_opr = {'app_key': app_key, 'user_id': user_id, 'name': filename}
                post(self.operation, upload_opr)
                print self.result
                return

            elif self.operation == 'delete':
                filename = os.path.basename(self.view.file_name())
                delete_opr = {'app_key': app_key, 'user_id': user_id, 'filename': filename}
                post(self.operation, delete)
                print self.result
                return

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(err)
        self.result = False


# Post
class PostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        threads = []


        return

    def handle_threads(self, edit, threads):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
            if thread.result == False:
                continue
        return


# Delete
class DelPostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        io = StringIO.StringIO(self.delpost(delurl, do_delete))
        rep = json.load(io)
        print rep
