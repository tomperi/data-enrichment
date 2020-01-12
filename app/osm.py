import requests
import logging
import json
from lxml.etree import fromstring
from xmljson import XMLData
from geo import (
    add_point_to_node,
    add_polygon_to_way,
    filter_nodes,
    validate_coordinates,
)

from typing import Dict, List, Union

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_nodes(bounding_box: List[float], amenities: str = "*") -> Dict:
    url = f"http://www.overpass-api.de/api/xapi?*[amenity=%s][bbox=%s]" % (
        amenities,
        ",".join([str(x) for x in bounding_box]),
    )
    logging.info(url)
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Got status code: {response.status_code} from osm request")
        return []

    bf = XMLData(dict_type=dict)
    return bf.data(fromstring(response.content))


def locations_to_bounding_box(
    latitude: float, longitude: float, padding=0.01
) -> List[float]:
    bounding_box = [None, None, None, None]

    bounding_box[0] = min(bounding_box[0] or longitude, longitude) - padding
    bounding_box[1] = min(bounding_box[1] or latitude, latitude) - padding
    bounding_box[2] = max(bounding_box[2] or longitude, longitude) + padding
    bounding_box[3] = max(bounding_box[3] or latitude, latitude) + padding

    return bounding_box


def is_tagged(node: Dict, key: str, value: str) -> bool:
    """
    Iterates over all nodes tag and check if a given tag/value exists
    """
    if tags := node.get("tag"):
        if isinstance(tags, dict):
            tags = [tags]

        for tag in tags:
            if (tag.get("k"), tag.get("v")) == (key, value):
                return True

    return False


def get_school_amenity(l):
    """
    Filter a list to have only elements tagged as school amenity
    """
    return list(filter(lambda x: is_tagged(x, "amenity", "school"), l))


def count_schools(lat: float, long: float, padding: float = 0.01) -> int:
    """
    Counts the number of schools around a given location
    """
    response = get_nodes(locations_to_bounding_box(lat, long, padding), "school")

    if not response:
        raise ValueError("Error handling coordinates")

    nodes, ways, relations = response_to_objects(response)
    logging.info(
        f"received {len(nodes)} nodes, {len(ways)} ways, {len(relations)} relations"
    )

    nodes = [add_point_to_node(x) for x in nodes]
    nodes_map = {str(x.get("id")): x for x in nodes}

    tagged_nodes = get_school_amenity(nodes)
    tagged_ways = get_school_amenity(ways)

    tagged_ways = (
        [add_polygon_to_way(x, nodes_map) for x in tagged_ways]
        if nodes_map
        else tagged_ways
    )

    filtered_nodes = filter_nodes(tagged_nodes, tagged_ways)

    tagged_relations = get_school_amenity(relations)

    return sum(map(len, [filtered_nodes, tagged_ways, tagged_relations]))


def response_to_objects(response):
    return [
        ensure_list(response.get("osm", {}).get(x, []))
        for x in ["node", "way", "relation"]
    ]


def ensure_list(obj: Union[Dict, List]):
    if isinstance(obj, dict):
        return [obj]

    return obj
