

class ServiceDefinition(object):
    """
    service definition 
    
    :name: name of remote service
    :format: format (json,xml,html,rss,xmlrpc) of remote service
    :app: url friendly name of app  (hudsucker, workshops, delicious):  
    :cache: True/Fals to use cache default = True
    :cache_time: in seconds, default = 15 minutes
    :method_url:  url part of this service (many services/app=base_url)
    :url_format:  a simple string substitution of any of available values
    :api_key: secret api key for service
    :data: dict of name/value pair's to be added to request  (get/post)
    :base_url:  base url of the "app" (each app has many services, 
        shared base_url) ex:  http://demisauce.demisauce.com
        note, NOT trailing slash
    :cache:  default = True, to use cache or not
    """
    _service_keys = ['name']
    def __init__(self, name,format='xml', data={},app='hudsucker',
            base_url=None,api_key=None,local_key='id',cache=True,cache_time=900):
        self.name = name
        self.format = format
        self.app = app
        self.cache = cache
        self.cache_time = cache_time # 15 minutes
        self.url_format = None
        self.data = data
        self.isdefined = False
        self.needs_service_def = True
        self.method_url = None
        self.service_registry = None
        self.base_url = base_url
        # new
        self.url_patterns = []
    
    def __str__(self):
        return "{name:'%s',app:'%s',format:'%s',base_url:'%s'}" % (self.name,self.app,self.format,self.base_url)
    


def to_hudsucker_json(service):
    """Create a Hudsucker formatted request"""
    #TODO:   move this to a demisaucepy transport?
    """{"app": "delicious.com", 
                        "service": "rss_feed_for_test_only",
                        "params": {
                            "request_path": "/v2/rss/tag/python?count=5",
                            "format":"xml",
                            "base_url":  "http://feeds.delicious.com",
                            "url_patterns": ["/v2/rss"]
                        },
                        "version":"v1.1"
                    }\r\n"""
    py_json = {"app":service.app,
            "service":service.name,
            "params":{
                    "format":service.format,
                    "base_url":service.base_url,
                    "request_path":service.method_url
                },
            "version":'v1.1'}
            
    import simplejson
    json = simplejson.dumps(py_json)
    return '%s\r\n' % json