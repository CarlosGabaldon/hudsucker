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

