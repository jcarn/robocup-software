import main
import robocup
import constants
import math

max_speed = robocup.MotionConstraints.MaxRobotSpeed.value
max_accel = robocup.MotionConstraints.MaxRobotAccel.value

# Returns the minimum time to reach the given point for the given robot. 
def timeToPoint(final_point, cur_robot = None, cur_velocity = None, cur_pos = None):
	#Checks to make the time can be calculated. You need either a robot or a current velocity and posistion. You always needa final point to calculate the time to.
	if ((cur_robot == None and (cur_velocity == None or cur_pos == None)) or final_point == None):
		return float("inf")
	elif (not cur_robot == None):
		cur_velocity = cur_robot.vel
		cur_pos = cur_robot.pos
	path = final_point - cur_pos
	#Projection of our velocity onto the path, giving us a vector representing our veloicty towards the final point.
	proj_vel = path * (path.dot(cur_velocity) / path.magsq())
	#xf = .5*a*t^2 + vi*t + x0
	#0 = .5*a*t^2 + vi*t + (x0 - xf)
	#t = (-vi + sqrt(vi^2 - 4 * (.5*a*(x0-xf)))) / 2*(.5*a)
	#t = (-vi + sqrt(vi^2 +2*a*xf)) / a 
	est_time = (-1*proj_vel.mag() + math.sqrt(proj_vel.magsq() + 2 * max_accel * path.mag())) / max_accel
	return est_time

# Returns the minimum time to reach a moving object for the given robot. This uses the timeToPoint method above, but passes it the relative velocity of the robot to the moving point. The point could be the ball, or another robot.
def timeToMovingPoint(moving_point_pos, moving_point_vel, cur_robot):
	#All parameters are necesarry, can't calculate without them
	if cur_robot == None or moving_point_vel == None or moving_point_pos == None:
		return float("inf")
	#We don't give it the robot because we want it to use our relative velocity instead of the robot's actual velocity
	return timeToPoint(moving_point_pos, cur_velocity = (cur_robot.vel - moving_point_vel), cur_pos = cur_robot.pos)

def timeToBall(cur_robot):
	return timeToMovingPoint(main.ball().pos, main.ball().vel, cur_robot)

