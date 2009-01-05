"""
Testing framework for hudsucker
"""
import sys, logging, unittest, string, os
from socket import *
from hudsuckerpy.contentclient import TCPServiceResponse
from hudsucker.config.settings import Settings
from hudsucker.contentproxy import parse_hudsucker_request
from hudsuckerpy import ServiceDefinition
from hudsucker.remotecontent import here as base_dir
config_file = os.path.abspath('%s/config/settings.config' % (base_dir))
settings = Settings.load_xml(config=config_file )
yaml_file = os.path.abspath('%s/registry/db/registry.yaml' % (base_dir))
#registry = YamlRegistry(Settings,yaml_file)

def sock_data(sock):
    """Get to end of stream"""
    rsp = ''
    while True:
        data = sock.recv(1024)
        if not data or len(data) < 1024:
            break
        rsp += data
    return rsp

class ServicesTests(unittest.TestCase):    
    def setUp(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(('localhost',4615))
        self.sock = sock
        # set the value of a cache key
        self.sock.send('{"service": "memcached", "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}}\r\n')
        data = self.sock.recv(1024)
    
    def tearDown(self):
        self.sock.close()
    
    def test_memcached(self):
        """memcached tests memcached storage"""  
        self.sock.send('{"service": "memcached", "params": {"key": "some_key", "expiry_minutes": "60"}}\r\n')
        resp = TCPServiceResponse(self.sock.recv(1024))
        assert str(resp.content) == 'some_value'
        self.sock.send("""{"service": "memcached", "params": {"key": "some_key","value": "a_new_value", "expiry_minutes": "60"}}\r\n""")
        resp = TCPServiceResponse(self.sock.recv(1024))
        assert str(resp.content) == 'True'
        self.sock.send('{"service": "memcached", "params": {"key": "some_key", "expiry_minutes": "60"}}\r\n')
        resp = TCPServiceResponse(self.sock.recv(1024))
        assert str(resp.content) == 'a_new_value'
    
    def test_diagnostics(self):
        """diagnostics"""
        self.sock.send("""{"service": "diagnostics", "params": {"cmd": "stats"}}\r\n""")
        resp = TCPServiceResponse(self.sock.recv(1024))
        assert resp.content == 'Current connections: 1.'
    
    def test_remote_content(self):
        """get widget remote content"""
        self.sock.send('''{"service": "delicious.com", "params": {"widget": "tag", 
                                            "request_path": "/tag/widgets",
                                            "format":"html"}}\r\n''')
        resp = TCPServiceResponse(sock_data(self.sock))
        #print('resp.content for delicius request:  %s' % resp.content)
        assert resp.content is not None, 'should return html page'
        assert 'Bookmarks' in resp.content, 'should get from delicous bookmars'
        assert resp.is_success() == True
        self.sock.send('''{"service": "workshops", "params": {"widget": "somewidget", 
                                            "request_path": "/nearme/123/08/2008/50/"}}\r\n''')
        resp = TCPServiceResponse(self.sock.recv(1024))
        assert resp.content == None, 'should return nothing as it doesnt exist'
        assert resp.is_success() == False
    
    def test_no_registry_needed(self):
        """Test the ability to create fully functional service with no registry"""
        self.sock.send('''{"app": "delicious.com", 
                            "service": "rss_feed_for_test_only",
                            "params": {
                                "request_path": "/v2/rss/tag/python?count=5",
                                "format":"xml",
                                "base_url":  "http://feeds.delicious.com",
                                "url_patterns": ["/v2/rss"]
                            },
                            "version":"v1.1"
                        }\r\n''')
        resp = TCPServiceResponse(sock_data(self.sock))
        #print('resp.content for delicius request:  %s' % resp.content)
        assert resp.content is not None, 'should return rss xml'
        assert '<channel>' in resp.content, 'should get xml rss'
        assert resp.is_success() == True
    
    def test_response_parser(self):
        """test the response parser's ability to parse responses"""
        resp = TCPServiceResponse('0210some_value')
        assert str(resp.content) == 'some_value'
        resp = TCPServiceResponse('0215some_value_more')
        assert str(resp.content) == 'some_value_more'
        resp = TCPServiceResponse('v1.0\r\n200\r\n20\r\nsome_value_more_here')
        assert str(resp.content) == 'some_value_more_here'
        resp = TCPServiceResponse('v1.0\r\n200\r\n22\r\nsome_value\r\n_more_here')
        assert str(resp.content) == 'some_value\r\n_more_here'
    
    def test_request_parser(self):
        """Test out the Old/New/Versioned compaitility on requests"""
        sd = parse_hudsucker_request('{"service": "memcached", "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}}\r\n')
        assert sd.cache_time == 3600
        assert sd.name == 'memcached'
        assert sd.app == 'hudsucker'
        assert sd.data.has_key('key')
        assert sd.data['value'] == 'some_value'
        sd = parse_hudsucker_request('{"service": "workshops", "params": {"widget": "nearme", "request_path": "/nearme/123/08/2008/50/"}}\r\n')
        assert sd.cache_time == 0
        assert sd.name == 'nearme'
        assert sd.app == 'workshops'
        assert sd.method_url == '/nearme/123/08/2008/50/'
        sd = parse_hudsucker_request('''{"app":"hudsucker", "service": "memcached", "version":"v1.1",
            "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}}\r\n''')
        assert sd.cache_time == 3600
        assert sd.name == 'memcached'
        assert sd.app == 'hudsucker'
        assert sd.data.has_key('key')
        assert sd.data['value'] == 'some_value'
        sd = parse_hudsucker_request('''{"app": "workshops", "service":"nearme", "version":"v1.1",
            "params": {"request_path": "/nearme/123/08/2008/50/"}}''')
        assert sd.cache_time == 0
        assert sd.name == 'nearme'
        assert sd.app == 'workshops'
        assert sd.method_url == '/nearme/123/08/2008/50/'
    
    def test_yaml_registry(self):
        """Test that we can load the YAML registry
            and sample file"""
        from hudsucker.registry.yaml_registry import YamlRegistry
        registry = YamlRegistry(Settings,yaml_file)
        assert registry.db is not None
        sd = registry.load_service(ServiceDefinition('nearme',app='workshops'))
        assert sd.base_url == 'http://localhost'
        assert sd.url_patterns[0] == '/{service}/{zip}/'
        sd = parse_hudsucker_request('''{"service": "delicious.com", "params": {"widget": "tag", 
                                            "request_path": "/tag/widgets",
                                            "format":"html"}}\r\n''')
        sd = registry.load_service(sd)
        assert sd.app == 'delicious.com'
        assert sd.name == 'tag'
        assert sd.base_url == 'http://delicious.com'
    

if __name__ == "__main__":
    unittest.main()