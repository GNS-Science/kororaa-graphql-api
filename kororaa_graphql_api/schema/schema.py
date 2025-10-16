"""The main API schema."""

import logging

import graphene
from graphene import relay

import kororaa_graphql_api

from .publications import ScienceReportResult, get_science_reports
from .textual_content import TextualContentResult, get_textual_content
from .toshi_hazard import DisaggregationReportResult, disaggregation_reports

log = logging.getLogger(__name__)


class QueryRoot(graphene.ObjectType):
    """This is the entry point for all graphql query operations"""

    node = relay.Node.Field()

    about = graphene.String(description='About this API ')

    version = graphene.String(description='API version')

    disaggregation_reports = graphene.Field(
        DisaggregationReportResult,
    )

    science_reports = graphene.Field(
        ScienceReportResult,
    )

    textual_content = graphene.Field(
        TextualContentResult,
        index=graphene.Argument(graphene.String, required=False),
        tags=graphene.Argument(graphene.List(graphene.String), required=False),
    )

    def resolve_disaggregation_reports(root, info, **kwargs):
        log.info("resolve_disaggregation_reports kwargs %s" % kwargs)
        return disaggregation_reports(kwargs)

    def resolve_science_reports(root, info, **kwargs):
        log.info("resolve_science_reports kwargs %s" % kwargs)
        return get_science_reports(kwargs)

    def resolve_textual_content(root, info, **kwargs):
        log.info("resolve_textual_content kwargs %s" % kwargs)
        return get_textual_content(kwargs)

    def resolve_about(root, info, **args):
        return f"Hello World, I am kororaa_graphql_api version: {kororaa_graphql_api.__version__}"

    def resolve_version(root, info, **args):
        return kororaa_graphql_api.__version__


schema_root = graphene.Schema(query=QueryRoot, mutation=None, auto_camelcase=False)
