#!/usr/bin/env python

"""
Hudsucker entry point.
"""
import os
from twisted.internet import protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import service, internet
from hudsucker.config.settings import Settings
from hudsucker.contentproxyfactory import ContentProxyFactory

from hudsucker.registry.demisauce_registry import DemisauceRegistry

here = os.path.abspath(os.path.dirname(__file__))
Settings.base_path = here
settings = Settings.load_xml(config='%s/config/settings.config' % (here))
registry = DemisauceRegistry(Settings)

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
    # run twistd using yaml runner
    os.system("twistd -y run_demisauce.py -n -d %s" % (here))
