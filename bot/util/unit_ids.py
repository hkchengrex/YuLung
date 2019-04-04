from pysc2.lib.units import Neutral

from bot.util.static_units import UNITS, UnitID

"""
This file contains lists of useful unit ids
"""

# Ids for all kinds of mineral patches
MINERAL_UNIT_ID = [Neutral.MineralField, Neutral.MineralField750,
                   Neutral.RichMineralField, Neutral.RichMineralField750,
                   Neutral.BattleStationMineralField, Neutral.BattleStationMineralField750,
                   Neutral.LabMineralField, Neutral.LabMineralField750,
                   Neutral.PurifierMineralField, Neutral.PurifierMineralField750,
                   Neutral.PurifierRichMineralField, Neutral.PurifierRichMineralField750]

# Ids for all gas patches
GAS_UNIT_ID = [Neutral.VespeneGeyser, Neutral.RichVespeneGeyser,
               Neutral.ProtossVespeneGeyser, Neutral.PurifierVespeneGeyser,
               Neutral.ShakurasVespeneGeyser]

# Ids for everything that does not move
ALL_BUILDING_ID = []
def _init_building_ids():
    global ALL_BUILDING_ID
    ALL_BUILDING_ID = [
        u for _, u in UNITS.items() if u.movement_speed < 1e-3
    ]
_init_building_ids()

ZERG_BUILDINGS_TYPE = [
    UNITS[UnitID.Hatchery],
    UNITS[UnitID.Extractor],
    UNITS[UnitID.SpawningPool],
    UNITS[UnitID.EvolutionChamber],
    UNITS[UnitID.SpineCrawler],
    UNITS[UnitID.SporeCrawler],
    UNITS[UnitID.RoachWarren],
    UNITS[UnitID.BanelingNest],
    UNITS[UnitID.Lair],
    UNITS[UnitID.HydraliskDen],
    UNITS[UnitID.LurkerDenMP],
    UNITS[UnitID.InfestationPit],
    UNITS[UnitID.Spire],
    UNITS[UnitID.NydusNetwork],
    UNITS[UnitID.NydusCanal],
    UNITS[UnitID.Hive],
    UNITS[UnitID.GreaterSpire],
    UNITS[UnitID.CreepTumor],
]

ZERG_BASES = [
    UNITS[UnitID.Hatchery],
    UNITS[UnitID.Lair],
    UNITS[UnitID.Hive],
]

FROM_LARVA_TYPE = [
    UNITS[UnitID.Drone],
    UNITS[UnitID.Zergling],
    UNITS[UnitID.Hydralisk],
    UNITS[UnitID.Roach],
    UNITS[UnitID.Infestor],
    UNITS[UnitID.SwarmHostMP],
    UNITS[UnitID.Ultralisk],
    UNITS[UnitID.Overlord],
    UNITS[UnitID.Mutalisk],
    UNITS[UnitID.Corruptor],
    UNITS[UnitID.Viper],
]

FROM_DRONE_TYPE = [
    UNITS[UnitID.Hatchery],
    UNITS[UnitID.Extractor],
    UNITS[UnitID.SpawningPool],
    UNITS[UnitID.EvolutionChamber],
    UNITS[UnitID.SpineCrawler],
    UNITS[UnitID.SporeCrawler],
    UNITS[UnitID.RoachWarren],
    UNITS[UnitID.BanelingNest],
    UNITS[UnitID.HydraliskDen],
    UNITS[UnitID.LurkerDenMP],
    UNITS[UnitID.InfestationPit],
    UNITS[UnitID.Spire],
    UNITS[UnitID.NydusNetwork],
    UNITS[UnitID.UltraliskCavern],
]
