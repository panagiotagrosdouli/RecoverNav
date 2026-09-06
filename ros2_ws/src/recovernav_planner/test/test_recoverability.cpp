#include <gtest/gtest.h>

#include "recovernav_planner/recoverability.hpp"

using recovernav_planner::LocalGrid;
using recovernav_planner::structural_recoverability;

TEST(Recoverability, Bounded)
{
  LocalGrid grid{7, 7, std::vector<uint8_t>(49, 1)};
  const double q = structural_recoverability(grid, 3, 3, 3, 8);
  EXPECT_GE(q, 0.0);
  EXPECT_LE(q, 1.0);
}

TEST(Recoverability, OpenAreaHigherThanDeadEnd)
{
  LocalGrid open{7, 7, std::vector<uint8_t>(49, 1)};
  LocalGrid dead{7, 7, std::vector<uint8_t>(49, 0)};
  for (int y = 1; y <= 5; ++y) {
    dead.free[static_cast<std::size_t>(y) * 7 + 3] = 1;
  }
  for (int x = 3; x <= 5; ++x) {
    dead.free[static_cast<std::size_t>(1) * 7 + x] = 1;
  }
  EXPECT_GT(structural_recoverability(open, 3, 3, 3, 8),
            structural_recoverability(dead, 3, 3, 3, 8));
}
