import sublime
import sublime_plugin
import json
import os
import urllib
import urllib2
import threading

app_key = u''

# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, filename, filedata, operation, user_id, proxy_server, timeout):
        threading.Thread.__init__(self)
        self.filename  = filename
        self.filedata  = filedata
        self.operation = operation
        self.timeout   = timeout
        self.user_id   = user_id
        self.proxy     = proxy_server
        self.response  = None
        self.result    = None

    def run(self):
        try:
            opr = {'app_key': app_key, 'user_id': self.user_id}
            if self.operation == 'post':
                opr['name'] = self.filename
                opr['text'] = self.filedata
            elif self.operation == 'delete':
                opr['filename'] = self.filename

            self.post(self.operation, opr)
            self.parse_response()
            return

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(err)
        self.result = False

    # Post our data
    def post(self, method, data):
        dataenc= urllib.urlencode(data)
        if self.proxy != '':
            proxy = urllib2.ProxyHandler(proxies = {'http' : self.proxy})
            request = urllib2.build_opener(proxy)
        else:
            request = urllib2.build_opener()
        http_file = request.open(base_url + self.operation + '/', dataenc, timeout=self.timeout)
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

# CommandBase class
class CommandBase(sublime_plugin.TextCommand):
    """docstring for CommandBase"""
    def __init__(self, view):
        # Inherit from class TextCommand
        sublime_plugin.TextCommand.__init__(self, view)

    def run(self, edit):
        global base_url
        settings = sublime.load_settings('ScriptOgrSender.sublime-settings')
        base_url = settings.get('base_url')
        self.user_id = settings.get('user_id')
        self.proxy_server = settings.get('proxy_server')

        # Get filename
        basename = os.path.basename(self.view.file_name())
        f, ext = os.path.splitext(basename)
        self.runCommand(edit, f)

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
    def runCommand(self, edit, filename):
        # Get article contents
        self.view.run_command("select_all")
        sels = self.view.sel()

        # Start ScriptOgr.am api call in a thread
        threads = []
        for sel in sels:
            content = self.view.substr(sel).encode('utf8')
            thread = ScriptOgrApiCall(filename, content, 'post', self.user_id, self.proxy_server, 500)
            threads.append(thread)
            thread.start()

        self.view.sel().clear()

        # Handle threads
        self.handle_threads(threads)
        return

# Delete v0.2
class DelPostScrCommand(CommandBase):
    def runCommand(self, edit, filename):
        # Start ScriptOgr.am api call in a thread
        threads = []
        thread = ScriptOgrApiCall(filename, '', 'delete', self.user_id, self.proxy_server, 500)
        threads.append(thread)
        thread.start()

        # Handle threads
        self.handle_threads(threads)
        return