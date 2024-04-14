#! /bin/bash

PID=$(lsof -i:$COUNT_POINT_PORT | awk 'NR>1 {print $2}')
kill $PID
echo "Stopped server with PID $PID"
