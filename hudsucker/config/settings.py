#!/usr/bin/env python

class Settings(object):
    from xml.etree import ElementTree
    try:
        _doc = ElementTree.parse('config/settings.config')
        database = _doc.find('Database').attrib
        memcached = _doc.find('Memcached').attrib
        server = _doc.find('Server').attrib
        service_registry = _doc.find('ServiceRegistry').attrib
        if service_registry == None:
            svc_node = ElementTree.SubElement(_doc, "ServiceRegistry")
            svc_node.set("type", "YamlRegistry")
    except Exception, detail:
        print("ERROR: Can't load settings: %s." % detail)
        raise

