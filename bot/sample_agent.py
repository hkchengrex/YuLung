import numpy as np

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

from pysc2.lib import raw_units as ru

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL  # beacon/minerals
_PLAYER_ENEMY = features.PlayerRelative.ENEMY

FUNCTIONS = actions.FUNCTIONS

class MoveToBeacon(base_agent.BaseAgent):
  """An agent specifically for solving the MoveToBeacon map using the raw interface."""

  def step(self, obs):
    super(MoveToBeacon, self).step(obs)

    raw_units = [ru.RawUnit(u) for u in obs.observation.raw_units]
    for u in raw_units:
      if u.owner == ru.PLAYER_NEUTRAL:
        target = u.pos
      else:
        marine = u.tag

    return FUNCTIONS.Move_raw("now", target, marine)

class CollectMineralShards(base_agent.BaseAgent):
  """An agent for solving the CollectMineralShards map with feature units using the raw interface."""

  def reset(self):
    super(CollectMineralShards, self).reset()

    self.minerals = []
    self.marines = []
    self.marines_target = []

  def step(self, obs):
    super(CollectMineralShards, self).step(obs)

    raw_units = [ru.RawUnit(u) for u in obs.observation.raw_units]
    if len(self.marines) == 0:
      for u in raw_units:
        if u .owner != ru.PLAYER_NEUTRAL:
          self.marines.append(u)
          self.marines_target.append(0)

    if len(self.minerals) == 0:
      self.minerals = []
      for u in raw_units:
        if u .owner == ru.PLAYER_NEUTRAL:
          self.minerals.append(u)

    for i, m in enumerate(self.marines):
      if self.marines_target[i] not in raw_units:
        self.marines_target[i] = 0

      if self.marines_target[i] == 0 and len(self.minerals) > 0:
        # No order, we will give it one
        # Find closest mineral and send the marine there
        dist = [m.dist_to(x) for x in self.minerals]
        min_idx = np.argmin(dist)
        tar = self.minerals[min_idx]
        self.marines_target[i] = tar.tag
        del self.minerals[min_idx]
        return FUNCTIONS.Move_raw("now", tar.pos, m.tag)

    return FUNCTIONS.no_op()