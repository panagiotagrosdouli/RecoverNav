#pragma once

#include <functional>
#include <memory>
#include <string>
#include <vector>

#include "nav2_core/global_planner.hpp"
#include "nav2_costmap_2d/costmap_2d_ros.hpp"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "rclcpp_lifecycle/lifecycle_publisher.hpp"
#include "recovernav_planner/recoverability.hpp"

namespace recovernav_planner
{

class RecoverNavPlanner : public nav2_core::GlobalPlanner
{
public:
  RecoverNavPlanner() = default;
  ~RecoverNavPlanner() override = default;

  void configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;
  void cleanup() override;
  void activate() override;
  void deactivate() override;
  nav_msgs::msg::Path createPlan(
    const geometry_msgs::msg::PoseStamped & start,
    const geometry_msgs::msg::PoseStamped & goal,
    std::function<bool()> cancel_checker) override;

private:
  double q_at(unsigned int mx, unsigned int my) const;
  void publish_q_grid();

  rclcpp_lifecycle::LifecycleNode::SharedPtr node_;
  std::shared_ptr<tf2_ros::Buffer> tf_;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;
  nav2_costmap_2d::Costmap2D * costmap_{nullptr};
  rclcpp_lifecycle::LifecyclePublisher<nav_msgs::msg::OccupancyGrid>::SharedPtr q_pub_;
  std::string name_;
  double lambda_recovery_{2.0};
  int recoverability_radius_{5};
  int exit_sector_count_{8};
  int maximum_traversable_cost_{252};
  bool publish_recoverability_grid_{true};
};

}  // namespace recovernav_planner
