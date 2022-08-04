"""The main API schema."""

import graphene
from graphene import relay
from nzshm_common.location import CodedLocation

from .toshi_hazard import ToshiHazardCurveResult, hazard_curves, hazard_curves_dataframe, hazard_curves_dynamodb
from .toshi_hazard.toshi_hazard_rev0 import get_hazard_models  # TODO deprecate this


class GriddedLocation(graphene.ObjectType):
    lat = graphene.Float()
    lon = graphene.Float()
    code = graphene.String()


class GriddedLocationResult(graphene.ObjectType):
    location = graphene.Field(GriddedLocation)
    ok = graphene.Boolean()


class QueryRoot(graphene.ObjectType):
    """This is the entry point for all graphql query operations"""

    node = relay.Node.Field()

    about = graphene.String(description='About this API ')

    gridded_location = graphene.Field(
        GriddedLocationResult,
        lat=graphene.Argument(graphene.Float),
        lon=graphene.Argument(graphene.Float),
        resolution=graphene.Argument(graphene.Float),
    )

    hazard_curves = graphene.Field(
        ToshiHazardCurveResult,
        hazard_model=graphene.Argument(graphene.String),
        imts=graphene.Argument(graphene.List(graphene.String)),
        locs=graphene.Argument(graphene.List(graphene.String)),
        aggs=graphene.Argument(graphene.List(graphene.String)),
        vs30s=graphene.Argument(graphene.List(graphene.Float)),
    )

    def resolve_gridded_location(root, info, **kwargs):
        grid_loc = CodedLocation(kwargs['lat'], kwargs['lon'], kwargs['resolution'])
        return GriddedLocationResult(
            location=GriddedLocation(lat=grid_loc.lat, lon=grid_loc.lon, code=grid_loc.code), ok=True
        )

    def resolve_hazard_curves(root, info, **kwargs):
        print(f"resolve_hazard_curves(root, info, **kwargs) {kwargs}")
        print("#res = list(query.get_hazard_stats_curves(TOSHI_ID, ['PGA'], ['WLG', 'QZN'], ['mean']))")
        hazard_model = kwargs.get('hazard_model')

        # TODO: remove old revs
        # THE V2 DEMO from Dataframe
        if hazard_model == 'DEMO_SLT_TAG_FINAL':
            return hazard_curves_dataframe(kwargs)

        # THE V0 OLD TEST data from dynamoDB
        if list(get_hazard_models(hazard_model=kwargs.get('hazard_model'), vs30s=kwargs.get('vs30s'))):
            return hazard_curves_dynamodb(kwargs)

        return hazard_curves(kwargs)

    def resolve_about(root, info, **args):
        return "Hello World, I am kororaa_graphql_api!"


schema_root = graphene.Schema(query=QueryRoot, mutation=None, auto_camelcase=False)
