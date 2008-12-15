#!/usr/bin/env python
from twisted.internet import protocol
import contentproxy

class ContentProxyFactory(protocol.Factory):
    protocol = contentproxy.ContentProxy
    clients = []
    
    def __init__(self, registry):
        dbpool = registry.db
        _cache = registry.cache  
    
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

