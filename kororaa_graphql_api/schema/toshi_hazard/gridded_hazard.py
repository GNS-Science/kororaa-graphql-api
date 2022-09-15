"""Build Gridded Hazard."""
import json
import logging
import math
import os
from datetime import datetime as dt
from functools import lru_cache
import geopandas as gpd
import graphene
import matplotlib as mpl
from nzshm_common.geometry.geometry import create_square_tile
from nzshm_common.grids import RegionGrid
from toshi_hazard_store import query

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter
from .hazard_schema import GriddedLocation
from .gridded_hazard_helpers import (
    CustomPolygon,
    clip_tiles,
    nz_simplified_polgons,
)

log = logging.getLogger(__name__)

RegionGridEnum = graphene.Enum.from_enum(RegionGrid)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")


class ColourScaleNormalise(graphene.Enum):
    LOG = "log"
    LIN = "lin"


COLOR_SCALE_NORMALISE_LOG = (
    ColourScaleNormalise.LOG
    if os.getenv('COLOR_SCALE_NORMALISATION', '').upper() == 'LOG'
    else ColourScaleNormalise.LIN
)


class HexRgbValueMapping(graphene.ObjectType):
    levels = graphene.List(graphene.Float)
    hexrgbs = graphene.List(graphene.String)


def get_colour_scale(cmap: mpl.cm, norm: mpl.colors.Normalize, vmax: float) -> HexRgbValueMapping:
    # build the colour_scale
    assert vmax * 2 == int(vmax * 2)  # make sure we have a value on a 0.5 interval
    levels, hexrgbs = [], []
    for level in range(0, int(vmax * 10) + 1):
        levels.append(level / 10)
        hexrgbs.append(mpl.colors.to_hex(cmap(norm(level / 10))))
    hexrgb = HexRgbValueMapping(levels=levels, hexrgbs=hexrgbs)
    return hexrgb


class GeoJsonHazardMap(graphene.ObjectType):
    geojson = graphene.JSONString()
    colour_scale = graphene.Field(HexRgbValueMapping)


