import enum


class AutoNumber(enum.IntEnum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class CombatAction(AutoNumber):
    ATTACK_EXP_0 = ()
    ATTACK_EXP_1 = ()
    ATTACK_EXP_2 = ()
    ATTACK_EXP_3 = ()

    MOVE_EXP_0 = ()
    MOVE_EXP_1 = ()
    MOVE_EXP_2 = ()
    MOVE_EXP_3 = ()

    ELIMINATE = ()


class ConstructionAction(AutoNumber):
    NO_OP = ()

    BUILD_EXPANSION = ()
    BUILD_EXTRACTOR = ()

    # Some units are skipped.
    # No point building caster when you cannot cast.
    BUILD_DRONE = ()
    BUILD_OVERLORD = ()
    BUILD_ZERGLING = ()
    BUILD_ROACH = ()
    BUILD_QUEEN = ()
    BUILD_HYDRALISK = ()
    BUILD_SWARM_HOST = ()
    BUILD_MUTALISK = ()
    BUILD_CORRUPTOR = ()
    BUILD_ULTRALISK = ()
    BUILD_OVERSEER = ()


class TechAction(AutoNumber):
    NO_OP = ()

    MAKE_SPAWNING_POOL = ()
    MAKE_ROACH_WARREN = ()
    # MAKE_BANELING_NEST = ()
    MAKE_LAIR = ()
    MAKE_HYDRALISK_DEN = ()
    # MAKE_LURKER_DEN = ()
    MAKE_INFESTATION_PIT = ()
    MAKE_SPIRE = ()
    # MAKE_NYDUS_NETWORK = ()
    MAKE_HIVE = ()
    MAKE_ULTRALISK_CAVERN = ()
    # MAKE_GREATER_SPIRE = ()


class MiscAction(AutoNumber):
    NO_OP = ()
    SCOUT_ONCE = ()

