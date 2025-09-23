"""Schema objects for hazard."""
import graphene


class HazardCodedLocation(graphene.ObjectType):
    lat = graphene.Float()
    lon = graphene.Float()
    code = graphene.String()
    name = graphene.String(required=False)
    key = graphene.String(required=False)


class DisaggregationReport(graphene.ObjectType):
    """All the info about a given disagg report."""

    hazard_model = graphene.String()
    location = graphene.Field(HazardCodedLocation)
    imt = graphene.String()
    poe = graphene.Float()
    vs30 = graphene.Int()
    inv_time = graphene.Int()
    report_url = graphene.String()


class DisaggregationReportResult(graphene.ObjectType):
    ok = graphene.Boolean()
    reports = graphene.List(DisaggregationReport, required=False)
