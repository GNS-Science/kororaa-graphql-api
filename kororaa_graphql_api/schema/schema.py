"""The main API schema."""

import graphene
from graphene import relay
from toshi_hazard_store import query

from .toshi_hazard import hazard_models


class ToshiHazardCurve(graphene.ObjectType):
    """Represents one set of level and values for a hazard curve."""

    levels = graphene.List(graphene.Float, description="IMT levels.")
    values = graphene.List(graphene.Float, description="Hazard values.")


class ToshiHazardResult(graphene.ObjectType):
    """All the info about a given curve
    loc
    imt
    agg
    rlz
    vs30
    """

    hazard_model = graphene.ID()
    loc = graphene.String()
    imt = graphene.String()
    agg = graphene.String()
    vs30 = graphene.Float()
    curve = graphene.Field(ToshiHazardCurve)


# class ToshiHazardCurveConnection(relay.Connection):
#     """Relay Connection class."""

#     class Meta:
#         node = ToshiHazardResult


class ToshiHazardCurveResult(graphene.ObjectType):
    ok = graphene.Boolean()
    # curves_relay = relay.ConnectionField(ToshiHazardCurveConnection)
    curves = graphene.List(ToshiHazardResult)


class QueryRoot(graphene.ObjectType):
    """This is the entry point for all graphql query operations"""

    node = relay.Node.Field()

    about = graphene.String(description='About this API ')

    # hazard_curves = graphene.Field(ToshiHazardCurveQuery)

    hazard_curves = graphene.Field(
        ToshiHazardCurveResult,
        hazard_model=graphene.Argument(graphene.String),
        imts=graphene.Argument(graphene.List(graphene.String)),
        locs=graphene.Argument(graphene.List(graphene.String)),
        aggs=graphene.Argument(graphene.List(graphene.String)),
        vs30s=graphene.Argument(graphene.List(graphene.Float)),
    )

    def resolve_hazard_curves(root, info, **kwargs):
        print(f"resolve_hazard_curves(root, info, **kwargs) {kwargs}")
        print("#res = list(query.get_hazard_stats_curves(TOSHI_ID, ['PGA'], ['WLG', 'QZN'], ['mean']))")

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

        def build_response_from_query(result_tuples):
            # print("build_response_from_query", query_response)
            # print()
            for mapping, query_response in result_tuples:
                for obj in query_response:
                    yield ToshiHazardResult(
                        hazard_model=kwargs.get('hazard_model'),
                        vs30=mapping['vs30'],
                        imt=obj.imt,
                        loc=obj.loc,
                        agg=obj.agg,
                        curve=get_curve(obj),
                    )

        def get_curve(obj):
            # print(f"get_curve values from {obj}")
            levels, values = [], []
            for lv in obj.values:
                levels.append(float(lv.lvl))
                values.append(float(lv.val))
            return ToshiHazardCurve(levels=levels, values=values)

        return ToshiHazardCurveResult(ok=True, curves=build_response_from_query(result_tuples))

    #     # t0 = dt.utcnow()
    #     # search_result = db_root.search_manager.search(kwargs.get('search_term'))
    #     # db_metrics.put_duration(__name__, 'resolve_search' , dt.utcnow()-t0)
    #     # return Search(ok=True, search_result=search_result)

    def resolve_about(root, info, **args):
        return "Hello World, I am kororaa_graphql_api!"


schema_root = graphene.Schema(query=QueryRoot, mutation=None, auto_camelcase=False)
