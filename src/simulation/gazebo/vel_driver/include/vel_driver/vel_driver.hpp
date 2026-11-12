#pragma once
#include <rclcpp/rclcpp.hpp>
#include <rclcpp/create_timer.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <array>
#include <chrono>
#include <cmath>

namespace gazebo
{
class VelDriver : public rclcpp::Node
{
public:
    VelDriver();
private:
    void cmdVelCallback(geometry_msgs::msg::Twist::ConstSharedPtr msg);
    void publishStop();
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr steering_pub_, wheel_pub_;
    rclcpp::TimerBase::SharedPtr watchdog_;
    rclcpp::Time last_command_{0, 0, RCL_ROS_TIME};
    std::array<double, 4> steering_{};
    double l_f_, l_r_, d_l_, d_r_, radius_, timeout_;
};
}
