from dataclasses import dataclass


def player_to_resources(player):
    return Resources(
        player[1],
        player[2],
        player[4],  # Food cap and food used seems to be inverted
        player[3],
        player[8],
        player[10],
    )

@dataclass
class Resources:
    mineral: int
    vespene: int
    food_cap: int
    food_used: int
    army_count: int
    larva_count: int
