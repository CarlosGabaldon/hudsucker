from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='hudsuckerpy',
      version=version,
      description="Python library to Hudsucker Proxy Content Server",
      long_description="""
HudsuckerPy
===========

`Hudsucker
<http://hudsucker.googlecode.com>`_ is Proxy Server for remote
content and services written in python. 

**Hudsucker PY** Is a python library to talk to a *Hudsucker* proxy server.

Download and Installation
-------------------------

Hudsucker can be installed by geting the latest version at http://github.com/CarlosGabaldon/hudsucker
""",
    classifiers=["  Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ], 
    keywords='python',
    author='Aaron Raddon',
    author_email='',
    url='http://hudsucker.googlecode.com/',
    install_requires=["nose>=0.10.4",'simplejson>=1.9.2'],
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    # -*- Entry points: -*-
    """,
)
