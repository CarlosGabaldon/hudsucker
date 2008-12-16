import registry
try:
    import yaml
except Exception:
    print("""Missing Dependency: The PyYAML 
             module that allows access to 
             Yaml files must be installed.
             Please install from here:
             http://pyyaml.org/wiki/PyYAML
            """)


#http://pyyaml.org/download/pyyaml/PyYAML-3.06.tar.gz


class YamlRegistry(registry.Registry):
    """docstring for YamlRegistry"""
    def __init__(self, settings):
        super(YamlRegistry, self).__init__(settings)
        try:
            stream = file('registry/db/registry.yaml','r')
            self.db = yaml.load_all(stream)
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
    
    def load_service(self,app='hudsucker',service='ping'):
        """Loads service Registry"""
        base_url = None
        url_patterns = []
        for svc in self.db:
            if svc['service'] == app and svc['params']['widget'] == service:
                base_url = svc['base_url']
                url_patterns.append(svc['params']['url_pattern'])
        
        return base_url,url_patterns
