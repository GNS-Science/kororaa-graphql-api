"""Build Hazard curves from the old dynamoDB models."""

import logging

from nzshm_common.location import CodedLocation, location
from toshi_hazard_store import query_v3

from .hazard_schema import GriddedLocation, ToshiHazardCurve, ToshiHazardCurveResult, ToshiHazardResult

log = logging.getLogger(__name__)


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
        log.info("build_response_from_query")
        for obj in result:
            yield ToshiHazardResult(
                hazard_model=obj.hazard_model_id,
                vs30=obj.vs30,
                imt=obj.imt,
                loc=obj.nloc_001,
                agg=obj.agg,
                curve=get_curve(obj),
            )

    locations = []
    for loc in kwargs['locs']:
        # Check if this is a location ID eg "WLG" and if so, convert to the legit code
        if loc in location.LOCATIONS_BY_ID:
            site = location.LOCATIONS_BY_ID[loc]
            locations.append(CodedLocation(site['latitude'], site['longitude'], 0.001))
        else:
            locations.append(CodedLocation(*[float(x) for x in loc.split('~')], 0.1).resample(0.001))

    gridded_locations = [
        GriddedLocation(lat=loc.lat, lon=loc.lon, code=loc.code, resolution=loc.resolution) for loc in locations
    ]
    coded_locations = [loc.code for loc in locations]

    res = query_v3.get_hazard_curves(
        coded_locations, kwargs['vs30s'], [kwargs['hazard_model']], kwargs['imts'], aggs=kwargs['aggs']
    )
    return ToshiHazardCurveResult(ok=True, locations=gridded_locations, curves=build_response_from_query(res))
