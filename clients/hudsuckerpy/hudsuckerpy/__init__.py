
def UrlFormatter(url_format,sub_dict):
    for k in sub_dict.keys():
        if sub_dict[k] is not None:
            url_format = url_format.replace('{%s}'%k,sub_dict[k])
    return url_format
    

class ServiceDefinition(object):
    """
    service definition 
    
    :name: name of service
    :format: format (json,xml,html,rss,xmlrpc) of remote service
    :app: url friendly name of app  (hudsucker, workshops, delicious):  
    :cache: True/Fals to use cache default = True
    :cache_time: in seconds, default = 15 minutes
    :base_url:  base url of the "app" (each app has many services, 
        shared base_url) ex:  http://demisauce.demisauce.com
        note, NOT trailing slash
    :url_pattern:  a simple string substitution of any of available values
    :url: actual url for this service, if used will NOT use url_pattern
    :api_key: secret api key for service
    :data: dict of name/value pair's to be added to request  (get/post)
    """
    _service_keys = ['name']
    def __init__(self, name,format='xml', data={},app='hudsucker',
            base_url=None,api_key=None,local_key='id',cache=True,cache_time=900):
        self.name = name
        self.format = format
        self.app = app
        self.cache = cache  
        self.cache_time = cache_time # 15 minutes
        self.base_url = base_url
        self.url_pattern = None
        self.url = None # override
        self.data = data
        self.isdefined = False
        self.needs_service_def = True
        self.service_registry = None
    
    def get_url(self,request=''):
        urlformat = ''
        if self.url_pattern is not None and self.url_pattern != "None":
            # use service.method_url not url_format
            if self.url_pattern != None and self.url_pattern[0:1] == '/':
                urlformat =  '%s%s' % (self.base_url,self.url_pattern)
            else:
                urlformat =  '%s/%s' % (self.base_url,self.url_pattern)
            print('urlformat = %s' % (urlformat))
            self.data.update(
                {"format":self.format,
                 "service":self.name,
                 "request":request})
            return UrlFormatter(urlformat, self.data)
        else:
            return '%s/%s' % (self.base_url,self.url)
    
    def __str__(self):
        return "{name:'%s',app:'%s',format:'%s',base_url:'%s'}" % (self.name,self.app,self.format,self.base_url)
    

def to_hudsucker_json(service):
    """Create a Hudsucker formatted request"""
    #TODO:   move this to a demisaucepy transport?
    """{"app": "delicious.com", 
                        "service": "rss_feed_for_test_only",
                        "url_pattern": "/v2/rss/tag/python?count=5",
                        "base_url":  "http://feeds.delicious.com"
                        "params": {
                            "format":"xml"
                        },
                        "version":"1.1"
                    }\r\n"""
    py_json = {"app":service.app,
            "service":service.name,
            "base_url":service.base_url,
            "url_pattern":service.url_pattern,
            "params":{
                    "format":service.format
                },
            "version":'1.1'}
            
    import simplejson
    json = simplejson.dumps(py_json)
    return '%s\r\n' % json