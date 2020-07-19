#!/bin/bash
ffmpeg -f v4l2 -i /dev/video0 -f rtsp rtsp://0.0.0.0:8554/mystream2

