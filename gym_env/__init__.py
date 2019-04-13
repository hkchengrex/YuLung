from gym_env.base_env import SC2BaseEnv
from gym_env.move_env import SimpleMovementEnv, CollectMineralShardsEnv

from gym.envs.registration import register

register(
    id='CollectMineralShards-v0',
    entry_point='gym_env.move_env:CollectMineralShardsEnv',
    kwargs={}
)

