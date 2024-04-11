#! /bin/bash

`nohup poetry run start >> $PROJECTS/mahjong-record-counter-python/mahjong_record_counter/logs/server.log 2>&1 &` ; echo $!
