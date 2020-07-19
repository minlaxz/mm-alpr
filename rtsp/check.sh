#!/bin/bash
if [[ $(ps -a | grep -i rtsp-simple-ser | wc -l) == 1 ]]; then
echo 'running.'
else
echo 'no such process ' $(<rtsp.pid)
fi
