# Base image for ROS 2 Jazzy
FROM osrf/ros:jazzy-desktop

ARG ros_ws=/home/dev_ws
ARG ros_gz_ws=/home/ros_gz_ws

ENV DEBIAN_FRONTEND=noninteractive

# Core tools
RUN apt-get update && apt-get install -y \
    python3-pip \
    python-is-python3 \
    python3-colcon-clean \
    make \
    curl \
    nano \
    lsb-release \
    wget \
    libgflags-dev \
    libwebsocketpp-dev \
    nlohmann-json3-dev \
    libasio-dev \
    gnupg

RUN sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Install Gazebo harmonic + sim tools + SDFormat
RUN apt-get update && apt-get install -y \
    gz-harmonic \
    libsdformat14

# Install ROS 2 core and navigation tools
RUN apt-get update && apt-get install -y \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-robot-localization \
    ros-jazzy-plotjuggler-ros \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-ros2bag \
    ros-jazzy-rosbag2-storage-default-plugins \
    ros-jazzy-rqt-tf-tree \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-xacro \
    ros-jazzy-diagnostic-updater \
    ros-jazzy-diagnostic-aggregator \
    ros-jazzy-apriltag-ros \
    ros-jazzy-actuator-msgs \
    ros-jazzy-tf-transformations \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-spatio-temporal-voxel-layer \
    ros-jazzy-rviz2 \
    ros-jazzy-rviz-common \
    ros-jazzy-rviz-default-plugins \
    ros-jazzy-rviz-visual-tools \
    ros-jazzy-rviz-rendering \
    ros-jazzy-nav2-rviz-plugins \
    ros-jazzy-image-transport-plugins \
    ros-jazzy-gscam \
    ros-jazzy-image-common \
    ros-jazzy-topic-tools \
    ros-jazzy-rosbag2-storage-mcap \
    ros-jazzy-foxglove-bridge

# Python libraries
RUN pip install --break-system-packages transforms3d pyproj

# Extra tools
RUN apt-get install -y \
    less \
    xterm \
    byobu \
    python3-opencv

# Install custom PROJ library
COPY ./docker/ros2/lib /dep
RUN cd /dep/proj-5.2.0 \
    && bash ./configure \
    && make -j$(nproc) \
    && make install \
    && ln -s /usr/local/lib/libproj.so.13 /usr/lib/libproj.so.13

# Install Python requirements
COPY ./docker/ros2/requirements.txt .
RUN pip install --break-system-packages -r ./requirements.txt

# Set working directory
WORKDIR /home
ENV HOME=/home
ENV PYTHONUNBUFFERED=1

# Copy source workspaces
COPY ./dev_ws/src /home/dev_ws/src
COPY ./ros_gz_ws/src /home/ros_gz_ws/src

# rosdep fix and install
RUN rosdep init || true && rosdep update
RUN cd /home/ros_gz_ws && rosdep install -y --from-paths src --ignore-src --rosdistro ${ROS_DISTRO}

# Source ROS setup
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
RUN echo "source /home/dev_ws/install/setup.bash" >> ~/.bashrc
RUN echo "source /home/ros_gz_ws/install/setup.bash" >> ~/.bashrc
RUN echo "GZ_VERSION=harmonic" >> ~/.bashrc

# Colcon tools
RUN echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc \
    && echo "export _colcon_cd_root=${ros_ws}" >> ~/.bashrc \
    && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Entry point
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["sleep", "infinity"]
