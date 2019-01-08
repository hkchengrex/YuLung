from dataclasses import dataclass

def player_to_resources(player):
    return Resources(
        player[1],
        player[2],
        player[3],
        player[4],
        player[10],
        player[12]
    )

@dataclass
class Resources:
    mineral: int
    gas: int
    food_cap: int
    food_used: int
    army_count: int
    larva_count: int