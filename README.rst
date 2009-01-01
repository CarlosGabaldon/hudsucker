==============================
Hudsucker:  A Content Proxy
==============================
A TCP server that proxies requests from a web application for remote HTML and services. The content proxy runs local to the web application and listens on port 4615. 


Request Formatting
-------------------
An incoming request must be a JSON string in the following format, and it _must_ terminate with "\r\n".  Also note it passes a version attribute, allowing backwards compatibility to previous formats.::

    '''{"app": "workshops", "service": "nearme", "params": {"request_path": "/nearme/123/08/2008/50/", "version":"v1.1"}}\r\n'''
    
    '''{"app": "delicious.com", 
                        "service": "rss_feed_for_test_only",
                        "params": {
                            "request_path": "/v2/rss/tag/python?count=5",
                            "format":"xml",
                            "base_url":  "http://feeds.delicious.com",
                            "url_patterns": ["/v2/rss"]
                        },
                        "version":"v1.1"
                    }\r\n'''

Hudsucker also supports native services on Hudsucker.::

    {"app": "hudsucker","service": "memcached", "params": {"key": "some_key", "value": "some_value", "expiry_minutes": "60"}, "version":"v1.1"}
    
    {"app": "hudsucker","service": "diagnostics", "params": {"cmd": "ping", "servers": "myremotehost", "timeout_seconds": "5"}, "version":"v1.1"}
    
    {"app": "hudsucker","service": "diagnostics", "params": {"cmd": "delete_log", "filename": "twistd.log.1"}, "version":"v1.1"}
    
    {"app": "hudsucker","service": "diagnostics", "params": {"cmd": "stats"}, "version":"v1.1"}

Running Hudsucker:
------------------
To run Hudsucker as a background process
::

    twistd -y ~/dev/hudsucker/hudsucker/remotecontent.py -l ~/dev/hudsucker/log.log -d ~/dev/hudsucker/hudsucker 

To run Hudsucker as a foreground process and dump log info to console output
::

    twistd -y ~/dev/hudsucker/hudsucker/remotecontent.py -n -d ~/dev/hudsucker/hudsucker 

Dependencies:
---------------
- Python 2.5 http://python.org/download/
- setuptools 0.6c8 http://pypi.python.org/pypi/setuptools
- Twisted 8.1.0 http://twistedmatrix.com/trac/wiki/Downloads
- simplejson 1.9.2 http://pypi.python.org/packages/source/s/simplejson/
- python-memcached 1.43 ftp://ftp.tummy.com/pub/python-memcached/python-memcached-1.4.3.tar.gz
- httplib2 0.4.0 http://httplib2.googlecode.com/files/
- PyYAML:  easy_install pyyaml

For Windows Users:
- pywin32-212 http://python.net/crew/mhammond/win32/Downloads.html

    
    
