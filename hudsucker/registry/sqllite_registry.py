import registry
try:
    from pysqlite2 import dbapi2 as sqlite3
except Exception:
    print("""Missing Dependency: The pysqlite python extension 
             module that allows access to 
             SQLLite databases must be installed.
             Please run:
             sudo easy_install pysqlite
            """)


class SqlLiteRegistry(registry.Registry):
    """docstring for OracleRegistry"""
    def __init__(self, settings):
        super(registry.Registry, self).__init__(settings=settings)
        try:
            self.db = conn = sqlite3.connect('./db/registry')
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
        
