"""The main API schema."""

import graphene
from graphene import relay


class QueryRoot(graphene.ObjectType):
    """This is the entry point for all graphql query operations"""

    node = relay.Node.Field()

    about = graphene.String(description='About this API ')

    def resolve_about(root, info, **args):
        return "Hello World, I am kororaa_graphql_api!"


schema_root = graphene.Schema(query=QueryRoot, mutation=None, auto_camelcase=False)
