import play
import behavior
import skills.punt_kick
import skills.move
import enum
import main
import constants
import robocup


# this test repeatedly runs the PivotKick behavior aimed at our goal
class TestPuntKick(play.Play):
    def __init__(self):
        super().__init__(continuous=True)

        self.add_transition(behavior.Behavior.State.start,
                            behavior.Behavior.State.running, lambda: True,
                            'immediately')

        punt = skills.punt_kick.PuntKick()
        self.add_subbehavior(punt, 'punt', required=False)

    def execute_running(self):
        punt = self.subbehavior_with_name('punt')
        if punt.is_done_running():
            punt.restart()
