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
from hudsucker.contentproxyfactory import ContentProxyFactory
from hudsuckerpy import ServiceDefinition

class OracleRegistry(registry.Registry):
    """docstring for OracleRegistry"""
    def __init__(self, settings):
        super(OracleRegistry, self).__init__(settings=settings)
        try:
             self.db = cx_Oracle.SessionPool(settings.database['username'], 
                 Settings.database['password'], settings.database['dsn'], 
                 int(settings.database['min']), int(settings.database['max']), 
                 int(settings.database['increment']))
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
    
    def load_service(self,service=None):
        """Load Service definition from oracle db"""
        db = None
        service_def_key = 'service_def_%s_%s' % (service.app,service.name)
        service_def = ContentProxyFactory.cache_get(service_def_key)
        if not service_def:
            try:
                print('Attempting to load base URL and URL patterns from database.')
                db = self.db.acquire()
                cursor = db.cursor()
                cursor.arraysize = 50
                sql = """
                    select s.url base_url, u.pattern url_pattern
                    from service_provider s, widget w, widget_url_pattern u
                    where s.name = :app_name and w.name = :service_name
                    """
                cursor.execute(sql, app_name=service.app, service_name=service.name)
                rows = cursor.fetchall()
                if rows:
                    service.base_url = rows[0][0]
                    print('found SDW.row  base_url = %s' % (service.base_url))
                
                else:
                    print("WARNING: No rows for app '%s' and service '%s'." % (service.app, service.name))
            except Exception, detail:
                print("WARNING: Can't load base URL and URL patterns from database: %s." % detail)
            finally:
                if db:
                    self.db.release(db)
            service_def = ServiceDefinition(service.name,app=service.app)
            service_def.base_url = service.base_url
            service_def.url_patterns = service.url_patterns
            ContentProxyFactory.cache_set(service_def_key,service_def)
        else:
            # now transfer service_def -> service
            service.base_url = service_def.base_url
            service.url_patterns = service_def.url_patterns
        
        return service