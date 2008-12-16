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
        super(OracleRegistry, self).__init__(settings=settings)
        try:
             self.db = cx_Oracle.SessionPool(settings.database['username'], 
                 Settings.database['password'], settings.database['dsn'], 
                 int(settings.database['min']), int(settings.database['max']), 
                 int(settings.database['increment']))
        except Exception, detail:
            print("WARNING: Can't connect to database: %s." % detail)
            self.db = None
    
    def load_service(self,app='hudsucker',service='ping'):
        """Load Service definition from oracle db"""
        db = None
        base_url = None
        url_patterns = []
        try:
            print('Attempting to load base URL and URL patterns from database.')
            db = self.db.acquire()
            cursor = db.cursor()
            cursor.arraysize = 50
            sql = """
                select s.url base_url, u.pattern url_pattern
                from service_provider s, widget w, widget_url_pattern u
                where s.name = :service_name and w.name = :widget_name
                """
            cursor.execute(sql, service_name=self.service, widget_name=widget)
            rows = cursor.fetchall()
            if rows:
                url_patterns = []
                base_url = rows[0][0]
                for row in rows:
                    url_patterns.append(row[1])
            else:
                print("WARNING: No rows for service '%s' and widget '%s'." % (self.service, widget))
        except Exception, detail:
            print("WARNING: Can't load base URL and URL patterns from database: %s." % detail)
        finally:
            if db:
                self.db.release(db)
                
        return base_url, url_patterns