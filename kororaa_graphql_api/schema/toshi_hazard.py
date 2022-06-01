import graphene
from graphene import relay


# Toshi ID's mapped to VS30
hazard_models = [
    { "hazard_model": "TEST1",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTM3" },
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTYx" }]
    },
    {"hazard_model": "TEST2",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTcz" },
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTk3" }]
    },
    {"hazard_model": "TEST3",
        "mappings": [
            {"vs30": 250, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDA5" },
            {"vs30": 350, "toshi_id": "T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzMDE1" }]
    }
]


# class ToshiHazardCurveQuery(graphene.ObjectType):
#     """query hazard curves."""

#     args = graphene.Field(
#         ToshiHazardCurveResult,
#         toshi_hazard_id=graphene.Argument(graphene.ID),
#         imts=graphene.Argument(graphene.List(graphene.String)),
#         locs=graphene.Argument(graphene.List(graphene.String)),
#         aggs=graphene.Argument(graphene.List(graphene.String)),
#     )

#     qry = graphene.Field(ToshiHazardCurveResult)

#     def resolve_query(root, info, **kwargs):
#         print(f"resolve_hazard_curves(root, info, **kwargs) {kwargs}")
#         print("#res = list(query.get_hazard_stats_curves(TOSHI_ID, ['PGA'], ['WLG', 'QZN'], ['mean']))")
#         res = list(
#             query.get_hazard_stats_curves(
#                 kwargs.get('toshi_hazard_id'), kwargs.get('imts'), kwargs.get('locs'), kwargs.get('aggs')
#             )
#         )

#         def get_curve(obj):
#             # print(f"get_curve values from {obj}")
#             levels, values = [], []
#             for lv in obj.values:
#                 levels.append(float(lv.lvl))
#                 values.append(float(lv.val))
#             return ToshiHazardCurve(levels=levels, values=values)

#         def build_response_from_query(query_response):
#             # print("build_response_from_query", query_response)
#             # print()
#             for obj in query_response:
#                 yield ToshiHazardResult(
#                     toshi_hazard_id=obj.haz_sol_id, imt=obj.imt, loc=obj.loc, agg=obj.agg, curve=get_curve(obj)
#                 )

#         return ToshiHazardCurveResult(ok=True, curves=build_response_from_query(res))

#     #     # t0 = dt.utcnow()
#     #     # search_result = db_root.search_manager.search(kwargs.get('search_term'))
#     #     # db_metrics.put_duration(__name__, 'resolve_search' , dt.utcnow()-t0)
#     #     # return Search(ok=True, search_result=search_result)
