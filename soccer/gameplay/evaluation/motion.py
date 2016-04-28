import main
import robocup
import constants
import math

max_robot_speed = robocup.MotionContraints.MaxRobotSpeed.value()
max_robot_accel = robocup.MotionContraints.MaxRobotAccel.value()

## Returns the minimum time to reach the given point for the given robot.
# This assumes that the robot doesn't slow down to reach the point, that it doesn't need to avoid any obstacles, and it follows our motion constraints
def timeToPoint(cur_velocity, final_point):
	if cur_robot == None
		return float("inf")
	#Distance from robot to evaluation point
	path_dist = cur_robot.pos.distTo(final_point)
	#Time til max velocity is reached
	max_v_time = (max_robot_speed - cur_robot.vel.mag()) / max_robot_accel
	#Distance covered while the robot accelerates to max velocity
	max_v_dist = .5 * max_robot_accel * max_v_time^2 + cur_robot.vel.mag() * max_v_time
	#If the robot can reach the point entirely 
	if path_dist < max_v_dist:
		#Return time based on the equation: x(t) = .5*a*t^2 + vi*t + xi
		return (-cur_robot.vel.mag() + math.sqrt(cur_robot.vel.magsq() + 2 * max_robot_accel * path_dist)) / max_robot_accel
	else:
		return max_v_time + (path_dist - max_v_dist) / max_robot_speed


## Returns the minimum time to reach the ball for the given robot. 
# This assumes the robot does not slow down to retrieve the ball. It also
# assumes that the robot is on of ours, following our max acceleration and velocity values.
# In addition, it assumes the ball will continue along its current path.
def timeToBall(cur_robot):
	if cur_robot == None:
		return float("inf")
	robot_vel = cur_robot.vel
	ball_vel = robocup.main.vel

