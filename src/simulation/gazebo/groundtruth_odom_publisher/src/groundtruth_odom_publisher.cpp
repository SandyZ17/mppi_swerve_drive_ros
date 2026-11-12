#include "groundtruth_odom_publisher/groundtruth_odom_publisher.hpp"

namespace gazebo
{

// constructor
GroundTruthOdomPublisher::GroundTruthOdomPublisher()
    : rclcpp::Node("groundtruth_odom_publisher")
{
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    // load parameters 

    //// frame names
    base_frame_name = this->declare_parameter<std::string>("base_frame", "base_link");
    odom_frame_name = this->declare_parameter<std::string>("odom_frame", "odom");

    //// subscribing topic names
    std::string groundtruth_odom_topic;
    groundtruth_odom_topic = this->declare_parameter<std::string>("groundtruth_odom_topic", "/sim/groundtruth_odom");

    pub_odom_ = create_publisher<nav_msgs::msg::Odometry>("/groundtruth_odom", 10);
    // initialize subscribers
    sub_groundtruth_odom_ = this->create_subscription<nav_msgs::msg::Odometry>(groundtruth_odom_topic, rclcpp::SensorDataQoS(), std::bind(&GroundTruthOdomPublisher::groundTruthOdomCallback, this, std::placeholders::_1));
}

// destructor
GroundTruthOdomPublisher::~GroundTruthOdomPublisher()
{
    // No Contents
}

// /odom topic callback
void GroundTruthOdomPublisher::groundTruthOdomCallback(const nav_msgs::msg::Odometry::ConstSharedPtr& msg)
{
    nav_msgs::msg::Odometry odom = *msg;
    // Demo convention: simulator world, map, and odom have the same origin.
    odom.header.frame_id = "map";
    odom.child_frame_id = base_frame_name;
    pub_odom_->publish(odom);
    // get current time
    rclcpp::Time time_now_(msg->header.stamp, this->get_clock()->get_clock_type());

    // publish tf (avoiding publishing tf with same timestamp repeatedly)
    if(prev_tf_timestamp_ != time_now_)
    {
        // update cache
        prev_tf_timestamp_ = time_now_;

        // publish odom tf
        odom_tf_.header.stamp = time_now_;
        odom_tf_.header.frame_id = odom_frame_name;
        odom_tf_.child_frame_id = base_frame_name;
        odom_tf_.transform.translation.x = msg->pose.pose.position.x;
        odom_tf_.transform.translation.y = msg->pose.pose.position.y;
        odom_tf_.transform.translation.z = msg->pose.pose.position.z;
        odom_tf_.transform.rotation.x = msg->pose.pose.orientation.x;
        odom_tf_.transform.rotation.y = msg->pose.pose.orientation.y;
        odom_tf_.transform.rotation.z = msg->pose.pose.orientation.z;
        odom_tf_.transform.rotation.w = msg->pose.pose.orientation.w;
        tf_broadcaster_->sendTransform(odom_tf_);
    }
}

} // namespace gazebo
