==============================
Hudsucker:  A Content Proxy
==============================
A TCP server that proxies requests from a web application for remote HTML and services. The content proxy runs local to the web application and listens on port 4615. 


Request Formatting
-------------------
An incoming request must be a JSON string in the following format, and it _must_ terminate with "\r\n".::

    '''{"service": "workshops", "params": {"widget": "nearme", "request_path": "/nearme/123/08/2008/50/"}}\r\n'''

Note the name of the widget is passed in the params value, along with the request_path required to retrieve the HTML.::

    {"service": "memcached", "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}}
    
    {"service": "diagnostics", "params": {"cmd": "ping", "servers": "ONLPDOTNETWEB01 ONLPDOTNETWEB02 ONLPDOTNETWEB03 ONLPDOTNETWEB04", "timeout_seconds": "5"}}
    
    {"service": "diagnostics", "params": {"cmd": "delete_log", "filename": "twistd.log.1"}}
    
    {"service": "diagnostics", "params": {"cmd": "stats"}}

Running Hudsucker:
------------------
::

    twistd -y ~/dev/hudsucker/hudsucker/remotecontent.py -l ~/dev/hudsucker/log.log -d ~/dev/hudsucker/hudsucker 

Dependencies:
----------
    Python 2.5 (Windows: http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi)
    setuptools 0.6c8 (http://pypi.python.org/pypi/setuptools)
    Twisted 8.1.0 (Windows: http://tmrc.mit.edu/mirror/twisted/Twisted/8.1/Twisted_NoDocs-8.1.0.win32-py2.5.exe)
    pywin32-212 (http://python.net/crew/mhammond/win32/Downloads.html)
    simplejson 1.9.2 (http://pypi.python.org/packages/source/s/simplejson/simplejson-1.9.2.tar.gz)
    python-memcached 1.43 (ftp://ftp.tummy.com/pub/python-memcached/python-memcached-1.4.3.tar.gz)
    httplib2 0.4.0 (http://httplib2.googlecode.com/files/httplib2-0.4.0.tar.gz)
    PyYAML:  easy_install pyyaml
    
    