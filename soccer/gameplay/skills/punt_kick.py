import single_robot_composite_behavior
import skills.pivot_kick
import behavior
import skills.aim
import skills.capture
import role_assignment
import robocup
import constants
import main
from enum import Enum


# PuntKick executes a PivotKick - it always uses a
# high powered chip towards the opponent's goal
class PuntKick(single_robot_composite_behavior.SingleRobotCompositeBehavior):
    class State(Enum):
        punting = 1

    def __init__(self):
        super().__init__(continuous = True)

        self.add_state(PuntKick.State.punting, behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
                            PuntKick.State.punting, lambda: True,
                            'immediately')

        self.add_transition(
            PuntKick.State.punting, behavior.Behavior.State.completed,
            lambda: self.subbehavior_with_name('kick').state == behavior.Behavior.State.completed,
            'punt completed')

    def on_enter_punting(self):
        print("Punting")
        kicker = skills.pivot_kick.PivotKick()
        kickpower = (main.ball().pos - constants.Field.TheirGoalSegment.center()).mag() / 8
        # This shouldn't really be an issue, but it does prevent misfires or
        # accidental squib kicks.
        if (kickpower < 0.2):
            kickpower = 0.2

        # Prevents the robot from kicking harder than it can and creating a black hole
        if (kickpower > 1.0):
            kickpower = 1.0
        kicker.chip_power = kickpower
        kicker.use_chipper = True

        # We use very loose thresholds since our goal is to quickly get rid of the ball
        # TODO: Tune me
        # kicker.aim_params['error_threshold'] = 0.6
        # kicker.aim_params['max_steady_ang_vel'] = 9.0
        # kicker.aim_params['min_steady_duration'] = 0.5
        # kicker.aim_params['desperate_timeout'] = 6.0
        self.add_subbehavior(kicker, 'kick', required=False)

    def on_exit_punting(self):
        print("Punted")
        self.remove_subbehavior_with_name('kick')
