#!/usr/bin/env python

"""
Hudsucker entry point.


"""

from twisted.internet import protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import service, internet
from config.settings import Settings
from server.contentproxyfactory import ContentProxyFactory
#import registry.oracle_registry
#import registry.sqllite_registry
from registry.yaml_registry import YamlRegistry

def main():
    
    # todo look up registry in configuration ...
    #registry = oracle_registry.OracleRegistry(Settings)
    #registry = sqllite_registry.SQLLiteRegistry(Settings)
    registry = YamlRegistry(Settings)
    
    application = service.Application('remotecontent')
    internet.TCPServer(int(Settings.server['port']), ContentProxyFactory(registry=registry)).setServiceParent(application)

    from twisted.python.runtime import platformType
    if platformType == "win32":
        import win32api, win32con

        def sighandler(sig):
            if sig == win32con.CTRL_LOGOFF_EVENT:
                return True

        win32api.SetConsoleCtrlHandler(sighandler, True)


if __name__ == '__main__':
    main()



           


   