class GriddedHazard(graphene.ObjectType):
    grid_id = graphene.Field(RegionGridEnum)
    hazard_model = graphene.String()
    imt = graphene.String()
    agg = graphene.String()
    vs30 = graphene.Float()
    poe = graphene.Float()
    values = graphene.List(graphene.Float, description="Acceleration values.")

    hazard_map = graphene.Field(
        GeoJsonHazardMap,
        # Extra args
        color_scale=graphene.String(default_value='jet', required=False),
        color_scale_vmax=graphene.Float(required=False),
        color_scale_vmin=graphene.Float(default_value=0.0, required=False),
        color_scale_normalise=graphene.Argument(ColourScaleNormalise, required=False),
        stroke_width=graphene.Float(default_value='0.1', required=False),
        stroke_opacity=graphene.Float(default_value='1.0', required=False),
        fill_opacity=graphene.Float(default_value='1.0', required=False),
    )

    grid_locations = graphene.List(GriddedLocation)

    @lru_cache
    def resolve_hazard_map(root, info, **args):
        """Resolver gridded hazard to geojosn with formatting options."""
        t0 = dt.utcnow()
        log.info('resolve_geojson args: %s' % args)

        # get the query arguments
        color_scale_vmax = args.get('color_scale_vmax')
        color_scale_vmin = args.get('color_scale_vmin')
        color_scale_normalise = args.get('color_scale_normalise', COLOR_SCALE_NORMALISE_LOG)
        color_scale = args['color_scale']
        fill_opacity = args['fill_opacity']
        stroke_opacity = args['stroke_opacity']
        stroke_width = args['stroke_width']

        # TODO: is the a simpler way to access the base Enum class method?
        region_grid = RegionGrid[RegionGridEnum.get(root.grid_id).name]
        grid = region_grid.load()
        loc, geometry = [], []
        cmap = mpl.cm.get_cmap(color_scale)

        # >>>>>>>>>>>>>>>>>>>>>
        # build the hazard_map
        # for pt in grid:
        #     loc.append((pt[1], pt[0]))
        #     geometry.append(create_square_tile(region_grid.resolution, pt[1], pt[0]))

        def fix_nan(poes):
            for i in range(len(poes)):
                if poes[i] is None:
                    log.info('Nan at %s' % i)
                    poes[i] = 0.0
            return poes

        poes = fix_nan(root.values)
        nz_parts = nz_simplified_polgons()

        # build the hazard_map
        for idx, pt in enumerate(grid):
            loc.append((pt[1], pt[0]))
            tile = CustomPolygon(
                create_square_tile(region_grid.resolution, pt[1], pt[0]), poes[idx]
            )
            geometry.append(tile)

        print('built %s tiles in %s' % (len(geometry), dt.utcnow() - t0))

        new_geometry = clip_tiles(nz_parts, geometry)
        poes = [g.value() for g in new_geometry]

        # >>>>>>>>>>>>>>>>>>>>>>
        # grid colours
        color_scale_vmax = color_scale_vmax if color_scale_vmax else math.ceil(max(poes) * 2) / 2  # 0 ur None
        log.debug('color_scale_vmax: %s' % color_scale_vmax)

        if color_scale_normalise == ColourScaleNormalise.LOG:
            color_scale_vmin = color_scale_vmin or min(poes)
            log.debug("resolve_hazard_map using LOG normalized colour scale")
            norm = mpl.colors.LogNorm(vmin=color_scale_vmin, vmax=color_scale_vmax)
        else:
            color_scale_vmin = color_scale_vmin or 0
            log.debug("resolve_hazard_map using LIN normalized colour scale")
            norm = mpl.colors.Normalize(vmin=color_scale_vmin, vmax=color_scale_vmax)

        color_values = [mpl.colors.to_hex(cmap(norm(v)), keep_alpha=True) for v in poes]

        gdf = gpd.GeoDataFrame(
            data=dict(
                # loc=loc,
                geometry=[g.polygon() for g in new_geometry],
                value=[g.value() for g in new_geometry],
                fill=color_values,
                fill_opacity=[fill_opacity for n in poes],
                stroke=color_values,
                stroke_width=[stroke_width for n in poes],
                stroke_opacity=[stroke_opacity for n in poes],
            )
        )
        gdf = gdf.rename(
            columns={'fill_opacity': 'fill-opacity', 'stroke_width': 'stroke-width', 'stroke_opacity': 'stroke-opacity'}
        )

        db_metrics.put_duration(__name__, 'resolve_geojson', dt.utcnow() - t0)
        return GeoJsonHazardMap(
            geojson=json.loads(gdf.to_json()), colour_scale=get_colour_scale(cmap, norm, vmax=color_scale_vmax)
        )


class GriddedHazardResult(graphene.ObjectType):
    gridded_hazard = graphene.Field(graphene.List(GriddedHazard))
    ok = graphene.Boolean()


def query_gridded_hazard(kwargs):
    """Run query against dynamoDB."""
    t0 = dt.utcnow()
    log.info('query_gridded_hazard args: %s' % kwargs)

    def build_response_from_query(result):
        log.info("build_response_from_query %s" % result)
        for obj in result:
            yield GriddedHazard(
                grid_id=RegionGridEnum[obj.location_grid_id],
                hazard_model=obj.hazard_model_id,
                vs30=obj.vs30,
                imt=obj.imt,
                agg=obj.agg,
                poe=obj.poe,
                values=obj.grid_poes,
            )

    response = query.get_gridded_hazard(
        hazard_model_ids=kwargs['hazard_model_ids'],
        location_grid_ids=[RegionGridEnum.get(kwargs['grid_id']).name],  # wrapped in list as we receive just a singular
        vs30s=kwargs['vs30s'],
        imts=kwargs['imts'],
        aggs=kwargs['aggs'],
        poes=kwargs['poes'],
    )
    res = GriddedHazardResult(ok=True, gridded_hazard=build_response_from_query(response))
    db_metrics.put_duration(__name__, 'query_gridded_hazard', dt.utcnow() - t0)
    return res
