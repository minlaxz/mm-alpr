#!/bin/bash
config='rtsp-simple-server.yml'
admin_username=$(cat $config | awk 'NR==36 {print $2}')
admin_password=$(cat $config | awk 'NR==38 {print $2}')
user_username=$(cat $config | awk 'NR==43 {print $2}')
user_password=$(cat $config | awk 'NR==45 {print $2}')
end_point='anrp_stream'
host='0.0.0.0'
port='8554'
running_pid=$(sudo lsof -i:$port | awk 'NR==2 {print $2}')

serve_server(){
    ./rtsp-simple-server & echo $(date +%s) $! > rtsp.pid
    echo "server is started."
    ffmpeg -f v4l2 -i /dev/video0 -f rtsp rtsp://$admin_username:$admin_password@$host:$port/$end_point
    echo "webcam is published on: http://"$host_port/$end_point
}
terminate_server(){
    if [[ $running_pid != $(<rtsp.pid) ]];then
        echo "confused process id(s). running pid:'"$running_pid "'& stored pid:'"$(<rtsp.pid | awk '{print $2}')"'"
    fi
    case "$1" in
        -2) kill -2 $running_pid ;;#interrupt
        -9) kill -9 $running_pid ;;#terminate
        *) kill -15 $running_pid ;;#exit
    esac
        
        echo " ">rtsp.pid
}
check_server(){
    if [[ -z $running_pid ]];then echo "no such porcess on port: "$port " or with pid: "$(<rtsp.pid)
    else 
        echo "server was started at $(<rtsp.pid | awk '{print $1}')"
        echo "server is running at: "$port "with pid: "$running_pid
    fi
}
configure_server(){
    if [[ -z $running_pid ]]; then 
        echo "sever is running, stop first! "
    else
        echo "current_admin: "$admin_username
        echo "current_admin_password: "$admin_password
        echo "current_user: "$user_username
        echo "curret_user_password: "$user_password
        read -p "update (u)ser/(a)dmin ?:" choice
        case "$choice" in
            [uU]*) 
                read -p "update user name: " changedUserName
                read -p "update user password: " changedUserPassword
                sed -i "s/readUser: [^ ]*/readUser: $changedUserName/" $config
                sed -i "s/readPass: [^ ]*/readPass: $changedUserPassword/" $config
            ;;
            [aA]*) 
                read -p "update admin name: " changedAdminName
                read -p "update admin password: " changedAdminPassword
                sed -i "s/publishUser: [^ ]*/publishUser: $changedAdminName/" $config
                sed -i "s/publishPassword: [^ ]*/publishPassword: $changedAdminPassword/" $config
            ;;
            *) echo "invalid, break.";;
        esac
    fi
}
help_you(){
    echo "This is super helpful."
    echo "./god.sh -s || --serve        start server and publish webcam stream"
    echo "./god.sh -c || --check        check server status"
    echo "./god.sh -t || --terminate    terminate the server"
    echo "./god.sh -t    --confused     use whe error terminating the server"
    echo "./god.sh       --config       configure rtsp server' user & admin"
}   

stVar=$1 #**variable handling**
ndVar=$2

case "$stVar" in
    -s | --serve) serve_server ;;
    -t | --terminate) terminate_server $ndVar;;
    -c | --check) check_server ;;
    --config) configure_server ;;
    --[hH]*) help_you ;; 
    *) printf "[--help] for usage.\n" ;;
esac