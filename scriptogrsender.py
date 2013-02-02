import sublime
import sublime_plugin
import json
import os
import urllib
import urllib2
import threading

app_key = ''

# Load settings
def get_settings():
    global user_id, proxy_server, baseurl
    settings = sublime.load_settings('ScriptOgrSender.sublime-settings')
    user_id = settings.get('user_id')
    proxy_server = settings.get('proxy_server')
    baseurl = settings.get('base_url')

def init_settings():
    get_settings()
    sublime.load_settings('ScriptOgrSender.sublime-settings').add_on_change('get_settings', get_settings)

# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, filename, filedata, operation, timeout):
        self.filename  = filename
        self.filedata  = filedata
        self.operation = operation
        self.timeout   = timeout
        self.response  = None
        self.result    = None
        threading.Thread.__init__(self)

    def post(self, method, data):
        dataenc     = urllib.urlencode(data)
        if proxy_server != '':
            request = urllib2.build_opener(proxy_server)
        else:
            request = urllib2.build_opener()
        http_file   = request.open(baseurl + self.operation + '/', dataenc, timeout=self.timeout)
        self.response = http_file.read()

    def parse_response(self):
        response = json.loads(self.response)
        if response['status'] == 'success':
            if self.operation == 'post':
                self.response = 'Successfully post your article'
            elif self.operation == 'delete':
                self.response = 'Successfully delete your article'
        elif response['status'] == 'failed':
            self.response = response['reason']

    def get_response(self):
        return self.response

    def run(self):
        try:
            if self.operation == 'post':
                opr = {'app_key': app_key, 'user_id': user_id, 'name': self.filename, 'text': self.filedata}
            elif self.operation == 'delete':
                opr = {'app_key': app_key, 'user_id': user_id, 'filename': self.filename}

            self.post(self.operation, opr)
            self.parse_response()
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
        init_settings()

        # Get filename
        basename = os.path.basename(self.view.file_name())
        f, ext = os.path.splitext(basename)

        self.view.run_command("select_all")
        sels = self.view.sel()
        threads = []

        for sel in sels:
            content = self.view.substr(sel)
            thread = ScriptOgrApiCall(f, content, 'post', 500)
            threads.append(thread)
            thread.start()

        self.view.sel().clear()
        self.handle_threads(threads)
        return

    def handle_threads(self, threads, i=0, dir=0):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
            else:
                print '\nScriptOgr.am api response: ' + thread.get_response() + '\n'
                sublime.status_message('ScriptOgr.am api response: ' + thread.get_response())
            if thread.result == False:
                continue
        threads = next_threads

        if len(threads):
            before = i % 8
            after = (7) - before
            if not after:
                dir = -1
            if not before:
                dir = 1
            i += dir
            self.view.set_status('postopr', 'Posting page [%s=%s]' % \
                (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(threads, i, dir), 100)
            return
        self.view.erase_status('postopr')

# Delete
class DelPostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        init_settings()

        # Get filename
        basename = os.path.basename(self.view.file_name())
        f, ext = os.path.splitext(basename)

        threads = []
        thread = ScriptOgrApiCall(f, '', 'delete', 500)
        threads.append(thread)
        thread.start()

        self.handle_threads(threads)
        return

    def handle_threads(self, threads, i=0, dir=0):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
            else:
                print '\nScriptOgr.am api response: ' + thread.get_response() + '\n'
                sublime.status_message('ScriptOgr.am api response: ' + thread.get_response())
            if thread.result == False:
                continue
        threads = next_threads

        if len(threads):
            before = i % 8
            after = (7) - before
            if not after:
                dir = -1
            if not before:
                dir = 1
            i += dir
            self.view.set_status('postopr', 'Posting page [%s=%s]' % \
                (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(threads, i, dir), 100)
            return
        self.view.erase_status('postopr')
