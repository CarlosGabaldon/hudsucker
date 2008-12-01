#!/usr/bin/env python

"""
A TCP server that proxies requests from a web application for remote HTML. The content proxy runs local to the web application
and listens on port 4615. An incoming request must be a JSON string in the following format, and it _must_ terminate with "\r\n".

{"service": "workshops", "params": {"widget": "nearme", "request_path": "/nearme/123/08/2008/50/"}}

Note the name of the widget is passed in the params value, along with the request_path required to retrieve the HTML.

{"service": "memcached", "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}}
{"service": "diagnostics", "params": {"cmd": "ping", "servers": "ONLPDOTNETWEB01 ONLPDOTNETWEB02 ONLPDOTNETWEB03 ONLPDOTNETWEB04", "timeout_seconds": "5"}}
{"service": "diagnostics", "params": {"cmd": "delete_log", "filename": "twistd.log.1"}}
{"service": "diagnostics", "params": {"cmd": "stats"}}

Requires:
    Python 2.5 (Windows: http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi)
    setuptools 0.6c8 (http://pypi.python.org/pypi/setuptools)
    Twisted 8.1.0 (Windows: http://tmrc.mit.edu/mirror/twisted/Twisted/8.1/Twisted_NoDocs-8.1.0.win32-py2.5.exe)
    pywin32-212 (http://python.net/crew/mhammond/win32/Downloads.html)
    simplejson 1.9.2 (http://pypi.python.org/packages/source/s/simplejson/simplejson-1.9.2.tar.gz)
    python-memcached 1.43 (ftp://ftp.tummy.com/pub/python-memcached/python-memcached-1.4.3.tar.gz)
    httplib2 0.4.0 (http://httplib2.googlecode.com/files/httplib2-0.4.0.tar.gz)
    
ChangeLog:
    2008-08-19, Hung Luu: Initial release with limited error handling and hardcoded DEV paths
    2008-09-03, Hung Luu:
        - Expose python-memcached as a limited service so Service Registry Admin can get/set from/to memcached.
        - Replace individual restful parameters with one "requesturl" parameter.
    2008-09-09, Hung Luu:
        - Renamed "requesturl" to "request_path".
        - Renamed "expiryminutes" to "expiry_minutes".
        - Added a diagnostics service command to grab log entries based on a date range.
    2008-09-15, Hung Luu:
        - Added a Win32 event handler to ignore the logoff event.
        - Strip leading and trailing whitespace from URL patterns.
    2008-09-17, Hung Luu:
        - Guard against possible unicode characters in the remote HTML.
        - Load base URL and URL patterns from SDW as a fallback.
        - Make environmental settings configurable.
    2008-09-22, Hung Luu:
        - Allow configurable HTTP timeout.
    2008-10-13, Hung Luu:
        - Removed log file reading from diagnostics, Service Proxy Console can read the log files directly.
        - Added a diagnostics service command to ping other service proxies running in the same web farm.
        - Check memcached first for the content expiry minutes, then fallback to Settings.config.
        - Refactor diagnostics params formatting.
    2008-11-17, Hung Luu:
        - Write content meta in the first few bytes to help clients better parse response:
            First 2 bytes: x number of bytes to read after the first 2 bytes, which should represent the content length.
            Next x bytes: y number of bytes in the content.
            Next y bytes: The actual content.
        - Changed name to 'Content Proxy'.
        - Support cache meta in ModulePrefs of Gadget XML.
        - Cleanup of cache set ops with expiration.
        - Converted all print statements to print function calls for Python 3000.
        - Added a stats command for diagnostics.
"""

from twisted.internet import protocol
from twisted.protocols.basic import LineOnlyReceiver
import memcache, cx_Oracle

