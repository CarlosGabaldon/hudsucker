#!/usr/bin/env python
from twisted.protocols.basic import LineOnlyReceiver
from hudsucker.config.settings import Settings
from hudsuckerpy import ServiceDefinition

HUDSUCKER_SERVICES = ['diagnostics', 'memcached']

def parse_hudsucker_request(data):
    """Parse request into Service Definition
    json v1::
        {"service": "memcached", 
         "params": {"key": "some_key", 
                    "value": "some_value", 
                    "expiry_minutes": "60"}
        }
    
    json v1.1::
        {"app": "hudsucker", 
         "service": "memcached",
         "version":"1.1", 
         "expiry_minutes": "60",
         "params": {"key": "some_key", 
                    "value": "some_value"}
        }
    """
    import simplejson
    sd = ServiceDefinition('tbd')
    #print('Input data: ' + data)
    command = simplejson.loads(data)
    params = command['params']
    if 'version' not in command:
        # Legacy format before versioning
        if not command.has_key('service'):
            raise Exception('Requires service:   {"service":"myservice", ...}')
        svc = str(command['service'])
        if svc in HUDSUCKER_SERVICES:
            sd.app = 'hudsucker'
            sd.name = svc
        else:
            sd.app = svc
            sd.name = str(params['widget'])
            sd.format = 'gadgetmini'
            if params.has_key('format'):
                sd.format = str(params.get('format'))
            if not params.has_key('request_path'):
                raise Exception('Remote Content Services Require a Request Path')
            else:
                sd.url_pattern = str(params['request_path'])
        if 'expiry_minutes' in params:
            sd.cache_time = float(params['expiry_minutes']) * 60
        else:
            sd.cache_time = 0
        sd.data = params
        
    elif str(command['version']) == '1.1':
        # new versionable request's
        if not command.has_key('app'):
            raise Exception('Requires an App to be specified:   {"app": "hudsucker","version":"1.1",....')
        sd.app = str(command['app'])
        if not command.has_key('service'):
            raise Exception('Requires a Service to be specified:   {"app": "hudsucker", "service":"myservice","version":"1.1",....')
        sd.name = str(command['service'])
        if command.has_key('url_pattern'):
            #print('setting sd.url_pattern = %s' % (command['url_pattern']))
            sd.url_pattern = str(command['url_pattern'])
        if 'expiry_minutes' in command:
            sd.cache_time = float(command['expiry_minutes']) * 60
        else:
            sd.cache_time = 0
        sd.format = 'gadgetmini'
        if params.has_key('format'):
            sd.format = str(params.get('format'))
        if command.has_key('base_url'):
            sd.base_url = str(command['base_url'])
        if command.has_key('base_url') and command.has_key('url_pattern'):
            sd.isdefined = True
        sd.data = params
    else:
        raise Exception('Unknown Request Format')
    return sd



CONTENT_EXPIRY_MINUTES = 1440
class ContentProxy(LineOnlyReceiver):
    def __init__(self):
        self.service = ''
        self.service_def = None
        self.params = {}
    
    def requires_data_keys(self,keys):
        for key in keys:
            if not self.service_def.data.has_key(key):
                raise Exception('Missing ...., "params":{"%s":"value"}' % (key))
    
    def connectionMade(self):
        self.factory.clients.append(self)
    
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
    
    def lineReceived(self, data):
        import simplejson
        command = {}
        print('Input data: ' + data)
        command = simplejson.loads(data)
        self.service_def = parse_hudsucker_request(data)
        try:
            pass
        except Exception, detail:
            print('ERROR: Decoding JSON input: %s' % detail)
            self.transport.loseConnection()
        else:
            if self.service_def.app == 'hudsucker':
                if self.service_def.name == 'memcached':
                    self._process_memcached()
                elif self.service_def.name == 'diagnostics':
                    self._process_diagnostics()
                else:
                    raise NotImplementedError('Not implemented %s' % service_def.name)
            else:
                self._process_remote_content()
    
    def _process_memcached(self):
        """
        Get/Set values in memcached.  This is currently used
        through this proxy because not all .net/java/php/python libraries
        use the same alogrithms for key generation and can't share memcached storage
        therefore
        """
        self.requires_data_keys(['key'])
        # Memcached key cannot be unicode.
        key = str(self.service_def.data['key'])
        if self.service_def.data.has_key('value'):
            # Store strings in utf-8 encoding.
            value = self.service_def.data['value']
            if isinstance(value, basestring):
                value = value.encode('utf-8', 'replace')
            # Store value as Python object, or as string?
            set_result = False
            try:
                cache_time = float(self.service_def.cache_time)
                set_result = bool(self.factory.cache_set(key, value, cache_time))
            except Exception, detail:
                set_result = "Can't cache key '%s': %s."  % (key, detail)
            self._sendResponse(str(set_result))
        else:
            value = self.factory.cache_get(key)
            if value:
                self._sendResponse(str(value))
            else:
                self._sendResponse('KeyDoesntExist')
    
    def _process_diagnostics(self):
        content = ''
        self.requires_data_keys(['cmd'])
        cmd = self.service_def.data['cmd']
        if cmd == 'ping':
            import socket
            servers = self.service_def.data['servers']
            if servers:
                timeout_seconds = self.service_def.data['timeout_seconds']
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
            filename = self.service_def.data['filename']
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
        """
        Fulfill proxyed service request
        First get service definition, then fulfill
        """
        sd = self.service_def
        #TODO:  hash this to ensure it is a short key
        content_key = "app_%s_%s_%s" % (sd.app,sd.name,sd.get_url())
        content = self.factory.cache_get(content_key)
        if content:
            self._sendResponse(content)
        else:
            # Try loading from service registry.
            if self.factory.service_registry and self.service_def.isdefined == False:
                self.factory.service_registry.load_service(service=self.service_def)
                print('app=%s, service=%s, base_url=%s,url_pattern = %s' % (sd.app,sd.name,sd.base_url,sd.url_pattern))
            if not self.service_def.base_url:
                print("ERROR: Doesn't have base URL: (%s)" % (sd.base_url))
                self.transport.loseConnection()
            else:
                import httplib2
                url = sd.get_url()
                print('HTTP request: ' + url)
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
                    
                    resp, service_content = http.request(url)
                    if resp.status == 200 and sd.format in ['html','xml']:
                        self._sendResponse(service_content)
                    elif resp.status == 200 and sd.format == 'gadgetmini':
                        # TODO:  move this to ServiceResponse.from_gadgetmini()
                        from xml.etree import ElementTree
                        doc = ElementTree.fromstring(service_content)
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
                                        #TODO:  refactor this to store it in the already cached service def's, not in memcache
                                        moduleprefs_element = doc.find('ModulePrefs')
                                        cache = moduleprefs_element.get('cache')
                                        expiry_minutes = None
                                        if cache == 'true':
                                            expiry_minutes = moduleprefs_element.get('cache_expiry_minutes')
                                        if expiry_minutes == None and cache != 'false':
                                            expiry_minutes = self.factory.cache_get('aps_%s_content_expiry_minutes' % (self.sd.name))
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
                        print('WARNING: %s returned HTTP status code %d.' % (url, resp.status))
                except Exception, detail:
                    print('ERROR: HTTP request for %s has failed: %s.' % (url, detail))
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
    
