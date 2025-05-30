FROM osrf/ros:jazzy-desktop

ARG ros_ws=/home/dev_ws

ENV DEBIAN_FRONTEND=noninteractive

# Add Gazebo repository
RUN curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Install apt dependencies, including python3-venv and dependencies for python-pcl
RUN apt-get update && apt-get install -y \
    python3-pip \
    python-is-python3 \
    python3-colcon-clean \
    python3-venv \
    python3-dev \
    make \
    cmake \
    curl \
    nano \
    lsb-release \
    wget \
    libgflags2.2 \
    libgflags-dev \
    libwebsocketpp-dev \
    nlohmann-json3-dev \
    libasio-dev \
    gnupg \
    gz-harmonic \
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
    ros-jazzy-foxglove-bridge \
    less \
    xterm \
    byobu \
    python3-opencv \
    libpcl-dev \
    libproj-dev \
    libboost-all-dev \
    libeigen3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for pip installations
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --upgrade pip

# Install Python dependencies
COPY ./docker/ros2/requirements.txt .
RUN pip install -r ./requirements.txt
# Install transforms3d, pyproj, and python-pcl
RUN pip install transforms3d pyproj

# Custom proj-5.2.0 installation (optional, comment out if libproj-dev suffices)
COPY ./docker/ros2/lib /dep
RUN cd /dep/proj-5.2.0 \
    && bash ./configure \
    && make -j$(nproc) \
    && make install \
    && ln -s /usr/local/lib/libproj.so.13 /usr/lib/libproj.so.13

WORKDIR /home
ENV HOME=/home
ENV PYTHONUNBUFFERED=1

# Set up ROS environment
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc \
    && echo "source /home/dev_ws/install/setup.bash" >> ~/.bashrc \
    && echo "GZ_VERSION=harmonic" >> ~/.bashrc \
    && echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc \
    && echo "export _colcon_cd_root=${ros_ws}" >> ~/.bashrc \
    && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc \
    && echo "source /opt/venv/bin/activate" >> ~/.bashrc

COPY ./dev_ws/src /home/dev_ws/src

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["sleep", "infinity"]