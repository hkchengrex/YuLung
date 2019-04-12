# YuLung
YuLung (雨龍) - A Zerg StarCraft II agent.

Depends on a modded version of pysc2 (https://github.com/silver-rush/pysc2) that
exposes the raw interface.

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
