import enum
from bot.util.static_units import *


class CombatAction(enum.IntEnum):
    ATTACK_EXP_0 = 0
    ATTACK_EXP_1 = 1
    ATTACK_EXP_2 = 2
    ATTACK_EXP_3 = 3

    MOVE_EXP_0 = 4
    MOVE_EXP_1 = 5
    MOVE_EXP_2 = 6
    MOVE_EXP_3 = 7

    ELIMINATE = 8


class ConstructionAction(enum.IntEnum):
    NO_OP = 0

    BUILD_EXPANSION = 1
    BUILD_EXTRACTOR = 2

    # Some units are skipped.
    # No point building caster when you cannot cast.
    BUILD_DRONE = 3
    BUILD_OVERLORD = 4
    BUILD_ZERGLING = 5
    BUILD_ROACH = 6
    BUILD_QUEEN = 7
    BUILD_HYDRALISK = 8
    # BUILD_SWARM_HOST = 9
    BUILD_MUTALISK = 9
    BUILD_CORRUPTOR = 10
    BUILD_ULTRALISK = 11
    BUILD_OVERSEER = 12


CONSTRUCTION_UNITS_MAPPING = {
    ConstructionAction.BUILD_DRONE: UNITS[UnitID.Drone],
    ConstructionAction.BUILD_OVERLORD: UNITS[UnitID.Overlord],
    ConstructionAction.BUILD_ZERGLING: UNITS[UnitID.Zergling],
    ConstructionAction.BUILD_ROACH: UNITS[UnitID.Roach],
    ConstructionAction.BUILD_QUEEN: UNITS[UnitID.Queen],
    ConstructionAction.BUILD_HYDRALISK: UNITS[UnitID.Hydralisk],
    # ConstructionAction.BUILD_SWARM_HOST: UNITS[UnitID.SwarmHostMP],
    ConstructionAction.BUILD_MUTALISK: UNITS[UnitID.Mutalisk],
    ConstructionAction.BUILD_CORRUPTOR: UNITS[UnitID.Corruptor],
    ConstructionAction.BUILD_ULTRALISK: UNITS[UnitID.Ultralisk],
    ConstructionAction.BUILD_OVERSEER: UNITS[UnitID.Overseer],
}


class TechAction(enum.IntEnum):
    NO_OP = 0

    MAKE_SPAWNING_POOL = 1
    MAKE_EVOLUTION_CHAMBER = 2
    MAKE_ROACH_WARREN = 3
    # MAKE_BANELING_NEST = ()
    MAKE_LAIR = 4
    MAKE_HYDRALISK_DEN = 5
    # MAKE_LURKER_DEN = ()
    MAKE_INFESTATION_PIT = 6
    MAKE_SPIRE = 7
    # MAKE_NYDUS_NETWORK = ()
    MAKE_HIVE = 8
    MAKE_ULTRALISK_CAVERN = 9
    # MAKE_GREATER_SPIRE = ()


TECH_UNITS_MAPPING = {
    TechAction.MAKE_SPAWNING_POOL: UNITS[UnitID.SpawningPool].unit_id,
    TechAction.MAKE_EVOLUTION_CHAMBER: UNITS[UnitID.EvolutionChamber].unit_id,
    TechAction.MAKE_ROACH_WARREN: UNITS[UnitID.RoachWarren].unit_id,
    TechAction.MAKE_LAIR: UNITS[UnitID.Lair].unit_id,
    TechAction.MAKE_HYDRALISK_DEN: UNITS[UnitID.HydraliskDen].unit_id,
    TechAction.MAKE_INFESTATION_PIT: UNITS[UnitID.InfestationPit].unit_id,
    TechAction.MAKE_SPIRE: UNITS[UnitID.Spire].unit_id,
    TechAction.MAKE_HIVE: UNITS[UnitID.Hive].unit_id,
    TechAction.MAKE_ULTRALISK_CAVERN: UNITS[UnitID.UltraliskCavern].unit_id,
}


class MiscAction(enum.IntEnum):
    NO_OP = 0
    SCOUT_ONCE = 1


# Mineral-to-gas ratio
class ResourcesAction(enum.IntEnum):
    MG_RATIO_000 = 0
    MG_RATIO_025 = 1
    MG_RATIO_050 = 2
    MG_RATIO_075 = 3
    MG_RATIO_100 = 4


RESOURCES_RATIO_MAPPING = {
    ResourcesAction.MG_RATIO_000: 0.00,
    ResourcesAction.MG_RATIO_025: 0.25,
    ResourcesAction.MG_RATIO_050: 0.50,
    ResourcesAction.MG_RATIO_075: 0.75,
    ResourcesAction.MG_RATIO_100: 1.00,
}


class ConstructAmountAction(enum.IntEnum):
    BUILD_1 = 0
    BUILD_3 = 1
    BUILD_5 = 2


CONSTRUCT_AMOUNT_MAPPING = {
    ConstructAmountAction.BUILD_1: 1,
    ConstructAmountAction.BUILD_3: 3,
    ConstructAmountAction.BUILD_5: 5,
}
