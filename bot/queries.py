from pysc2.env.sc2_env import SC2Env

from s2clientprotocol import (
    common_pb2 as common_pb,
    query_pb2 as query_pb,
)


def query_path(sc2_env, point1, point2):
    return sc2_env.request_query([
        query_pb.RequestQuery(
            pathing=[query_pb.RequestQueryPathing(
                start_pos=common_pb.Point2D(x=point1.x, y=point1.y),
                end_pos=common_pb.Point2D(x=point2.x, y=point2.y)
            )]
        )
    ])
