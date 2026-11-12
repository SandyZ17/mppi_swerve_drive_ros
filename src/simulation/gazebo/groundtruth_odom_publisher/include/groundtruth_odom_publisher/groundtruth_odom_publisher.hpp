#pragma once

#include <rclcpp/rclcpp.hpp>
#include <rclcpp/create_timer.hpp>
#include <functional>
#include <chrono>
#include <cmath>
#include <memory>
#include <stdexcept>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

namespace gazebo
{
    class GroundTruthOdomPublisher : public rclcpp::Node
    {
        public:
            GroundTruthOdomPublisher();
            ~GroundTruthOdomPublisher();
            void groundTruthOdomCallback(const nav_msgs::msg::Odometry::ConstSharedPtr& msg);
        private:
            rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr sub_groundtruth_odom_;
            rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr pub_odom_;
            rclcpp::Time prev_tf_timestamp_{0, 0, RCL_ROS_TIME};
            std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
            geometry_msgs::msg::TransformStamped odom_tf_;
            std::string base_frame_name, odom_frame_name;
    };
}