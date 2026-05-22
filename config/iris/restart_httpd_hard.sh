#!/bin/bash
echo "Killing httpd..."
pkill -f httpd
sleep 3
echo "Starting httpd..."
/usr/irissys/httpd/bin/httpd -f /usr/irissys/httpd/conf/httpd.conf -k start
sleep 3
echo "httpd process:"
ps aux | grep httpd | grep -v grep
echo "Done"
