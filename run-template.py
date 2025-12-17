#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 10
python /data/data/com.termux/files/home/run.py > /data/data/com.termux/files/home/proxy_log.txt 2>&1 &
