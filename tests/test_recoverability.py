import numpy as np
from recovernav.environment import GridEnvironment
from recovernav.recoverability.local_exits import local_exit_score, recoverability_heatmap

def test_q_bounded():
    env=GridEnvironment(np.zeros((9,9),dtype=np.uint8)); heat=recoverability_heatmap(env,radius=2); vals=heat[~np.isnan(heat)]; assert np.all((0<=vals)&(vals<=1))

def test_dead_end_lower_than_intersection():
    grid=np.ones((11,11),dtype=np.uint8); grid[5,1:10]=0; grid[2:9,5]=0; intersection=local_exit_score(GridEnvironment(grid),(5,5),radius=3)
    dead_grid=np.ones((11,11),dtype=np.uint8); dead_grid[5,1:6]=0; dead=local_exit_score(GridEnvironment(dead_grid),(5,5),radius=3); assert dead<intersection