CONTENT_EXPIRY_MINUTES = 1440
class ContentProxy(LineOnlyReceiver):
    def __init__(self):
        self.service = ''
        self.params = {}

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
    
    def lineReceived(self, data):
        import simplejson
        command = {}
        print('Input data: ' + data)
        try:
            command = simplejson.loads(data)
        except Exception, detail:
            print('ERROR: Decoding JSON input: %s' % detail)
            self.transport.loseConnection()
        else:
            self.service = command.get('service')
            self.params = command.get('params')
            if not self.service or not self.params:
                print("ERROR: Missing 'service' and/or 'params' JSON keys.")
                self.transport.loseConnection()
            else:
                self.service = str(self.service)
                if self.service == 'memcached':
                    self._process_memcached()
                elif self.service == 'diagnostics':
                    self._process_diagnostics()
                else:
                    self._process_remote_content()

    def _process_memcached(self):
        key = self.params.get('key')
        if not key:
            print("ERROR: Missing 'key' parameter.")
            self.transport.loseConnection()
        else:
            # Memcached key cannot be unicode.
            key = str(key)
            value = self.params.get('value')
            if value:
                # Store strings in utf-8 encoding.
                if isinstance(value, basestring):
                    value = value.encode('utf-8', 'replace')
                # Store value as Python object, or as string?
                set_result = False
                expiry_minutes = self.params.get('expiry_minutes')
                if expiry_minutes != None:
                    try:
                        set_result = bool(self.factory.cache_set(key, value, float(expiry_minutes)))
                    except Exception, detail:
                        set_result = "Can't cache key '%s': %s."  % (key, detail)
                else:
                    set_result = bool(self.factory.cache_set(key, value))
                self._sendResponse(str(set_result))
            else:
                value = self.factory.cache_get(key)
                if value:
                    self._sendResponse(str(value))
                else:
                    self._sendResponse('KeyDoesntExist')

    def _process_diagnostics(self):
        content = ''
        cmd = self.params.get('cmd')
        if cmd == 'ping':
            import socket
            servers = self.params.get('servers')
            if servers:
                timeout_seconds = self.params.get('timeout_seconds')
                if not timeout_seconds:
                    timeout_seconds = '5'
                port = int(Settings.server['port'])
                server_list = servers.split(' ')
                for server in server_list:
                    server = str(server)
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(float(timeout_seconds))
                        s.connect((server, port))
                        s.close()
                        content += "Successfully connected to server '%s' on port %d.\n" % (server, port)
                    except socket.error, detail:
                        content += "Can't connect to server '%s' on port %d: %s.\n" % (server, port, detail)
        elif cmd == 'delete_log':
            import re, os
            pattern = 'twistd[.]log[.].*$'
            regex = re.compile(pattern)
            filename = self.params.get('filename')
            if not filename:
                found_none = True
                names = os.listdir(os.getcwd())
                for name in names:
                    if regex.match(name):
                        found_none = False
                        try:
                            os.remove(name)
                            content += "Rolled log file '%s' deleted.\n" % name
                        except Exception, detail:
                            content += "Can't delete rolled log file '%s': %s.\n" % (name, detail)
                if found_none:
                    content += 'There were no rolled log files to delete.'
            elif regex.match(filename):
                filename = str(filename)
                try:
                    os.remove(filename)
                    content += "Rolled log file '%s' deleted." % filename;
                except Exception, detail:
                    content += "Can't delete rolled log file '%s': %s" % (filename, detail)
        elif cmd == 'stats':
            content += 'Current connections: %d.' % len(self.factory.clients)               
        if content:
            self._sendResponse(content)
        self.transport.loseConnection()
        
    def _process_remote_content(self):
        widget = self.params.get('widget')
        request_path = self.params.get('request_path')
        if not widget or not request_path:
            print("ERROR: Missing 'widget' and/or 'request_path' JSON keys.")
            self.transport.loseConnection()
        else:
            widget = str(widget)
            request_path = str(request_path)
            base_url_key = 'aps_%s_baseurl' % self.service
            url_patterns_key = 'aps_%s_%s_urlpatterns' % (self.service, widget)
            content_key = 'aps_%s_%s_%s' % (self.service, widget, request_path)                    
            cache_dict = self.factory.cache_get_multi([base_url_key, url_patterns_key, content_key])
            content = cache_dict.get(content_key)
            if content:
                self._sendResponse(content)
            else:
                base_url = cache_dict.get(base_url_key)
                # URL patterns stored in memcached as Python list.
                url_patterns = cache_dict.get(url_patterns_key)
                if not base_url or not url_patterns:
                    # Try loading from database.
                    if self.factory.dbpool:
                        db = None
                        try:
                            print('Attempting to load base URL and URL patterns from database.')
                            db = self.factory.dbpool.acquire()
                            cursor = db.cursor()
                            cursor.arraysize = 50
                            sql = """
                                select s.url base_url, u.pattern url_pattern
                                from service_provider s, widget w, widget_url_pattern u
                                where s.name = :service_name and w.name = :widget_name
                                """
                            cursor.execute(sql, service_name=self.service, widget_name=widget)
                            rows = cursor.fetchall()
                            if rows:
                                url_patterns = []
                                base_url = rows[0][0]
                                for row in rows:
                                    url_patterns.append(row[1])
                            else:
                                print("WARNING: No rows for service '%s' and widget '%s'." % (self.service, widget))
                            if base_url and url_patterns:
                                mapping = {base_url_key: base_url, url_patterns_key: url_patterns}
                                self.factory.cache_set_multi(mapping)
                        except Exception, detail:
                            print("WARNING: Can't load base URL and URL patterns from database: %s." % detail)
                        finally:
                            if db:
                                self.factory.dbpool.release(db)
                if not base_url:
                    print("ERROR: Can't load base URL: " + base_url_key)
                    self.transport.loseConnection()
                if not url_patterns:
                    print("ERROR: Can't load URL patterns: " + url_patterns_key)
                    self.transport.loseConnection()
                if base_url and url_patterns:
                    import re
                    matched = False
                    for url_pattern in url_patterns:
                        regex = re.compile(url_pattern.strip())
                        if regex.match(request_path):
                            matched = True
                            break                   
                    if matched:
                        import httplib2
                        widget_url = base_url + request_path
                        # Uncomment to enable HTTP caching.
                        #http = httplib2.Http('.cache')
                        timeout_seconds = self.factory.cache_get('aps_http_timeout_seconds')
                        if not timeout_seconds:
                            timeout_seconds = Settings.server.get('http_timeout_seconds')
                        if not timeout_seconds:
                            http = httplib2.Http()
                        else:
                            http = httplib2.Http(timeout=int(timeout_seconds))
                        try:
                            print('HTTP request: ' + widget_url)
                            resp, gadget_xml = http.request(widget_url)
                            if resp.status == 200:
                                from xml.etree import ElementTree
                                doc = ElementTree.fromstring(gadget_xml)
                                content_element = doc.find('Content')
                                # Why does this keep returning true: if not content_element?
                                if content_element == None:
                                    self._sendResponse("NoContent")
                                else:
                                    content = content_element.text
                                    if content:
                                        try:
                                            content = content.encode('utf-8', 'replace')
                                        except Exception, detail:
                                            print('WARNING: UTF-8 encoding of remote HTML failed: %s.' % detail)
                                            self._sendResponse('BadEncoding')
                                        else:
                                            try:
                                                moduleprefs_element = doc.find('ModulePrefs')
                                                cache = moduleprefs_element.get('cache')
                                                expiry_minutes = None
                                                if cache == 'true':
                                                    expiry_minutes = moduleprefs_element.get('cache_expiry_minutes')
                                                if expiry_minutes == None and cache != 'false':
                                                    expiry_minutes = self.factory.cache_get('aps_%s_%s_content_expiry_minutes' % (self.service, widget))
                                                    if expiry_minutes == None:
                                                        expiry_minutes = Settings.memcached.get('content_expiry_minutes')
                                                        if expiry_minutes == None:
                                                            expiry_minutes = CONTENT_EXPIRY_MINUTES
                                                if expiry_minutes != None and not self.factory.cache_set(content_key, content, float(expiry_minutes)):
                                                    raise Exception('Set operation failed.')
                                            except Exception, detail:
                                                print("WARNING: Can't cache content: %s." % detail)
                                            finally:
                                                self._sendResponse(content)
                                    else:
                                        self._sendResponse('EmptyContent')
                            else:
                                print('WARNING: %s returned HTTP status code %d.' % (widget_url, resp.status))
                        except Exception, detail:
                            print('ERROR: HTTP request for %s has failed: %s.' % (widget_url, detail))
                            self.transport.loseConnection()
                    else:
                        print("ERROR: Request URL doesn't match any URL patterns: %s." % url_patterns)
                        self.transport.loseConnection()

    def _writeContentMeta(self, content):
        num_bytes_content_as_string = str(len(content))
        num_bytes_len_as_string = str(len(num_bytes_content_as_string))
        if len(num_bytes_len_as_string) < 2:
            num_bytes_len_as_string = '0' + num_bytes_len_as_string
        self.transport.write(num_bytes_len_as_string)
        self.transport.write(num_bytes_content_as_string)

    def _sendResponse(self, content):
        self._writeContentMeta(content)
        self.transport.write(content + '\r\n')

