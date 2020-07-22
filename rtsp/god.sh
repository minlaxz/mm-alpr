#!/bin/bash
admin_username='admin'
admin_password='adminpassword'
end_point='anrp_stream'
host='0.0.0.0'
port='8554'
running_pid=$(sudo lsof -i:$port | awk 'NR==2 {print $2}')

serve_server(){
    ./rtsp-simple-server & echo $!>rtsp.pid
    echo "server is started."
    ffmpeg -f v4l2 -i /dev/video0 -f rtsp rtsp://$admin_username:$admin_password@$host:$port/$end_point
    echo "webcam is published on: http://"$host_port/$end_point
}
terminate_server(){
    if [[ $running_pid != $(<rtsp.pid) ]];then
        echo "confused process id(s). running pid:'"$running_pid "'& stored pid:'"$stored_pid"'"
    fi
    case "$1" in
        -2) kill -2 $running_pid ;;#interrupt
        -9) kill -9 $running_pid ;;#terminate
        *) kill -15 $running_pid ;;#exit
    esac
        
        echo " ">rtsp.pid
}
check_server(){
    if [[ -z $running_pid ]];then echo "no such porcess."
    else echo "server is running at: "$port "with pid: "$running_pid
    fi
}
help_you(){
    echo "This is super helpful."
    echo "./god.sh -s || --serve        start server and publish webcam stream"
    echo "./god.sh -c || --check        check server status"
    echo "./god.sh -t || --terminate    terminate the server"
    echo "./god.sh -t    --confused     use whe error terminating the server"
}   

stVar=$1 #**variable handling**
ndVar=$2

case "$stVar" in
    -s | --serve) serve_server ;;
    -t | --terminate) terminate_server $ndVar;;
    -c | --check) check_server ;;
    --[hH]*) help_you ;; 
    *) printf "[--help] for usage.\n" ;;
esac