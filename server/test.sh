#!/usr/bin/env bash
# 
# Make testing easier by restarting twistd, since it is a 
# daemon process changes made to code don't get re-loaded, 
# so this will reload code changes

# look for twistd, kill and restart
kill `cat twistd.pid`

dir=`pwd`   # assume we are going to work in current directory

# run twistd in background and send logs to log.log
twistd -y hudsucker/remotecontent.py -l ../../log.log -d $dir

python hudsucker/tests/test_server.py


