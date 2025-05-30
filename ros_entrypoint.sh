#!/bin/bash
set -e
    
source /opt/venv/bin/activate
source "/opt/ros/jazzy/setup.bash"
source /home/dev_ws/install/setup.bash
# source /home/ros_gz_ws/install/setup.bash

exec "$@"