import registry
try:
    import cx_Oracle
except Exception:
    print("""Missing Dependency: The cx_Oracle Python extension 
             module that allows access to 
             Oracle databases must be installed.
             Please install from here:
             http://python.net/crew/atuining/cx_Oracle/
            """)


class OracleRegistry(registry.Registry):
    """docstring for OracleRegistry"""
    def __init__(self, settings):
        super(Registry, self).__init__(settings=settings)
        try:
             self.db = cx_Oracle.SessionPool(settings.database['username'], 
                 Settings.database['password'], settings.database['dsn'], 
                 int(settings.database['min']), int(settings.database['max']), 
                 int(settings.database['increment']))
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
        
        