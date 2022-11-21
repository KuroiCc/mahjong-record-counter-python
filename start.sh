export COUNT_POINT_PORT=39002

export PYTHONPATH=/home/kuroi_cc/git-repositorys/mahjong-record-counter-python

`nohup python3 mahjong_record_counter/main.py > port.txt 2>&1 &` ; echo $!