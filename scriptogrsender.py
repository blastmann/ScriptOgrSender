import sublime
import sublime_plugin
import json
import os
import urllib
import urllib2
import threading

# ScriptOgr.am app key
# Please don't modify this key and don't use it in other apps.
# If you want to develop your own app, please apply your own app key
app_key = u'Zl61hxkhDb14f80dad2938ee022365a68e55d2098d'

# Api Call
class ScriptOgrApiCall(threading.Thread):
    """docstring for ScriptOgrApiCall"""
    def __init__(self, action=None):
        threading.Thread.__init__(self)
        if action is None:
            self.action = {}
        else:
            self.action = action
        self.response = None
        self.result = None

    def run(self):
        try:
            opr = {'app_key': app_key, 'user_id': self.action['user_id']}
            if self.action['operation'] == 'post':
                opr['name'] = self.action['filename']
                opr['text'] = self.action['content']
            elif self.action['operation'] == 'delete':
                opr['filename'] = self.action['filename']

            self.post(opr)
            self.parse_response()
            return

        except urllib2.HTTPError as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except urllib2.URLError as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(err)
        self.result = False

    # Post our data
    def post(self, data):
        dataenc= urllib.urlencode(data)
        if self.action['proxy'] != '':
            proxy_handler = urllib2.ProxyHandler({'http': self.action['proxy']})
            request = urllib2.build_opener(proxy_handler)
        else:
            request = urllib2.build_opener()
        http_file = request.open(base_url + self.action['operation'] + '/', dataenc, timeout=self.action['timeout'])
        self.response = http_file.read()

    # Parse the api response
    def parse_response(self):
        response = json.loads(self.response)
        if response['status'] == 'success':
            if self.action['operation'] == 'post':
                self.response = 'Successfully post your article'
            elif self.action['operation'] == 'delete':
                self.response = 'Successfully delete your article'
        elif response['status'] == 'failed':
            self.response = response['reason']

    def get_response(self):
        return self.response

# CommandBase class
class ScriptOgrCommandBase(sublime_plugin.TextCommand):
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

    def handle_threads(self, threads, i=0, indicator=0):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
            else:
                print '\nScriptOgr.am api response: ' + thread.get_response() + '\n'
                sublime.status_message('ScriptOgr.am api response: ' + thread.get_response())
            if not thread.result:
                continue
        threads = next_threads

        if len(threads):
            before = i % 8
            after = 7 - before
            if not after:
                indicator = -1
            if not before:
                indicator = 1
            i += indicator
            self.view.set_status('operating', 'ScriptOgrSender is operating [%s=%s]' % (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(threads, i, indicator), 100)
            return
        self.view.erase_status('operating')

class PostScrCommand(ScriptOgrCommandBase):
    """docstring for PostScrCommand"""
    def runCommand(self, edit, filename):
        # Get article contents
        self.view.run_command("select_all")
        sels = self.view.sel()

        # Start ScriptOgr.am api call in a thread
        threads = []
        for sel in sels:
            content = self.view.substr(sel).encode('utf8')
            # data package
            action = {
                'filename': filename,
                'content': content,
                'operation': 'post',
                'user_id': self.user_id,
                'proxy': self.proxy_server,
                'timeout': 500
            }
            thread = ScriptOgrApiCall(action)
            threads.append(thread)
            thread.start()

        self.view.sel().clear()

        # Handle threads
        self.handle_threads(threads)
        return

class DelPostScrCommand(ScriptOgrCommandBase):
    def runCommand(self, edit, filename):
        # Start ScriptOgr.am api call in a thread
        threads = []
        # data package
        action = {
            'filename': filename,
            'operation': 'delete',
            'user_id': self.user_id,
            'proxy': self.proxy_server,
            'timeout': 500
        }
        thread = ScriptOgrApiCall(action)
        threads.append(thread)
        thread.start()

        # Handle threads
        self.handle_threads(threads)
        return