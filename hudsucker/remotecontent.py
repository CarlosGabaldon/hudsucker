#!/usr/bin/env python

"""
Hudsucker entry point.


"""

from twisted.internet import protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import service, internet
import config.settings
import server.contentproxyfactory
#import registry.oracle_registry
#import registry.sqllite_registry
import registry.yaml_registry

def main():
    
    # todo look up registry in configuration ...
    #registry = oracle_registry.OracleRegistry(Settings)
    #registry = sqllite_registry.SQLLiteRegistry(Settings)
    registry = yaml_registry.YamlRegistry(Settings)
    
    application = service.Application('remotecontent')
    internet.TCPServer(int(settings.Settings.server['port']), ContentProxyFactory(registry=registry)).setServiceParent(application)

    from twisted.python.runtime import platformType
    if platformType == "win32":
        import win32api, win32con

        def sighandler(sig):
            if sig == win32con.CTRL_LOGOFF_EVENT:
                return True

        win32api.SetConsoleCtrlHandler(sighandler, True)


if __name__ == '__main__':
    main()



           


   

