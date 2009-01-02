#!/usr/bin/env python
from twisted.internet import protocol
from hudsucker import contentproxy

class ContentProxyFactory(protocol.Factory):
    protocol = contentproxy.ContentProxy
    clients = []
    dbpool = None
    service_registry = None
    _cache = None
    def __init__(self, registry):
        ContentProxyFactory.dbpool = registry.db
        ContentProxyFactory.service_registry = registry
        ContentProxyFactory._cache = registry.cache  
    
    @staticmethod
    def cache_set(key, value, expiry_seconds = 0):
        # Convert expiry minutes to seconds as expected by the memcached client.
        return ContentProxyFactory._cache.set(key, value, expiry_seconds)
        
    @staticmethod
    def cache_get(key):
        return ContentProxyFactory._cache.get(key)
    
    @staticmethod
    def cache_get_multi(keys):
        return ContentProxyFactory._cache.get_multi(keys)

    @staticmethod
    def cache_set_multi(mapping):
        return ContentProxyFactory._cache.set_multi(mapping)

