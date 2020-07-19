#!/bin/bash
kill -9 $(<rtsp.pid) & echo $!
