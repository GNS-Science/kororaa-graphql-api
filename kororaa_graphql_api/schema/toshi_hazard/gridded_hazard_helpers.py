from datetime import datetime as dt
from pathlib import Path
from typing import Iterable, List, Optional

from nzshm_grid_loc.io import load_polygon_file
from shapely.geometry import Polygon


class CustomPolygon:
    def __init__(self, polygon: Polygon, value: float = None):
        self._polygon = polygon
        self._value = value

    def value(self) -> Optional[float]:
        return self._value

    def polygon(self) -> Polygon:
        return self._polygon

    def __hash__(self):
        return hash((self._polygon.wkt, self._value))

    def __eq__(self, other):
        return self._polygon == other._polygon and self._value == other._value


def inner_tiles(clipping_parts: List[Polygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    """Filter tiles, yielding only those that are completely covered by a clipping part.

    This can yield a tile more than once if the clipping_parts overlap can to cover that tile.
    """
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.covers(tile.polygon()):
                yield tile


def edge_tiles(clipping_parts: List[Polygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    """Filter tiles, yielding only those that intersect a clipping_part and clipping them to that intersection."""
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.intersects(tile.polygon()):
                try:
                    yield CustomPolygon(nz_part.intersection(tile.polygon()), tile.value())
                except (Exception) as err:
                    print(err)


def nz_simplified_polgons() -> Iterable[Polygon]:
    small_nz = Path(__file__).parent.parent.parent / 'resources' / 'small-nz.wkt.csv.zip'
    nzdf = load_polygon_file(str(small_nz))

    # build the clipped
    nz_parts = nzdf['geometry'].tolist()

    # try to remove holes
    nz_parts_whole = []
    for part in nz_parts:
        nz_parts_whole.append(Polygon(part.exterior.coords))
    return nz_parts_whole


def clip_tiles(clipping_parts: List[Polygon], tiles: List[Polygon]):
    t0 = dt.utcnow()
    covered_tiles: List[CustomPolygon] = list(inner_tiles(clipping_parts, tiles))
    print('filtered %s wlg tiles to %s in %s' % (len(tiles), len(covered_tiles), dt.utcnow() - t0))

    outer_tiles: List[CustomPolygon] = list(set(tiles).difference(set(covered_tiles)))

    t0 = dt.utcnow()
    clipped_tiles: List[CustomPolygon] = list(edge_tiles(clipping_parts, outer_tiles))
    print('clipped %s edge tiles to %s in %s' % (len(outer_tiles), len(clipped_tiles), dt.utcnow() - t0))

    new_geometry = covered_tiles + clipped_tiles
    return new_geometry
