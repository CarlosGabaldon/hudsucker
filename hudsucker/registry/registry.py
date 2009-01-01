#!/usr/bin/env python
try:
    import memcache
except Exception, detail:
    print("""Missing Dependency: The python-memcached extension 
             module that allows access to 
             memcached must be installed.
             Please install from here:
             ftp://ftp.tummy.com/pub/python-memcached/
            """)


class Registry(object):
    """Service Registry"""
    def __init__(self, settings):
        self.db = None
        self.cache = memcache.Client(settings.memcached['servers'].split(','))
    
    def load_service(self,service):
        """Loads service Registry info for app/service"""
        raise NotImplementedError("Must be implemented by Registry")
    
