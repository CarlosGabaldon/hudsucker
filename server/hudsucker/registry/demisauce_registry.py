import registry
try:
    import demisaucepy
    import demisaucepy.cfg as dsconfig
    from demisaucepy import cache_setup

except Exception:
    print("""Missing Dependency: The Demisaucepy library
            is necessary for the configuraiton in your settings.config
            of ServiceRegistry type="Demisauce"   """)

class DemisauceRegistry(registry.Registry):
    """Registry for remote web service based
    service registry on a demisauce server"""
    def __init__(self, settings):
        super(DemisauceRegistry, self).__init__(settings=settings)
        api_key = settings.service_registry['api_key']
        url = settings.service_registry['source']
        appname = settings.service_registry['appname']
        try:
            dsconfig.CFG['demisauce.apikey'] = api_key or 'a95c21ee8e64cb5ff585b5f9b761b39d7cb9a202'
            dsconfig.CFG['demisauce.url'] = url or 'http://localhost:4951'
            dsconfig.CFG['demisauce.appname'] = appname or 'hudsucker'
            dsconfig.CFG['cacheservers'] = settings.memcached['servers'].replace(',',';')
            cache_setup.load_cache(cachetype='memcache')
        except Exception, detail:
            print("WARNING: Can't connect to demisauce: %s." % detail)
    
    def config_tostr(self):
        return "url:%s, apikey=%s, cache=%s" % (dsconfig.CFG['demisauce.url'] ,
            dsconfig.CFG['demisauce.apikey'],dsconfig.CFG['cacheservers'] )
    
    def load_service(self,service):
        """Loads service Registry"""
        
        dsservice=demisaucepy.ServiceDefinition(
            name=service.name,
            format='xml',
            app_slug=service.app
        )
        from demisaucepy.cache import cache
        #print('in load_service cfg.CFG["demisauce.url"] = %s' % (dsconfig.CFG['demisauce.url']))
        if not dsservice.isdefined and dsservice.needs_service_def == True:
            print('DemisauceRegistry_load:  calling service definition load %s/%s' % (dsservice.app_slug,dsservice.name))
            dsservice.cache = False
            dsservice.load_definition(request_key='request')
            service.base_url = dsservice.base_url
            service.format = dsservice.format
            service.method_url = dsservice.get_url('none')
            service.method_url = service.method_url.replace('%s/' % dsservice.base_url,'')
        return service