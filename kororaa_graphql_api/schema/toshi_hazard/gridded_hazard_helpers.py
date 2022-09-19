import logging
from datetime import datetime as dt
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Tuple

from nzshm_grid_loc.io import load_polygon_file
from shapely.geometry import Polygon

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter

log = logging.getLogger(__name__)
db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")


class CustomPolygon:
    def __init__(self, polygon: Polygon, location: Tuple[float, float]):
        self._polygon = polygon
        self._location = location

    def polygon(self) -> Polygon:
        return self._polygon

    def location(self) -> Tuple[float, float]:
        return self._location

    def __hash__(self):
        return hash((self._polygon.wkt, self._location))

    def __eq__(self, other):
        return self._polygon == other._polygon and self._location == other._location


def inner_tiles(clipping_parts: List[CustomPolygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    """Filter tiles, yielding only those that are completely covered by a clipping part.

    This can yield a tile more than once if the clipping_parts overlap can to cover that tile.
    """
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.polygon().covers(tile.polygon()):
                yield tile


def edge_tiles(clipping_parts: List[CustomPolygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    """Filter tiles, yielding only those that intersect a clipping_part and clipping them to that intersection."""
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.polygon().intersects(tile.polygon()):
                try:
                    clipped = CustomPolygon(nz_part.polygon().intersection(tile.polygon()), tile.location())
                    if not clipped.polygon().geom_type == 'Point':
                        yield clipped
                    else:
                        raise RuntimeError("Clipped tile %s is not a Polygon" % (repr(clipped.polygon())))
                except (Exception) as err:
                    log.warning("edge_tiles raised error: %s" % err)


@lru_cache
def nz_simplified_polgons() -> Iterable[Polygon]:
    small_nz = Path(__file__).parent.parent.parent / 'resources' / 'small-nz.wkt.csv.zip'
    nzdf = load_polygon_file(str(small_nz))
    nz_parts = nzdf['geometry'].tolist()
    # try to remove holes
    nz_parts_whole = []
    for part in nz_parts:
        nz_parts_whole.append(CustomPolygon(Polygon(part.exterior.coords),tuple([part.centroid.x, part.centroid.y])))
    return tuple(nz_parts_whole)


@lru_cache
def clip_tiles(clipping_parts: Tuple[CustomPolygon], tiles: Tuple[CustomPolygon]):
    t0 = dt.utcnow()
    covered_tiles: List[CustomPolygon] = list(inner_tiles(clipping_parts, tiles))
    db_metrics.put_duration(__name__, 'filter_inner_tiles', dt.utcnow() - t0)

    outer_tiles: List[CustomPolygon] = list(set(tiles).difference(set(covered_tiles)))

    t0 = dt.utcnow()
    clipped_tiles: List[CustomPolygon] = list(edge_tiles(clipping_parts, outer_tiles))
    db_metrics.put_duration(__name__, 'clip_outer_tiles', dt.utcnow() - t0)

    log.info('filtered %s tiles to %s inner in %s' % (len(tiles), len(covered_tiles), dt.utcnow() - t0))
    log.info('clipped %s edge tiles to %s in %s' % (len(outer_tiles), len(clipped_tiles), dt.utcnow() - t0))

    new_geometry = covered_tiles + clipped_tiles
    return tuple(new_geometry)
