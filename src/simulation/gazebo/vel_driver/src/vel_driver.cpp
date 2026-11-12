#include "vel_driver/vel_driver.hpp"

namespace gazebo
{
VelDriver::VelDriver() : rclcpp::Node("vel_driver")
{
    l_f_ = declare_parameter("l_f", 0.5);
    l_r_ = declare_parameter("l_r", 0.5);
    d_l_ = declare_parameter("d_l", 0.5);
    d_r_ = declare_parameter("d_r", 0.5);
    radius_ = declare_parameter("tire_radius", 0.2);
    timeout_ = declare_parameter("command_timeout", 0.5);
    if (radius_ <= 0.0 || timeout_ <= 0.0) { throw std::invalid_argument("Invalid driver parameters"); }
    steering_pub_ = create_publisher<std_msgs::msg::Float64MultiArray>(
        declare_parameter("steering_topic", "/fwids/steering_controller/commands"), 10);
    wheel_pub_ = create_publisher<std_msgs::msg::Float64MultiArray>(
        declare_parameter("wheel_topic", "/fwids/wheel_controller/commands"), 10);
    sub_ = create_subscription<geometry_msgs::msg::Twist>(
        declare_parameter("control_cmd_vel_topic", "/cmd_vel"), 1,
        std::bind(&VelDriver::cmdVelCallback, this, std::placeholders::_1));
    watchdog_ = rclcpp::create_timer(this, get_clock(), std::chrono::milliseconds(100), [this]() {
        if ((now() - last_command_).seconds() > timeout_) { publishStop(); }
    });
}

void VelDriver::publishStop()
{
    std_msgs::msg::Float64MultiArray wheels;
    wheels.data.assign(4, 0.0);
    wheel_pub_->publish(wheels);
}

void VelDriver::cmdVelCallback(geometry_msgs::msg::Twist::ConstSharedPtr msg)
{
    if (!std::isfinite(msg->linear.x) || !std::isfinite(msg->linear.y) || !std::isfinite(msg->angular.z))
    {
        publishStop();
        return;
    }
    last_command_ = now();
    const std::array<double, 4> x{l_f_, l_f_, -l_r_, -l_r_};
    const std::array<double, 4> y{d_l_, -d_r_, d_l_, -d_r_};
    std_msgs::msg::Float64MultiArray angles, wheels;
    for (size_t i = 0; i < 4; ++i)
    {
        const double vx = msg->linear.x - msg->angular.z * y[i];
        const double vy = msg->linear.y + msg->angular.z * x[i];
        double speed = std::hypot(vx, vy) / radius_;
        if (speed > 1e-6)
        {
            double angle = std::atan2(vy, vx);
            // Equivalent reverse wheel motion avoids rotating steering through pi.
            if (angle > M_PI_2) { angle -= M_PI; speed = -speed; }
            else if (angle < -M_PI_2) { angle += M_PI; speed = -speed; }
            steering_[i] = angle;
        }
        angles.data.push_back(steering_[i]);
        wheels.data.push_back(speed);
    }
    steering_pub_->publish(angles);
    wheel_pub_->publish(wheels);
}
}
