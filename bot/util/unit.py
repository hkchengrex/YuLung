from dataclasses import dataclass
from typing import List

@dataclass
class Unit:
    unit_id: int
    name: str
    cargo_size: int             # Number of cargo slots it occupies in transports.
    mineral_cost: int
    vespene_cost: int
    food_required: float
    food_provided: float
    ability_id: int             # The ability that builds this unit.
    build_time: float
    sight_range: float

    tech_alias: int
    unit_alias: int

    tech_requirement: List[int]
    require_attached: bool

    # Subject to change on upgrade
    attributes: List[str]
    movement_speed: float
    armor: float
    weapons: list

