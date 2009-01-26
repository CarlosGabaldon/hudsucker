"""
Testing framework for hudsucker
"""
import sys, logging, unittest, string, os
from socket import *
from hudsuckerpy.contentclient import TCPServiceResponse
from hudsucker.config.settings import Settings
from hudsucker.contentproxy import parse_hudsucker_request
from hudsuckerpy import ServiceDefinition, to_hudsucker_json
from hudsucker.remotecontent import here as base_dir
config_file = os.path.abspath('%s/config/settings.config' % (base_dir))
settings = Settings.load_xml(config=config_file )

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
    
    def tearDown(self):
        self.sock.close()
    
    def test_demisauce_registry(self):
        from hudsucker.registry.demisauce_registry import DemisauceRegistry
        registry = DemisauceRegistry(Settings)
        #print registry.config_tostr()
        sd = registry.load_service(ServiceDefinition('comment',app='demisauce',data={'key':'for_testing'}))
        #print('sd.base_url:  %s' % sd.base_url)
        #print('config_file:  %s' % config_file)
        #print('demisauce service uri:  %s' % Settings.registry_config['source'])
        assert str(sd.base_url) == Settings.registry_config['source']
        json = to_hudsucker_json(sd)
        print('json:  %s' % (json))
        self.sock.send('%s\r\n' % json)
        resp = TCPServiceResponse(self.sock.recv(1024))
        print('content:   %s' % (resp.content))
        assert resp.content is not None
        assert resp.is_success() == True
    

if __name__ == "__main__":
    unittest.main()