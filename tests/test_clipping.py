"""Tests for toshi_hazard_rev module."""

import unittest
import random
import json
from unittest import mock
from pathlib import Path
from graphene.test import Client
from datetime import datetime as dt

import geopandas as gpd

from nzshm_common.grids import RegionGrid
from nzshm_common.geometry.geometry import create_square_tile
from nzshm_grid_loc import geography as geo
from nzshm_grid_loc.io import load_polygon_file
from shapely.geometry import Polygon
import shapely
import random

from typing import List, Iterable

GRID = 'WLG_0_01_nb_1_1'
#GRID = 'NZ_0_1_NB_1_1'


class CustomPolygon(Polygon):

    def set_value(self, value):
        self.custom_value = value
        return self

    def get_value(self):
        return(self.custom_value)

    def to_tuple(self):
        return((self.wkt, self.custom_value))

    @staticmethod
    def from_tuple(record):
        poly = CustomPolygon(shapely.wkt.loads(record[0]))
        poly.set_value(record[1])
        return poly


class TestCustomPolygon(unittest.TestCase):

    def test_custom_tuple_roundtrip(self):

        polygon = Polygon([(0, 0), (1, 1), (1, 0)])
        custom = CustomPolygon(polygon)
        custom.set_value(42)

        new_custom = CustomPolygon.from_tuple(custom.to_tuple())
        self.assertEqual(custom, new_custom)


    def test_custom_tuple_hashable(self):

        pA = CustomPolygon(Polygon([(0, 0), (1, 1), (1, 0)])).set_value(42)
        pB = CustomPolygon(Polygon([(0, 0), (1, 1), (1, 0)])).set_value(84)

        setA = set([pA.to_tuple()])
        setB = set([pA.to_tuple(), pB.to_tuple()])

        self.assertEqual( setA.intersection(setB), set([pA.to_tuple()]))


def inner_tiles(clipping_parts: List[Polygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.covers(tile):
                yield tile

def edge_tiles(clipping_parts: List[Polygon], tiles: List[CustomPolygon]) -> Iterable[CustomPolygon]:
    for nz_part in clipping_parts:
        for tile in tiles:
            if nz_part.intersects(tile):
                try:
                    yield CustomPolygon(nz_part.intersection(tile)).set_value(tile.get_value())
                except (Exception) as err:
                    print(err)

def nz_simplified_polgons() -> Iterable[Polygon]:
        small_nz = Path(__file__).parent / 'fixtures' / 'small-nz.wkt.csv.zip'
        # nzdf = geo.Regions.NZ_SMALL.load()
        nzdf = load_polygon_file(str(small_nz))

        # build the clipped
        nz_parts = nzdf['geometry'].tolist()

        # try to remove holes
        nz_parts_whole = []
        for part in nz_parts:
            nz_parts_whole.append(Polygon(part.exterior.coords))

        return nz_parts_whole

# def clip_tiles(clipping_parts:List[Polygon], tiles: List[Polygon]):
#     t0 = dt.utcnow()
#     covered_tiles = list(inner_tiles(clipping_parts, tiles))
#     print('filtered %s wlg tiles to %s in %s' % (len(tiles), len(covered_tiles), dt.utcnow() - t0))

#     # must be faster way ?
#     outer_tiles = list(set([g.wkt for g in tiles]).difference(set([g.wkt for g in covered_tiles])))
#     outer_tiles = [shapely.wkt.loads(t) for t in outer_tiles]

#     t0 = dt.utcnow()
#     clipped_tiles = list(edge_tiles(clipping_parts, outer_tiles))
#     print('clipped %s edge tiles to %s in %s' % (len(outer_tiles), len(clipped_tiles), dt.utcnow() - t0))

#     new_geometry = covered_tiles + clipped_tiles
#     return new_geometry

def clip_tiles(clipping_parts:List[Polygon], tiles: List[Polygon]):
    t0 = dt.utcnow()
    covered_tiles: List[CustomPolygon] = list(inner_tiles(clipping_parts, tiles))
    print('filtered %s wlg tiles to %s in %s' % (len(tiles), len(covered_tiles), dt.utcnow() - t0))

    # must be faster way ?
    outer_tiles: List[CustomPolygon] = list(set([g.to_tuple() for g in tiles]).difference(set([g.to_tuple() for g in covered_tiles])))
    outer_tiles = [CustomPolygon.from_tuple(t) for t in outer_tiles]

    t0 = dt.utcnow()
    clipped_tiles: List[CustomPolygon] = list(edge_tiles(clipping_parts, outer_tiles))
    print('clipped %s edge tiles to %s in %s' % (len(outer_tiles), len(clipped_tiles), dt.utcnow() - t0))

    new_geometry = covered_tiles + clipped_tiles
    return new_geometry



class TestGriddedHazard(unittest.TestCase):

    def test_get_clipped_grid(self):

        region_grid = RegionGrid[GRID]
        grid = region_grid.load()
        geometry = []

        t0 = dt.utcnow()

        # build the hazard_map
        for pt in grid:
            tile = CustomPolygon(create_square_tile(region_grid.resolution, pt[1], pt[0]))
            tile.set_value(random.randint(0, 4.7e6) / 1e6 )
            geometry.append(tile)
        print('built %s tiles in %s' % (len(geometry), dt.utcnow() - t0))

        nz_parts = nz_simplified_polgons()

        new_geometry = clip_tiles(nz_parts, geometry)

        gdf = gpd.GeoDataFrame(data=dict(geometry=new_geometry, value=[g.get_value() for g in new_geometry]))

        with open('dump_new_clipped.json', 'w') as f:
            f.write(gdf.to_json())

        # with open('nz_small.json', 'w') as f:
        #     f.write(nzdf.to_json())


        # for pt in grid:
        #     geometry.append(create_square_tile(region_grid.resolution, pt[1], pt[0]))
        # print('built %s wlg tiles in %s' % (len(geometry), dt.utcnow() - t0))
        # print(nzdf)
        assert 0
