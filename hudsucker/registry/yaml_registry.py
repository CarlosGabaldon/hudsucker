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
        try:
            stream = file('registry/db/registry.yaml','r')
            self.db = yaml.load(stream)
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
        self.cache = None    
        super(registry.Registry, self).__init__(settings=settings)
        
