import pytest
from ..main import app
from geo import (
    add_point_to_node,
    add_polygon_to_way,
    filter_nodes,
    validate_coordinates,
    is_within_ways
)
from shapely.geometry import Point, Polygon

def test_valdiate_coordinates_true():
    assert validate_coordinates(90, 180) == False


def test_valdiate_coordinates_false():
    assert validate_coordinates(32, 34) == True


def test_add_point_to_node():
    node = add_point_to_node({'id': 123456789, 'lat': 32, 'lon': 34})
    p = node.get("point")

    assert p.x == 32, p.y == 34 


def test_add_polygon_to_way():
    node_map = {
        "1": {"point": Point(0, 0)},
        "2": {"point": Point(0, 1)},
        "3": {"point": Point(1, 0)},
        "4": {"point": Point(1, 1)},
    }
    way = {"nd": [{"ref": 1}, {"ref": 2}, {"ref": 3}, {"ref": 4}]}
    way = add_polygon_to_way(way, node_map)
    
    assert way.get("polygon") == Polygon([(0, 0), (0, 1), (1, 0), (1, 1)])


def test_is_within_ways_true():
    node = {"id": "1", "point": Point(0.5, 0.5)}
    ways = [{"id": "2", "polygon": Polygon([(0, 0), (0, 1), (1, 0), (1, 1)])}]

    assert is_within_ways(node, ways) == True


def test_is_within_ways_false():
    node = {"point": Point(2, 1)}
    ways = [{"polygon": Polygon([(0, 0), (0, 1), (1, 0), (1, 1)])}]

    assert is_within_ways(node, ways) == False
