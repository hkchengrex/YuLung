from envs.base_env import SC2BaseEnv
from envs.move_env import SimpleMovementEnv, CollectMineralShardsEnv

from gym.envs.registration import register

register(
    id='CollectMineralShards-v0',
    entry_point='envs.move_env:CollectMineralShardsEnv',
    kwargs={}
)

register(
    id='YuLungSimple64-v0',
    entry_point='envs.yulung_env:YuLungSimple64Env',
    kwargs={}
)