SHELL := /bin/bash
export LOCAL_UID := $(shell id -u)
export LOCAL_GID := $(shell id -g)
DOCKER_COMPOSE ?= docker compose
PLANNER ?= mppi_h
WORLD ?= maze
GUI ?= true
RVIZ ?= true
JOBS ?= 2
RUN = $(DOCKER_COMPOSE) run --rm dev

.PHONY: setup_docker run_docker build local_build navigation gazebo_world test smoke_test slam clean

setup_docker:
	$(DOCKER_COMPOSE) build dev

run_docker:
	$(RUN) bash

build:
	$(RUN) bash -c 'MAKEFLAGS=-j$(JOBS) colcon build --symlink-install --parallel-workers $(JOBS) --cmake-args -DCMAKE_BUILD_TYPE=Release'

local_build:
	source /opt/ros/humble/setup.bash && colcon build --symlink-install --parallel-workers $(JOBS) --cmake-args -DCMAKE_BUILD_TYPE=Release

navigation:
	$(RUN) ros2 launch mppi_bringup navigation.launch.py local_planner:=$(PLANNER) gazebo_world_name:=$(WORLD) gui:=$(GUI) open_rviz:=$(RVIZ)

gazebo_world:
	$(RUN) ros2 launch mppi_bringup gazebo_world.launch.py gazebo_world_name:=$(WORLD) gui:=$(GUI)

slam:
	$(RUN) ros2 launch mppi_bringup slam.launch.py gazebo_world_name:=$(WORLD) gui:=$(GUI)

smoke_test:
	$(RUN) python3 scripts/smoke_test_ros2.py --require-goal

test:
	$(RUN) python3 -m pytest -q tests

clean:
	rm -rf build install log
