# Robot Simulation

This package provides a **ROS2 simulation environment** for the Durian Project robot.  
It includes Gazebo worlds, launch files, controller configs, and tools to visualize and test robot in simulation.

### Run simulation

To launch the robot in Gazebo with all default nodes
```sh 
ros2 launch robot_simulation robot_bringup.launch.py
```
Or to calling only robot_description and controller
```sh
ros2 launch robot_simulation summon.launch.py
```