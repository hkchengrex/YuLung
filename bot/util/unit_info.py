import enum
from dataclasses import dataclass
from typing import List

from s2clientprotocol import data_pb2 as sc_data


class Attribute(enum.IntEnum):
    Light = 1
    Armored = 2
    Biological = 3
    Mechanical = 4
    Robotic = 5
    Psionic = 6
    Massive = 7
    Structure = 8
    Hover = 9
    Heroic = 10
    Summoned = 11

    def gen_py(self):
        return 'Attribute.' + self.name


class Alliance(enum.IntEnum):
  Self = 1
  Ally = 2
  Neutral = 3
  Enemy = 4



@dataclass
class Weapon:
    type: int
    damage: float
    attacks: int
    range: float
    speed: float
    damage_bonus: dict

    @classmethod
    def from_proto(cls, weapon_proto: sc_data.Weapon):
        damage_bonus = dict()
        for db in weapon_proto.damage_bonus:
            damage_bonus[db.attribute] = db.bonus

        return cls(
            type=weapon_proto.type,
            damage=weapon_proto.damage,
            attacks=weapon_proto.attacks,
            range=weapon_proto.range,
            speed=weapon_proto.speed,
            damage_bonus=damage_bonus
        )

    def gen_py(self):
        return ('Weapon('
                'type=%d, damage=%f, '
                'attacks=%d, range=%f, '
                'speed=%f, damage_bonus=%s)' %
                (self.type, self.damage, self.attacks,
                 self.range, self.speed, repr(self.damage_bonus)))


@dataclass
class UnitType:
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

    tech_alias: List[int]
    unit_alias: int

    tech_requirement: int
    require_attached: bool

    # Subject to change on upgrade
    attributes: list
    movement_speed: float
    armor: float
    weapons: list

    @classmethod
    def from_proto(cls, unit_proto: sc_data.UnitTypeData):
        return cls(
            unit_id=unit_proto.unit_id,
            name=unit_proto.name,
            cargo_size=unit_proto.cargo_size,
            mineral_cost=unit_proto.mineral_cost,
            vespene_cost=unit_proto.vespene_cost,
            food_required=unit_proto.food_required,
            food_provided=unit_proto.food_provided,
            ability_id=unit_proto.ability_id,
            build_time=unit_proto.build_time,
            sight_range=unit_proto.sight_range,

            tech_alias=list(unit_proto.tech_alias),
            unit_alias=unit_proto.unit_alias,
            tech_requirement=unit_proto.tech_requirement,
            require_attached=unit_proto.require_attached,

            attributes=[Attribute(a) for a in unit_proto.attributes],
            movement_speed=unit_proto.movement_speed,
            armor=unit_proto.armor,
            weapons=[Weapon.from_proto(w) for w in unit_proto.weapons],
        )

    def gen_py(self):

        tech_alias = '[' + \
                     ', '.join([str(a) for a in self.tech_alias]) + \
                     ']'

        attributes = '[' + \
                     ', '.join([a.gen_py() for a in self.attributes]) + \
                     ']'

        weapons = '[' + \
                  ', '.join([w.gen_py() for w in self.weapons]) + \
                  ']'

        return('UnitType(unit_id=%d, name=\'%s\', cargo_size=%d, \n'
              'mineral_cost=%d, vespene_cost=%d, \n'
              'food_required=%f, food_provided=%f, \n'
              'ability_id=%d, build_time=%d, \n'
              'sight_range=%f, tech_alias=%s, \n'
              'unit_alias=%d, tech_requirement=%d, \n'
              'require_attached=%s, attributes=%s, \n'
              'movement_speed=%f, armor=%f, weapons=%s)\n\n'
              % (self.unit_id, self.name, self.cargo_size,
                 self.mineral_cost, self.vespene_cost,
                 self.food_required, self.food_provided,
                 self.ability_id, self.build_time,
                 self.sight_range, tech_alias,
                 self.unit_alias, self.tech_requirement,
                 str(self.require_attached), attributes,
                 self.movement_speed, self.armor, weapons))


