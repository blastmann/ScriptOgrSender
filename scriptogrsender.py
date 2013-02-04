import sublime
import sublime_plugin
import json
import os
import urllib
import urllib2
import threading

app_key = ''

# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, filename, filedata, operation, userid, proxy, timeout):
        self.filename  = filename
        self.filedata  = filedata
        self.operation = operation
        self.timeout   = timeout
        self.userid    = userid
        self.proxy     = proxy
        self.response  = None
        self.result    = None
        threading.Thread.__init__(self)

    # Post our data
    def post(self, method, data):
        dataenc     = urllib.urlencode(data)
        if self.proxy != '':
            request = urllib2.build_opener(self.proxy)
        else:
            request = urllib2.build_opener()
        http_file   = request.open(baseurl + self.operation + '/', dataenc, timeout=self.timeout)
        self.response = http_file.read()

    # Parse the api response
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
                opr = {'app_key': app_key, 'user_id': self.userid, 'name': self.filename, 'text': self.filedata}
            elif self.operation == 'delete':
                opr = {'app_key': app_key, 'user_id': self.userid, 'filename': self.filename}

            self.post(self.operation, opr)
            self.parse_response()
            return

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(err)
        self.result = False

# CommandBase class
class CommandBase(sublime_plugin.TextCommand):
    """docstring for CommandBase"""
    def __init__(self, view):
        # Inherit from class TextCommand
        sublime_plugin.TextCommand.__init__(self, view)
        self.user_id = None
        self.proxy_server = None
        self.base_url = None

    # Get plugin settings
    def get_settings(self):
        settings = sublime.load_settings('ScriptOgrSender.sublime-settings')
        self.user_id = settings.get('user_id')
        self.proxy_server = settings.get('proxy_server')
        self.base_url = settings.get('base_url')

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
            self.view.set_status('operating', 'ScriptOgrSender is opearting [%s=%s]' % \
                (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(threads, i, dir), 100)
            return
        self.view.erase_status('operating')

# Post v0.2
class PostScrCommand(CommandBase):
    """docstring for PostScrCommand"""
    def run (self, edit):
        if self.user_id == '':
            self.get_settings()

        # Get filename
        basename = os.path.basename(self.view.file_name())
        f, ext = os.path.splitext(basename)

        # Get article contents
        self.view.run_command("select_all")
        sels = self.view.sel()

        # Start ScriptOgr.am api call in a thread
        threads = []
        for sel in sels:
            content = self.view.substr(sel)
            thread = ScriptOgrApiCall(f, content, 'post', self.user_id, self.proxy_server, 500)
            threads.append(thread)
            thread.start()

        self.view.sel().clear()

        # Handle threads
        self.handle_threads(threads)
        return

# Delete v0.2
class DelPostScrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.user_id == '':
            self.get_settings()

        # Get filename
        basename = os.path.basename(self.view.file_name())
        f, ext = os.path.splitext(basename)

        # Start ScriptOgr.am api call in a thread
        threads = []
        thread = ScriptOgrApiCall(f, '', 'delete', self.user_id, self.proxy_server, 500)
        threads.append(thread)
        thread.start()

        # Handle threads
        self.handle_threads(threads)
        return