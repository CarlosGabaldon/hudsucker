#!/usr/bin/env python

class Settings(object):
    database = {'dsn':None,'username':None}
    memcached = {'servers':'localhost:11211','content_expiry_minutes':180}
    server = {'port':4615,'http_timeout_seconds':3}
    service_registry = {"type":"yaml", "source":"registry/db/registry.yaml"}
    base_path = '~/'
    @staticmethod
    def load_xml(config='config/settings.config'):
        """Load Configuration from Xml File
        <?xml version="1.0" encoding="utf-8"?>
        <ContentProxy>
          <Server port="4615" http_timeout_seconds="3" />
          <ServiceRegistry type="yaml" source="registry/db/registry.yaml" />
          or
          <ServiceRegistry type="oracle" username="" password="" dsn="" min="1" max="2" increment="1" />
          or
          type="demisauce" appname="hudsucker_testing" 
            source="http://localhost:4951" api_key="a95c21ee8e64cb5ff585b5f9b761b39d7cb9a202"
          <Memcached servers="192.168.125.128:11211" content_expiry_minutes="180" />
          
          <!-- Legacy Support, switch to ServiceRegistry  -->
          <Database username="" password="" dsn="" min="1" max="2" increment="1" />
        </ContentProxy>

        """
        from xml.etree import ElementTree
        try:
            _doc = ElementTree.parse(config)
            Settings.database = _doc.find('Database').attrib
            Settings.memcached = _doc.find('Memcached').attrib
            Settings.server = _doc.find('Server').attrib
            _registry= _doc.find('ServiceRegistry')
            if _registry == None:
                svc_node = ElementTree.SubElement(_doc.getroot(), "ServiceRegistry")
                svc_node.set("type", "YamlRegistry")
                Settings.service_registry = svc_node
            else:
                Settings.service_registry = _registry.attrib
        except Exception, detail:
            print("ERROR: Can't load settings: %s." % detail)
            raise
    

