import main
import robocup
import constants
import math

max_speed = robocup.MotionContraints.MaxRobotSpeed.value()
max_accel = robocup.MotionContraints.MaxRobotAccel.value()

# Returns the minimum time to reach the given point for the given robot. 
def timeToPoint(cur_robot, cur_velocity, cur_pos, final_point):
	#Checks to make the time can be calculated. You need either a robot or a current velocity and posistion. You always needa final point to calculate the time to.
	if (cur_robot == None and (cur_velocity == None or cur_pos = None)) or final_point == None:
		return float("inf")
	elif not cur_robot == None:
		cur_velocity = cur_robot.vel
		cur_pos = cur_robot.pos
	path = final_point - cur_pos
	#Projection of our velocity onto the path, giving us a vector representing our veloicty towards the final point.
	proj_vel = path.dot(cur_velocity) / path.magsq() * path
	return (-1*proj_vel.mag() + math.sqrt(proj_vel.magsq() + 2 * max_accel * path.mag()) / max_accel


# Returns the minimum time to reach a moving object for the given robot. This uses the timeToPoint method above, but passes it the relative velocity of the robot to the moving point. The point could be the ball, or another robot.
def timeToMovingPoint(cur_robot, moving_point_vel, moving_point_pos):
	#All parameters are necesarry, can't calculate without them
	if cur_robot == None or moving_point_vel == None or moving_point_pos == None:
		return float("inf")
	#We don't give it the robot because we want it to use our relative velocity instead of the robot's actual velocity
	timeToPoint(None, (cur_robot.vel - moving_point_vel), cur_robot.pos, moving_point_pos)

