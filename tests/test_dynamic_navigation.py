from recovernav.execution import run_scenario
from recovernav.robot import NavigationState, Robot
from recovernav.scenarios import make_scenario

def test_dynamic_obstacle_invalidates_path():
    s=make_scenario("corridor"); robot=Robot(s.environment.copy(),s.start,s.goal); assert robot.plan(); assert s.dynamic_obstacle in robot.current_path; robot.env.add_dynamic_obstacle(s.dynamic_obstacle); assert robot.path_blocked()

def test_replanning_starts_from_current_position():
    s=make_scenario("open_room"); robot=Robot(s.environment.copy(),s.start,s.goal); robot.plan(); robot.step(); robot.step(); current=robot.position; block=robot.current_path[robot._path_index+3]; robot.env.add_dynamic_obstacle(block); robot.step(); assert robot.current_path[0]==current; assert robot.replans==1

def test_robot_reaches_goal_when_alternative_exists():
    robot,metrics=run_scenario(make_scenario("open_room"),"baseline"); assert metrics.success; assert robot.state==NavigationState.GOAL_REACHED; assert metrics.replans>=1

def test_robot_fails_cleanly_when_no_route_exists():
    robot,metrics=run_scenario(make_scenario("corridor"),"baseline"); assert not metrics.success; assert robot.state==NavigationState.FAILED

def test_paired_scenarios_identical():
    s=make_scenario("two_routes",seed=7); b,_=run_scenario(s,"baseline"); r,_=run_scenario(s,"recovernav"); assert b.env.shape==r.env.shape; assert s.start==b.trajectory[0]==r.trajectory[0]; assert s.goal==b.goal==r.goal
