"""Schema objects for hazard."""
import graphene


class GriddedLocation(graphene.ObjectType):
    lat = graphene.Float()
    lon = graphene.Float()
    resolution = graphene.Float()
    code = graphene.String()


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
    locations = graphene.List(GriddedLocation, required=False)
    curves = graphene.List(ToshiHazardResult)


class GriddedLocationResult(graphene.ObjectType):
    location = graphene.Field(GriddedLocation)
    ok = graphene.Boolean()



