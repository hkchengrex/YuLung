from gym.envs.registration import register

register(
    id='YuLungSimple64-v0',
    entry_point='envs.yulung_env:YuLungSimple64Env',
    kwargs={}
)

register(
    id='YuLungAbiogenesisEnv-v0',
    entry_point='envs.yulung_env:YuLungAbiogenesisEnv',
    kwargs={}
)