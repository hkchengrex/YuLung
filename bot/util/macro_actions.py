import enum


class AutoNumber(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class MacroAction(AutoNumber):
    ATTACK_EXP_0 = ()
    ATTACK_EXP_1 = ()
    ATTACK_EXP_2 = ()
    ATTACK_EXP_3 = ()

    ELIMINATE = ()

    BUILD_EXPANSION = ()
    SCOUT_ONCE = ()
    BUILD_EXTRACTOR = ()

    MAKE_SPAWNING_POOL = ()
    MAKE_ROACH_WARREN = ()
    MAKE_BANELING_NEST = ()
    MAKE_LAIR = ()
    MAKE_HYDRALISK_DEN = ()
    MAKE_LURKER_DEN = ()
    MAKE_INFESTATION_PIT = ()
    MAKE_SPIRE = ()
    MAKE_NYDUS_NETWORK = ()
    MAKE_HIVE = ()
    MAKE_ULTRALISK_CAVERN = ()
    MAKE_GREATER_SPIRE = ()

    BUILD_DRONE = ()
    BUILD_OVERLORD = ()
    BUILD_ZERGLING = ()
