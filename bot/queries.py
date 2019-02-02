from s2clientprotocol import (
    common_pb2 as common_pb,
    query_pb2 as query_pb,
)


def query_path(sc2_env, point1, point2):
    return sc2_env.request_query([
        query_pb.RequestQuery(
            pathing=[query_pb.RequestQueryPathing(
                start_pos=common_pb.Point2D(x=point1.x/100, y=point1.y/100),
                end_pos=common_pb.Point2D(x=point2.x/100, y=point2.y/100)
            )]
        )
    ])


def query_building_placement(sc2_env, ability_id, target_pos):
    return sc2_env.request_query([
        query_pb.RequestQuery(
            placements=[query_pb.RequestQueryBuildingPlacement(
                ability_id=ability_id,
                target_pos=common_pb.Point2D(x=target_pos.x/100, y=target_pos.y/100)
            )]
        )
    ])[0].placements[0].result


def query_available_abilities(sc2_env, unit_tag):
    return [a.ability_id for a in sc2_env.request_query([
        query_pb.RequestQuery(
            abilities=[query_pb.RequestQueryAvailableAbilities(
                unit_tag=unit_tag,
            )]
        )
    ])[0].abilities[0].abilities]
