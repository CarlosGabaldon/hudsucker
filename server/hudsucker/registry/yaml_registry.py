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
    """A Service Definition registry that stores info in local 
    yaml file and stores in memory (won't be reloaded 
    if yaml is changed while twistd is running)"""
    def __init__(self, settings, yaml_file='hudsucker/registry/db/registry.yaml'):
        super(YamlRegistry, self).__init__(settings)
        try:
            stream = file(yaml_file,'r')
            self.db = [svc for svc in yaml.load_all(stream)]
        except Exception, detail:
            raise Exception(yaml_file)
            print("WARNING: Can't get YAML file: %s." % detail)
            self.db = None
    
    def load_service(self,service=None):
        """
        Returns service Definition after population additiona
        info from registry
        """
        if service is None:
            raise Exception("must have service defintion to know which to load")
        found = False
        for svc in self.db:
            if svc['service'] == service.name and svc['app'] == service.app:
                found = True
                service.base_url = svc['base_url']
                service.url_patterns.append(svc['params']['url_pattern'])
        return service
