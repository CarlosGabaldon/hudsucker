#!/usr/bin/env python

"""
Hudsucker entry point.


"""
import os, sys
from twisted.internet import protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import service, internet
from hudsucker.config.settings import Settings
from hudsucker.contentproxyfactory import ContentProxyFactory
#import registry.oracle_registry
#import registry.sqllite_registry
from hudsucker.registry.yaml_registry import YamlRegistry
#from registry.demisauce_registry import DemisauceRegistry

#def main():
    
# todo look up registry in configuration ...
#registry = oracle_registry.OracleRegistry(Settings)
#registry = sqllite_registry.SQLLiteRegistry(Settings)
# why did i do this pathing?  Because tests, and this from twistd weren't picking up same path
here = os.path.abspath(os.path.dirname(__file__))
Settings.base_path = here
settings = Settings.load_xml(config='%s/config/settings.config' % (here))
registry = YamlRegistry(Settings, os.path.abspath('%s/registry/db/registry.yaml' % (here)))
#registry = DemisauceRegistry(Settings)

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
    t = True
