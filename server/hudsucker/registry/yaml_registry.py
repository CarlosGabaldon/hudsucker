import registry
try:
    import yaml
except Exception:
    print("""Missing Dependency: The PyYAML module that allows access to 
             Yaml files must be installed.  Please install from here:
             http://pyyaml.org/wiki/PyYAML""")

class YamlRegistry(registry.Registry):
    """A Service Definition registry that stores info in local 
    yaml file and stores in memory (won't be reloaded 
    if yaml is changed while twistd is running)"""
    def __init__(self, settings, yaml_file='hudsucker/registry/db/registry.yaml'):
        super(YamlRegistry, self).__init__(settings)
        try:
            stream = file(yaml_file,'r')
            services = [svc for svc in yaml.load_all(stream)]
            self.db = {}
            for svc in services:
                self.db[svc['service']] = svc
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
        if self.db.has_key(service.name):
            service.base_url = self.db[service.name]['base_url']
            if service.url_pattern == None:
                service.url_pattern = self.db[service.name]['url_pattern']
        return service
    
