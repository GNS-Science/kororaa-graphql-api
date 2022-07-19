from toshi_hazard_store import query

"""The main API schema."""
import itertools
import graphene
import pandas as pd
from pathlib import Path
from nzshm_common.location import location

CWD = Path(__file__)
DF_JSON = str(Path(CWD.parent, '../resources/FullLT_allIMT_nz34_all_aggregates.json'))


def lookup_site_code(lat, lon, default="???"):
    """Map locations to nzshm_common.location.LOCATIONS."""
    for loc in location.LOCATIONS:
        if round(float(lat),2) == loc['latitude'] and round(float(lon),2) == loc['longitude']:
            return loc['id']
    return default


def df_with_site_codes(df):
    """Add site codes to the datframe"""

    def calc_new_col(row):
        return lookup_site_code(lat=row['lat'], lon=row['lon'])

    df["loc"] = df.apply(calc_new_col, axis=1)
    return df


SLT_TAG_FINAL_DF = df_with_site_codes(pd.read_json(DF_JSON, dtype={'lat':str,'lon':str}))


class ToshiHazardCurve(graphene.ObjectType):
    """Represents one set of level and values for a hazard curve."""
    levels = graphene.List(graphene.Float, description="IMT levels.")
    values = graphene.List(graphene.Float, description="Hazard values.")


class ToshiHazardResult(graphene.ObjectType):
    """All the info about a given curve."""
    hazard_model = graphene.String()
    loc = graphene.String()
    imt = graphene.String()
    agg = graphene.String()
    vs30 = graphene.Float()
    curve = graphene.Field(ToshiHazardCurve)

class ToshiHazardCurveResult(graphene.ObjectType):
    ok = graphene.Boolean()
    curves = graphene.List(ToshiHazardResult)


# Toshi ID's mapped to VS30
hazard_models = [
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



def hazard_curves_dataframe(kwargs):
    """Run query against the demo dataframe."""
    assert kwargs.get('hazard_model') == 'DEMO_SLT_TAG_FINAL'

    print(SLT_TAG_FINAL_DF)
    imts = kwargs.get('imts')
    aggs = kwargs.get('aggs')
    locs = kwargs.get('locs')

    def filter_df(df, imts, aggs):
        imt_filter = df['imt'].isin(imts)
        #vs30_filter = df[df['vs30'].isin(vs30s)]
        agg_filter = df['agg'].isin(aggs)
        loc_filter = df['loc'].isin(locs)
        return df[imt_filter & agg_filter & loc_filter]

    def build_curve(filtered_df, agg):
        df = filtered_df[filtered_df['agg'] == agg]
        levels, values = df['level'].tolist(), df['hazard'].tolist()
        return ToshiHazardCurve(levels=levels, values=values)

    def build_response_from_query(df, imts, locs, aggs):
        """Todo add vs30s."""

        for(imt, loc, agg) in itertools.product(imts, locs, aggs):
            yield ToshiHazardResult(
                hazard_model=kwargs.get('hazard_model'),
                vs30=400,
                imt=imt,
                loc=loc,
                agg=agg,
                curve=build_curve(df, agg),
                )

    curves = build_response_from_query(filter_df(SLT_TAG_FINAL_DF, imts, aggs), imts, locs, aggs)

    return ToshiHazardCurveResult(ok=True, curves=curves)

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

    def get_hazard_models(hazard_model, vs30s):
        for model in hazard_models:
            if model['hazard_model'] == hazard_model:
                for mapping in model['mappings']:
                    if mapping['vs30'] in vs30s:
                        print(f'mapping {mapping}')
                        yield mapping

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

#     # t0 = dt.utcnow()
#     # search_result = db_root.search_manager.search(kwargs.get('search_term'))
#     # db_metrics.put_duration(__name__, 'resolve_search' , dt.utcnow()-t0)
#     # return Search(ok=True, search_result=search_result)




