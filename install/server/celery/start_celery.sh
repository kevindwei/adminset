#!/bin/bash
/usr/bin/celery multi start w1 w2 -c 2 -A adminset -l INFO  --logfile="/var/opt/adminset/logs/%n%I.log" --pidfile=/var/opt/adminset/pid/%n.pid

