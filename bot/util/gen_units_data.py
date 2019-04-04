# Reference from gen_units.py of pysc2

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl import app
from pysc2 import maps
from pysc2 import run_configs
from pysc2.lib import static_data
from s2clientprotocol import common_pb2 as sc_common
from s2clientprotocol import sc2api_pb2 as sc_pb

from .unit_info import UnitType


def get_data():
    """Get the game's static data from an actual game."""
    run_config = run_configs.get()

    with run_config.start(want_rgb=False) as controller:
        m = maps.get("Sequencer")  # Arbitrary ladder map.
        create = sc_pb.RequestCreateGame(local_map=sc_pb.LocalMap(
            map_path=m.path, map_data=m.data(run_config)))
        create.player_setup.add(type=sc_pb.Participant)
        create.player_setup.add(type=sc_pb.Computer, race=sc_common.Random,
                                difficulty=sc_pb.VeryEasy)
        join = sc_pb.RequestJoinGame(race=sc_common.Random,
                                     options=sc_pb.InterfaceOptions(raw=True))

        controller.create_game(create)
        controller.join_game(join)
        return controller.data_raw()


def gen_header(class_name):
    print('# Auto-generated.')
    print('import enum')
    print()
    print('class %s(enum.IntEnum):' % class_name)
    print()


def generate_py_units(data):
    """
    Generate the list of units in units.py.
    Also re-parametrize IDs.
    """
    gen_header('UnitID')
    units = []
    for unit in sorted(data.units, key=lambda a: a.name):
        if unit.unit_id in static_data.UNIT_TYPES:
            print('    %s = %d' % (unit.name, len(units)))
            units.append(unit)
            # print(type(list(unit.weapons)))
            # print([i for i in (list(unit.weapons))])

    print()
    print()
    print('from .unit import Attribute, Weapon, UnitType')
    print('UNITS = dict()')
    print()
    for i, unit in enumerate(units):
        print('UNITS[UnitID.%s] = %s' % (unit.name, UnitType.from_proto(unit).gen_py()))


def main(unused_argv):
    data = get_data()

    generate_py_units(data)


if __name__ == "__main__":
    app.run(main)
