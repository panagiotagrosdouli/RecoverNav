#include "recovernav_planner/recovernav_planner.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <queue>
#include <stdexcept>
#include <utility>

#include "nav2_costmap_2d/cost_values.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace recovernav_planner
{
namespace
{
struct OpenNode
{
  double f;
  unsigned int index;
  bool operator>(const OpenNode & other) const {return f > other.f;}
};
}  // namespace

void RecoverNavPlanner::configure(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  std::string name,
  std::shared_ptr<tf2_ros::Buffer> tf,
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros)
{
  node_ = parent.lock();
  if (!node_) {
    throw std::runtime_error("RecoverNavPlanner: failed to lock lifecycle node");
  }
  name_ = std::move(name);
  tf_ = std::move(tf);
  costmap_ros_ = std::move(costmap_ros);
  costmap_ = costmap_ros_->getCostmap();

  node_->declare_parameter(name_ + ".lambda_recovery", 2.0);
  node_->declare_parameter(name_ + ".recoverability_radius", 5);
  node_->declare_parameter(name_ + ".exit_sector_count", 8);
  node_->declare_parameter(name_ + ".maximum_traversable_cost", 252);
  node_->declare_parameter(name_ + ".publish_recoverability_grid", true);
  node_->get_parameter(name_ + ".lambda_recovery", lambda_recovery_);
  node_->get_parameter(name_ + ".recoverability_radius", recoverability_radius_);
  node_->get_parameter(name_ + ".exit_sector_count", exit_sector_count_);
  node_->get_parameter(name_ + ".maximum_traversable_cost", maximum_traversable_cost_);
  node_->get_parameter(name_ + ".publish_recoverability_grid", publish_recoverability_grid_);

  if (lambda_recovery_ < 0.0 || recoverability_radius_ < 1 || exit_sector_count_ < 1) {
    throw std::invalid_argument("RecoverNavPlanner: invalid recoverability parameters");
  }
  q_pub_ = node_->create_publisher<nav_msgs::msg::OccupancyGrid>(
    "/recovernav/recoverability_grid", rclcpp::QoS(1).transient_local());
}

void RecoverNavPlanner::cleanup()
{
  q_pub_.reset();
  costmap_ = nullptr;
  costmap_ros_.reset();
  tf_.reset();
  node_.reset();
}

void RecoverNavPlanner::activate()
{
  if (q_pub_) {q_pub_->on_activate();}
}

void RecoverNavPlanner::deactivate()
{
  if (q_pub_) {q_pub_->on_deactivate();}
}

double RecoverNavPlanner::q_at(unsigned int mx, unsigned int my) const
{
  const int r = recoverability_radius_;
  LocalGrid local;
  local.width = static_cast<unsigned int>(2 * r + 1);
  local.height = static_cast<unsigned int>(2 * r + 1);
  local.free.assign(static_cast<std::size_t>(local.width * local.height), 0);
  for (int oy = -r; oy <= r; ++oy) {
    for (int ox = -r; ox <= r; ++ox) {
      const int gx = static_cast<int>(mx) + ox;
      const int gy = static_cast<int>(my) + oy;
      const unsigned int lx = static_cast<unsigned int>(ox + r);
      const unsigned int ly = static_cast<unsigned int>(oy + r);
      if (gx < 0 || gy < 0 || gx >= static_cast<int>(costmap_->getSizeInCellsX()) ||
        gy >= static_cast<int>(costmap_->getSizeInCellsY()))
      {
        continue;
      }
      const auto cost = costmap_->getCost(static_cast<unsigned int>(gx), static_cast<unsigned int>(gy));
      const bool traversable = cost != nav2_costmap_2d::NO_INFORMATION &&
        cost <= static_cast<unsigned char>(maximum_traversable_cost_);
      local.free[static_cast<std::size_t>(ly) * local.width + lx] = traversable ? 1 : 0;
    }
  }
  return structural_recoverability(local, r, r, r, exit_sector_count_);
}

void RecoverNavPlanner::publish_q_grid()
{
  if (!publish_recoverability_grid_ || !q_pub_ || !q_pub_->is_activated()) {return;}
  nav_msgs::msg::OccupancyGrid msg;
  msg.header.stamp = node_->now();
  msg.header.frame_id = costmap_ros_->getGlobalFrameID();
  msg.info.resolution = costmap_->getResolution();
  msg.info.width = costmap_->getSizeInCellsX();
  msg.info.height = costmap_->getSizeInCellsY();
  msg.info.origin.position.x = costmap_->getOriginX();
  msg.info.origin.position.y = costmap_->getOriginY();
  msg.info.origin.orientation.w = 1.0;
  msg.data.assign(static_cast<std::size_t>(msg.info.width * msg.info.height), -1);
  for (unsigned int y = 0; y < msg.info.height; ++y) {
    for (unsigned int x = 0; x < msg.info.width; ++x) {
      const auto c = costmap_->getCost(x, y);
      if (c == nav2_costmap_2d::NO_INFORMATION || c >= nav2_costmap_2d::LETHAL_OBSTACLE) {continue;}
      msg.data[static_cast<std::size_t>(y) * msg.info.width + x] =
        static_cast<int8_t>(std::lround(100.0 * q_at(x, y)));
    }
  }
  q_pub_->publish(msg);
}

nav_msgs::msg::Path RecoverNavPlanner::createPlan(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & goal,
  std::function<bool()> cancel_checker)
{
  nav_msgs::msg::Path path;
  path.header.stamp = node_->now();
  path.header.frame_id = costmap_ros_->getGlobalFrameID();

  unsigned int sx, sy, gx, gy;
  if (!costmap_->worldToMap(start.pose.position.x, start.pose.position.y, sx, sy) ||
    !costmap_->worldToMap(goal.pose.position.x, goal.pose.position.y, gx, gy))
  {
    RCLCPP_WARN(node_->get_logger(), "RecoverNavPlanner: start or goal outside global costmap");
    return path;
  }

  const unsigned int w = costmap_->getSizeInCellsX();
  const unsigned int h = costmap_->getSizeInCellsY();
  const auto idx = [w](unsigned int x, unsigned int y) {return y * w + x;};
  const auto heuristic = [gx, gy](unsigned int x, unsigned int y) {
      return std::abs(static_cast<int>(x) - static_cast<int>(gx)) +
             std::abs(static_cast<int>(y) - static_cast<int>(gy));
    };
  const unsigned int start_i = idx(sx, sy);
  const unsigned int goal_i = idx(gx, gy);
  const double inf = std::numeric_limits<double>::infinity();
  std::vector<double> gscore(static_cast<std::size_t>(w * h), inf);
  std::vector<int> parent(static_cast<std::size_t>(w * h), -1);
  std::priority_queue<OpenNode, std::vector<OpenNode>, std::greater<OpenNode>> open;
  gscore[start_i] = 0.0;
  open.push({static_cast<double>(heuristic(sx, sy)), start_i});
  constexpr int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

  while (!open.empty()) {
    if (cancel_checker && cancel_checker()) {
      RCLCPP_INFO(node_->get_logger(), "RecoverNavPlanner: planning canceled");
      return path;
    }
    const auto current = open.top();
    open.pop();
    if (current.index == goal_i) {break;}
    const unsigned int cx = current.index % w;
    const unsigned int cy = current.index / w;
    for (const auto & d : dirs) {
      const int nx_i = static_cast<int>(cx) + d[0];
      const int ny_i = static_cast<int>(cy) + d[1];
      if (nx_i < 0 || ny_i < 0 || nx_i >= static_cast<int>(w) || ny_i >= static_cast<int>(h)) {
        continue;
      }
      const auto nx = static_cast<unsigned int>(nx_i);
      const auto ny = static_cast<unsigned int>(ny_i);
      const auto cost = costmap_->getCost(nx, ny);
      if (cost == nav2_costmap_2d::NO_INFORMATION || cost > maximum_traversable_cost_) {continue;}
      const unsigned int ni = idx(nx, ny);
      const double q = q_at(nx, ny);
      const double occupancy_penalty = static_cast<double>(cost) / 252.0;
      const double step = 1.0 + occupancy_penalty + lambda_recovery_ * (1.0 - q);
      const double tentative = gscore[current.index] + step;
      if (tentative < gscore[ni]) {
        gscore[ni] = tentative;
        parent[ni] = static_cast<int>(current.index);
        open.push({tentative + static_cast<double>(heuristic(nx, ny)), ni});
      }
    }
  }

  if (start_i != goal_i && parent[goal_i] < 0) {
    RCLCPP_WARN(node_->get_logger(), "RecoverNavPlanner: no path found");
    publish_q_grid();
    return path;
  }

  std::vector<unsigned int> cells;
  for (int cur = static_cast<int>(goal_i); cur >= 0; cur = parent[static_cast<std::size_t>(cur)]) {
    cells.push_back(static_cast<unsigned int>(cur));
    if (static_cast<unsigned int>(cur) == start_i) {break;}
  }
  std::reverse(cells.begin(), cells.end());
  path.poses.reserve(cells.size());
  for (const auto cell : cells) {
    const unsigned int x = cell % w;
    const unsigned int y = cell / w;
    double wx, wy;
    costmap_->mapToWorld(x, y, wx, wy);
    geometry_msgs::msg::PoseStamped pose;
    pose.header = path.header;
    pose.pose.position.x = wx;
    pose.pose.position.y = wy;
    pose.pose.orientation.w = 1.0;
    path.poses.push_back(pose);
  }
  if (!path.poses.empty()) {
    path.poses.front() = start;
    path.poses.front().header = path.header;
    path.poses.back() = goal;
    path.poses.back().header = path.header;
  }
  publish_q_grid();
  return path;
}

}  // namespace recovernav_planner

PLUGINLIB_EXPORT_CLASS(recovernav_planner::RecoverNavPlanner, nav2_core::GlobalPlanner)
