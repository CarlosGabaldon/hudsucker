from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='hudsucker',
      version=version,
      description="Hudsucker is a Proxy Content Server in Python",
      long_description="""
Hudsucker
===========

`Hudsucker
<http://hudsucker.googlecode.com>`_ is Proxy Server for remote
content and services written in python. 

More information and Download
------------------------------

Hudsucker can found at http://hudsucker.googlecode.com or development version at http://github.com/CarlosGabaldon/hudsucker
""",
    classifiers=["  Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ], 
    keywords='python',
    author='Hung',
    author_email='',
    url='http://hudsucker.googlecode.com/',
    install_requires=["elementtree>=1.1","nose>=0.10.4",
        'simplejson>=1.9.2', 'python-memcached>=1.43',
        'httplib2', 'PyYAML'],
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    # -*- Entry points: -*-
    """,
)
