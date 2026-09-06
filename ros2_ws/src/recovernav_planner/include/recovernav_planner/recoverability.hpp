#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cmath>
#include <queue>
#include <vector>

namespace recovernav_planner
{

struct LocalGrid
{
  unsigned int width{0};
  unsigned int height{0};
  std::vector<uint8_t> free;

  bool inside(int x, int y) const
  {
    return x >= 0 && y >= 0 && static_cast<unsigned int>(x) < width &&
           static_cast<unsigned int>(y) < height;
  }

  bool is_free(int x, int y) const
  {
    return inside(x, y) && free[static_cast<std::size_t>(y) * width + x] != 0;
  }
};

inline double structural_recoverability(
  const LocalGrid & grid, int cx, int cy, int radius, int sector_count = 8)
{
  if (radius < 1 || sector_count < 1 || !grid.is_free(cx, cy)) {
    return 0.0;
  }

  const int xmin = std::max(0, cx - radius);
  const int xmax = std::min(static_cast<int>(grid.width) - 1, cx + radius);
  const int ymin = std::max(0, cy - radius);
  const int ymax = std::min(static_cast<int>(grid.height) - 1, cy + radius);

  const int local_w = xmax - xmin + 1;
  const int local_h = ymax - ymin + 1;
  std::vector<uint8_t> visited(static_cast<std::size_t>(local_w * local_h), 0);
  auto local_idx = [xmin, ymin, local_w](int x, int y) {
      return static_cast<std::size_t>((y - ymin) * local_w + (x - xmin));
    };

  std::queue<std::pair<int, int>> q;
  q.emplace(cx, cy);
  visited[local_idx(cx, cy)] = 1;
  std::size_t reachable = 0;
  std::vector<uint8_t> exits(static_cast<std::size_t>(sector_count), 0);
  constexpr std::array<std::pair<int, int>, 4> dirs{{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}};

  while (!q.empty()) {
    const auto [x, y] = q.front();
    q.pop();
    ++reachable;

    const int dx = x - cx;
    const int dy = y - cy;
    if (std::abs(dx) == radius || std::abs(dy) == radius || x == xmin || x == xmax || y == ymin ||
      y == ymax)
    {
      const double ax = static_cast<double>(dx);
      const double ay = static_cast<double>(dy);
      if (ax != 0.0 || ay != 0.0) {
        constexpr double pi = 3.14159265358979323846;
        double angle = std::atan2(ay, ax);
        if (angle < 0.0) {
          angle += 2.0 * pi;
        }
        const int sector = std::min(
          sector_count - 1, static_cast<int>(angle / (2.0 * pi) * sector_count));
        exits[static_cast<std::size_t>(sector)] = 1;
      }
    }

    for (const auto & [ox, oy] : dirs) {
      const int nx = x + ox;
      const int ny = y + oy;
      if (nx < xmin || nx > xmax || ny < ymin || ny > ymax || !grid.is_free(nx, ny)) {
        continue;
      }
      const auto idx = local_idx(nx, ny);
      if (!visited[idx]) {
        visited[idx] = 1;
        q.emplace(nx, ny);
      }
    }
  }

  const double area = static_cast<double>(local_w * local_h);
  const double coverage = area > 0.0 ? static_cast<double>(reachable) / area : 0.0;
  const int active = static_cast<int>(
    std::count(exits.begin(), exits.end(), static_cast<uint8_t>(1)));
  const double exit_score = std::min(
    1.0, static_cast<double>(active) / std::max(2, sector_count / 2));
  const double q_value = 0.55 * exit_score + 0.45 * coverage;
  return std::clamp(q_value, 0.0, 1.0);
}

}  // namespace recovernav_planner
