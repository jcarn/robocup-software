import single_robot_composite_behavior
import behavior
import skills.move
import skills.capture
import skills.punt_kick
import constants
import robocup
import main
from enum import Enum
import math
#import evaluation.motion


## Defender behavior meant to be coordinated in a defense tactic
# The regular defender does a lot of calculations and figures out where it should be
# This defender lets someone else (the Defense tactic) handle calculations and blocks things based on that
class SubmissiveDefender(
        single_robot_composite_behavior.SingleRobotCompositeBehavior):
    class State(Enum):
        ## gets between a particular opponent and the goal.  stays closer to the goal
        marking = 1
        # TODO: add clear state to get and kick a free ball
        retrieving = 2
        clearing = 3

    def __init__(self):
        super().__init__(continuous=True)
        self._block_object = None
        # self._opponent_avoid_threshold = 2.0
        self._defend_goal_radius = 1.4

        self.block_line = None

        for state in SubmissiveDefender.State:
            self.add_state(state, behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
                            SubmissiveDefender.State.marking, lambda: True,
                            "immediately")

        # Robot is marking by default. If the situation dictates that the ball
        # needs cleared, the robot retrieves the ball. If the robot retrieves
        # the ball, it then clears it and resumes marking. Otherwise, it resumes
        # marking without clearing. As it stands, retrieving and clearing don't
        # need to be seperate, but there could be utility in knowing and reacting
        # to the success of the retrieval.
        self.add_transition(SubmissiveDefender.State.marking,
                            SubmissiveDefender.State.retrieving,
                            lambda: should_retrieve(), "retrieve")
        self.add_transition(SubmissiveDefender.State.retrieving,
                            SubmissiveDefender.state.clearing,
                            lambda: self.robot.has_ball(),
                            "retrieved and clearing")
        self.add_transition(SubmissiveDefender.State.retrieving,
                            SubmissiveDefender.state.marking,
                            lambda: not should_retrieve(), "failed retrieve")
        self.add_transition(SubmissiveDefender.State.clearing,
                            SubmissiveDefender.State.marking,
                            lambda: not self.robot.has_ball(), "cleared")

    ## Returns True if the defender should clear a ball. It detirmines this by
    # evaluating the ratio between the estimated time it takes an opponent to reach
    # the ball and the estimated time it takes our robot to reach the ball. If the
    # ratio is above some threshold, the robot should clear the ball. The threshold
    # ratio is completely arbitrary and requires tuning.
    def should_retrieve(self):
        print("Implement me!")
        #Find the most threatening bot and its min time to ball
        threat_bot, threat_time = None, float("inf")
        for bot in main.their_robots():
            if bot.visible:
                bot_time = (
                    main.ball.pos() -
                    bot.pos()).mag()  #evaluation.motion.timeToBall(bot)
                if bot_time < threat_time:
                    threat_time, threat_bot = bot_time, bot

        #Compressed code I was messing with, no idea if it works. Delete before commit.
        #threat_time = bot_time if threat_time > (bot_time = evaluation.motion.timeToBall(bot)) for bot in main.their_robots())

        #Define ratio. TODO: Tune this
        threshold_ratio = 2.0

        #Evaluates the ratio and detirmines if we have enough time to clear
        #return True if threat_bot != None and threat_time / evaluation.motion.timeToBall(self.robot) > threshold_ratio else return False
        return (True if
                (threat_bot != None and threat_time /
                 (main.ball.pos() - self.robot.pos()).mag() > threshold_ratio)
                else False)

    ## the line we should be on to block
    # The defender assumes that the first endpoint on the line is the source of
    # the threat it's blocking and makes an effort to face towards it
    @property
    def block_line(self):
        return self._block_line

    @block_line.setter
    def block_line(self, value):
        self._block_line = value

        # we move somewhere along this arc to mark our 'block_line'
        arc_left = robocup.Arc(
            robocup.Point(-constants.Field.GoalFlat / 2, 0),
            constants.Field.ArcRadius + constants.Robot.Radius * 2,
            math.pi / 2, math.pi)
        arc_right = robocup.Arc(
            robocup.Point(constants.Field.GoalFlat / 2, 0),
            constants.Field.ArcRadius + constants.Robot.Radius * 2, 0,
            math.pi / 2)
        seg = robocup.Segment(
            robocup.Point(
                -constants.Field.GoalFlat / 2,
                constants.Field.ArcRadius + constants.Robot.Radius * 2),
            robocup.Point(
                constants.Field.GoalFlat / 2,
                constants.Field.ArcRadius + constants.Robot.Radius * 2))

        default_pt = seg.center()

        if self._block_line != None:
            # main.system_state().draw_line(self._block_line, constants.Colors.White, "SubmissiveDefender")
            main.system_state().draw_circle(
                self._block_line.get_pt(0), 0.1, constants.Colors.White,
                "SubmissiveDefender")

            threat_point = self._block_line.get_pt(0)

            intersection_center = seg.line_intersection(self._block_line)

            if threat_point.x < 0:
                intersections_left = arc_left.intersects_line(self._block_line)
                if len(intersections_left) > 0:
                    self._move_target = max(intersections_left,
                                            key=lambda p: p.y)
                elif intersection_center is not None:
                    self._move_target = intersection_center
                else:
                    self._move_target = default_pt
            elif threat_point.x >= 0:
                intersections_right = arc_right.intersects_line(
                    self._block_line)
                if len(intersections_right) > 0:
                    self._move_target = max(intersections_right,
                                            key=lambda p: p.y)
                elif intersection_center is not None:
                    self._move_target = intersection_center
                else:
                    self._move_target = default_pt
        else:
            self._move_target = default_pt

    ## where the bot plans to move in order to block the block_line
    @property
    def move_target(self):
        return self._move_target

    def on_enter_marking(self):
        move = skills.move.Move()
        self.add_subbehavior(move, 'move', required=False)  # FIXME: priority

    def on_enter_retrieving(self):
        print("Implement me!")
        #Add relevant skills, some of this this might be bypassed with a tactic
        self.add_subbehavior(skills.capture.Capture(),
                             'capture',
                             required=True)

    def on_enter_clearing(self):
        self.add_subbehavior(skills.punt_kick.PuntKick(),
                             'punt',
                             required=True)

    def execute_running(self):
        self.robot.set_avoid_opponents(False)

    ## move to a position to block the 'block_line'
    # if no block_line is specified, blocks the ball
    def execute_marking(self):
        move = self.subbehavior_with_name('move')
        move.pos = self.move_target

        arc_left = robocup.Arc(
            robocup.Point(-constants.Field.GoalFlat / 2, 0),
            constants.Field.ArcRadius + constants.Robot.Radius * 2,
            math.pi / 2, math.pi)
        arc_right = robocup.Arc(
            robocup.Point(constants.Field.GoalFlat / 2, 0),
            constants.Field.ArcRadius + constants.Robot.Radius * 2, 0,
            math.pi / 2)
        seg = robocup.Segment(
            robocup.Point(
                -constants.Field.GoalFlat / 2,
                constants.Field.ArcRadius + constants.Robot.Radius * 2),
            robocup.Point(
                constants.Field.GoalFlat / 2,
                constants.Field.ArcRadius + constants.Robot.Radius * 2))

        if move.pos != None:
            main.system_state().draw_circle(move.pos, 0.02,
                                            constants.Colors.Green, "Mark")
            main.system_state().draw_segment(seg, constants.Colors.Green,
                                             "Mark")
            main.system_state().draw_arc(arc_left, constants.Colors.Green,
                                         "Mark")
            main.system_state().draw_arc(arc_right, constants.Colors.Green,
                                         "Mark")

        # make the defender face the threat it's defending against
        if self.robot != None and self.block_line != None:
            self.robot.face(self.block_line.get_pt(0))

    def execute_clearing(self):
        #Find Ball
        #Move to Ball
        #Pick up Ball?
        #Clear ball by passing it to offense
        #Auxiliarry: Draw stuff, don't break things
        #end
        print("Implement me!")

    def on_exit_marking(self):
        self.remove_subbehavior('move')

    def on_exit_retrieving(self):
        self.remove_subbehavior('capture')

    def on_exit_clearing(self):
        print("Implement me!")
        #Remove skills added earlier
        #Auxilarry: Consider reporting success of clearing?

    def role_requirements(self):
        reqs = super().role_requirements()
        # FIXME: be smarter
        return reqs
