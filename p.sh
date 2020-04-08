#!/bin/bash

#watch -n 2 "ps u -C python3"

watch -n 5 "ps -eo pid,user,etime,cmd  --forest | grep -v grep | grep python" 