class Settings(object):
    from xml.etree import ElementTree
    try:
        _doc = ElementTree.parse('settings.config')
        database = _doc.find('Database').attrib
        memcached = _doc.find('Memcached').attrib
        server = _doc.find('Server').attrib
    except Exception, detail:
        print("ERROR: Can't load settings: %s." % detail)
        raise

           
class ContentProxyFactory(protocol.Factory):
    protocol = ContentProxy
    clients = []
    try:
        dbpool = cx_Oracle.SessionPool(Settings.database['username'], Settings.database['password'], Settings.database['dsn'], int(Settings.database['min']), int(Settings.database['max']), int(Settings.database['increment']))
    except Exception, detail:
        print("WARNING: Can't connect to database: %s." % detail)
        dbpool = None
    _cache = memcache.Client(Settings.memcached['servers'].split(','))    
    
    @staticmethod
    def cache_set(key, value, expiry_minutes = 0):
        # Convert expiry minutes to seconds as expected by the memcached client.
        return ContentProxyFactory._cache.set(key, value, expiry_minutes * 60)
        
    @staticmethod
    def cache_get(key):
        return ContentProxyFactory._cache.get(key)
    
    @staticmethod
    def cache_get_multi(keys):
        return ContentProxyFactory._cache.get_multi(keys)

    @staticmethod
    def cache_set_multi(mapping):
        return ContentProxyFactory._cache.set_multi(mapping)



   
from twisted.application import service, internet

application = service.Application('remotecontent')
internet.TCPServer(int(Settings.server['port']), ContentProxyFactory()).setServiceParent(application)

from twisted.python.runtime import platformType
if platformType == "win32":
    import win32api, win32con
    
    def sighandler(sig):
        if sig == win32con.CTRL_LOGOFF_EVENT:
            return True
    
    win32api.SetConsoleCtrlHandler(sighandler, True)
