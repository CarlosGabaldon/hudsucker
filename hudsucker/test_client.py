"""
Testing framework for hudsucker
"""
import sys, logging, unittest, string
from socket import *
from contentclient import TCPServiceResponse

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
        """Test the ability to create full functional service with no registry"""
        self.sock.send('''{"service": "delicious.com", 
                            "params": {
                                "widget": "rss_feed_for_test_only", 
                                "request_path": "/v2/rss/tag/python?count=5",
                                "format":"xml",
                                "base_url":  "http://feeds.delicious.com",
                                "url_patterns": ["/v2/rss"]
                            }
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
    
    def test_yaml_registry(self):
        """Test that we can load the YAML registry
            and sample file"""
        from config.settings import Settings
        from registry.yaml_registry import YamlRegistry
        registry = YamlRegistry(Settings)
        assert registry.db is not None
        base_url, url_patterns = registry.load_service(app='workshops',service='nearme')
        assert base_url == 'http://localhost'
        assert url_patterns[0] == '/{service}/{zip}/'
    
    def test_demisauce_registry(self):
        from config.settings import Settings
        from registry.demisauce_registry import DemisauceRegistry
        registry = DemisauceRegistry(Settings)
        #assert registry.db is not None
        base_url, url_patterns = registry.load_service(app='demisauce',service='comment')
        #print('base_url, url_patterns = %s, %s' % (base_url, url_patterns))
        assert str(base_url) == 'http://localhost:4951'
        assert url_patterns == []
    

if __name__ == "__main__":
    unittest.main()