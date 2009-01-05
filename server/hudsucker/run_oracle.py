#!/usr/bin/env python

"""
Hudsucker entry point.
"""
import os
from twisted.application import service, internet
from hudsucker.config.settings import Settings
from hudsucker.contentproxyfactory import ContentProxyFactory

from hudsucker.registry.oracle_registry import OracleRegistry

here = os.path.abspath(os.path.dirname(__file__))
Settings.base_path = here
Settings.load_xml(config='%s/config/settings_sdw.config' % (here))
Settings.registry = OracleRegistry(Settings)

application = service.Application('remotecontent')
internet.TCPServer(int(Settings.server['port']), ContentProxyFactory(registry=registry)).setServiceParent(application)

