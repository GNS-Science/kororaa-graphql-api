"""Build Hazard curves from the old dynamoDB models."""

import logging
from typing import Any, Dict, Iterable, Iterator

from nzshm_common.location import location
from toshi_hazard_store import query_v3

from .hazard_schema import ToshiHazardCurve, ToshiHazardCurveResult, ToshiHazardResult

log = logging.getLogger(__name__)


def lookup_site_code(lat, lon, default="???"):
    """Map locations to nzshm_common.location.LOCATIONS."""
    for loc in location.LOCATIONS:
        if round(float(lat), 2) == loc['latitude'] and round(float(lon), 2) == loc['longitude']:
            return loc['id']
    return default


def hazard_curves(kwargs):
    """Run query against dynamoDB usign v3 query."""

    def get_curve(obj):
        # print(f"get_curve values from {obj}")
        levels, values = [], []
        for lv in obj.values:
            levels.append(float(lv.lvl))
            values.append(float(lv.val))
        return ToshiHazardCurve(levels=levels, values=values)

    def build_response_from_query(result):
        # THS_HazardAggregation-LOCAL<-36.9~174.8, -36.870~174.770:250:PGA:mean:GRIDDED_THE_THIRD>
        for obj in result:
            yield ToshiHazardResult(
                hazard_model=obj.hazard_model_id,
                vs30=obj.vs30,
                imt=obj.imt,
                loc=obj.nloc_001,
                agg=obj.agg,
                curve=get_curve(obj),
            )

    res = query_v3.get_hazard_curves(kwargs['locs'], kwargs['vs30s'],
        [kwargs['hazard_model']], kwargs['imts'], aggs=kwargs['aggs'])
    return ToshiHazardCurveResult(ok=True, curves=build_response_from_query(res))
