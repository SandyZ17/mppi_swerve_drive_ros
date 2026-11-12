cmake_minimum_required(VERSION 3.16)
project(world_handler)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(ament_cmake REQUIRED)
install(DIRECTORY launch config world xacro rviz DESTINATION share/${PROJECT_NAME})
ament_package()
