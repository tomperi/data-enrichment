import logging
from shapely.geometry import Point, Polygon
from typing import Dict, List


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def add_point_to_node(node: Dict) -> Dict:
    """
    Add a Point object to a node dictionary, based on it's coordinates
    """
    return dict(node, **{"point": Point(node.get("lat"), node.get("lon"))})


def add_polygon_to_way(way: Dict, node_map: Dict) -> Dict:
    """
    Add a Polygon object to a way, based on a list of relevant nodes
    """
    polygon = Polygon(
                [
                    (p.x, p.y)
                    for x in way.get("nd")
                    if (p := node_map.get(str(x.get("ref", "")), {}).get("point"))
                ]
            )
    if str(polygon) != "GEOMETRYCOLLECTION EMPTY":
        way["polygon"] = polygon
    
    return way


def is_within_ways(node: Dict, ways: List) -> bool:
    """
    Predicate for checking if a given node overlaps a list of ways 
    """
    point = node.get("point")
    for way in ways:
        polygon = way.get("polygon")
        if polygon and (
            point.within(polygon) or polygon.exterior.distance(point) == 0.0
        ):
            logging.warning(f"found point {node.get('id')} within way {way.get('id')}")
            return True

    logging.info("")

    return False


def filter_nodes(node_list: List, ways: List) -> List:
    """
    Filter all nodes that overlap any way of a given list
    """
    return list(filter(lambda x: not is_within_ways(x, ways), node_list))


def validate_coordinates(lat, long) -> bool:
    try:
        lat, long = float(lat), float(long)
        if (-90 < lat < 90) and (-180 < long < 180):
            return True
    except ValueError:
        return False

    return False
