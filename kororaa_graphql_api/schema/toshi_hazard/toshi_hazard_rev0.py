"""Build Hazard curves from the old dynamoDB models."""

import logging
from typing import Any, Dict, Iterable, Iterator

from nzshm_common.location import location
from toshi_hazard_store import query

from .hazard_schema import ToshiHazardCurve, ToshiHazardCurveResult, ToshiHazardResult

log = logging.getLogger(__name__)


def lookup_site_code(lat, lon, default="???"):
    """Map locations to nzshm_common.location.LOCATIONS."""
    for loc in location.LOCATIONS:
        if round(float(lat), 2) == loc['latitude'] and round(float(lon), 2) == loc['longitude']:
            return loc['id']
    return default


# Toshi ID's mapped to VS30
hazard_models: Iterable[Dict] = [
    {
        "hazard_model": "TEST1",
        "notes": "These are the 15km max_jump from GT R2VuZXJhbFRhc2s6MTAyOTM0 .",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDA5"},
            {"vs30": 300, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDEy"},
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDE1"},
            {"vs30": 400, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDE4"},
            {"vs30": 450, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDIx"},
            {"vs30": 750, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDI0"},
        ],
    },
    {
        "hazard_model": "TEST2",
        "notes": "",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTcz"},
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTk3"},
        ],
    },
    {
        "hazard_model": "TEST3",
        "notes": "",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDA5"},
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDE1"},
        ],
    },
]


def get_hazard_models(hazard_model: str, vs30s: Iterable[float]) -> Iterator[Dict[str, Any]]:
    for model in hazard_models:
        if model['hazard_model'] == hazard_model:
            for mapping in model['mappings']:
                if mapping['vs30'] in vs30s:
                    # rint(f'mapping {mapping}')
                    yield mapping


def hazard_curves_dynamodb(kwargs):
    """Run query against dynamoDB."""

    def get_curve(obj):
        # print(f"get_curve values from {obj}")
        levels, values = [], []
        for lv in obj.values:
            levels.append(float(lv.lvl))
            values.append(float(lv.val))
        return ToshiHazardCurve(levels=levels, values=values)

    def build_response_from_query(hazard_model, result_tuples):
        # print("build_response_from_query", query_response)
        # print()
        for mapping, query_response in result_tuples:
            for obj in query_response:
                yield ToshiHazardResult(
                    hazard_model=hazard_model,
                    vs30=mapping['vs30'],
                    imt=obj.imt,
                    loc=obj.loc,
                    agg=obj.agg,
                    curve=get_curve(obj),
                )

    result_tuples = []
    for mapping in get_hazard_models(hazard_model=kwargs.get('hazard_model'), vs30s=kwargs.get('vs30s')):
        result_tuples.append(
            (
                mapping,
                list(
                    query.get_hazard_stats_curves(
                        mapping["toshi_id"], kwargs.get('imts'), kwargs.get('locs'), kwargs.get('aggs')
                    )
                ),
            )
        )

    return ToshiHazardCurveResult(ok=True, curves=build_response_from_query(kwargs.get('hazard_model'), result_tuples))
