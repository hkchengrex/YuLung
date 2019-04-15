# YuLung
YuLung (雨龍) - A Zerg StarCraft II agent.

Depends on a modded version of pysc2 (https://github.com/silver-rush/pysc2) that
exposes the raw interface.

Current training:
`
python test_ppo.py --env-name "YuLungSimple64-v0" --algo ppo
 --use-gae --lr 2.5e-4 --clip-param 0.1 --value-loss-coef 0.5
 --num-processes 16 --num-steps 64 --num-mini-batch 8
 --save-interval 100 --log-interval 1 --use-linear-lr-decay
 --entropy-coef 0.01 expr_id_1
`

Running the actual bot:

`python -m pysc2.bin.agent --map "Simple64" 
--agent bot.agent.YuLungAgent --agent_race zerg
 --feature_screen_size 128 --feature_minimap_size 25 
 --camera_width 142
`

More complex case:

`python -m pysc2.bin.agent --map "Abiogenesis" 
--agent bot.agent.YuLungAgent --agent_race zerg
 --feature_screen_size 128 --feature_minimap_size 25 
 --camera_width 142`

Running the test bot: 

`python -m pysc2.bin.agent --map CollectMineralShards --agent bot.sample_agent.CollectMineralShards`

To generate static unit information (Might need manual clean up for pygame output):

`python -m bot.util.gen_units_data | tee bot/util/static_units.py`
