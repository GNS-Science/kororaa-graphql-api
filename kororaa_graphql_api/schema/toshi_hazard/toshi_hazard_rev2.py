"""Build Hazard curves from the old dynamoDB models."""

import logging
from typing import Iterable, Iterator
from nzshm_common.location import CodedLocation, location
from toshi_hazard_store import query_v3

from .hazard_schema import GriddedLocation, ToshiHazardCurve, ToshiHazardCurveResult, ToshiHazardResult

log = logging.getLogger(__name__)



def match_named_location_coord_code(location_code: str) -> CodedLocation:
    """Attempt to match a Named Location ."""
    tloc = CodedLocation(*[float(x) for x in location_code.split('~')], 0.01).resample(0.001)
    for loc in location.LOCATIONS_BY_ID:
        site = location.LOCATIONS_BY_ID[loc]
        named_location = CodedLocation(site['latitude'], site['longitude'], 0.01).resample(0.001)
        print('test', tloc, 'named', named_location, loc)
        if tloc == named_location:
            return GriddedLocation(lat=tloc.lat, lon=tloc.lon, code=tloc.code, resolution=tloc.resolution, name=site.get('name'), key=site.get('id'))


def normalise_locations(locations: Iterable[str]) -> Iterator[CodedLocation]:
    for loc in locations:
        # Check if this is a location ID eg "WLG" and if so, convert to the legit code
        if loc in location.LOCATIONS_BY_ID:
            site = location.LOCATIONS_BY_ID[loc]
            cloc = CodedLocation(site['latitude'], site['longitude'], 0.01).resample(0.001) # NamedLocation have 0.01 resolution
            yield GriddedLocation(lat=cloc.lat, lon=cloc.lon, code=cloc.code, resolution=cloc.resolution, name=site.get('name'), key=site.get('id'))
            continue

        # do these coordinates match a named location, if so convert to the legit code.
        matched = match_named_location_coord_code(loc)
        if matched:
            yield matched
            continue

        cloc = CodedLocation(*[float(x) for x in loc.split('~')], 0.1).resample(0.001)
        yield GriddedLocation(lat=cloc.lat, lon=cloc.lon, code=cloc.code, resolution=cloc.resolution)

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

    gridded_locations = list(normalise_locations(kwargs['locs']))

    # gridded_locations = [
    #     GriddedLocation(lat=loc.lat, lon=loc.lon, code=loc.code, resolution=loc.resolution) for loc in locations
    # ]

    coded_locations = [loc.code for loc in gridded_locations]
    res = query_v3.get_hazard_curves(
        coded_locations, kwargs['vs30s'], [kwargs['hazard_model']], kwargs['imts'], aggs=kwargs['aggs']
    )
    return ToshiHazardCurveResult(ok=True, locations=gridded_locations, curves=build_response_from_query(res))
