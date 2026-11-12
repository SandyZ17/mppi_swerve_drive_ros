FROM osrf/ros:humble-desktop

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake python3-colcon-common-extensions python3-rosdep \
    python3-numpy python3-yaml python3-pytest \
    ros-humble-grid-map-core ros-humble-grid-map-ros ros-humble-grid-map-msgs \
    ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
    ros-humble-ros2-controllers ros-humble-xacro ros-humble-robot-state-publisher \
    ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-slam-toolbox ros-humble-joy \
    && rm -rf /var/lib/apt/lists/*

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN if ! getent group "${GROUP_ID}" >/dev/null; then groupadd -g "${GROUP_ID}" mppi; fi \
    && if ! getent passwd "${USER_ID}" >/dev/null; then \
       useradd -u "${USER_ID}" -g "${GROUP_ID}" -M -d /tmp -s /bin/bash mppi; fi
ENV HOME=/tmp
WORKDIR /ws
COPY docker/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
USER ${USER_ID}:${GROUP_ID}
STOPSIGNAL SIGINT
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
