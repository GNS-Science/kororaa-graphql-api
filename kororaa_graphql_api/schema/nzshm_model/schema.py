"""The nzshm_model API schema."""

import ast
import graphene
import json
import dataclasses
import nzshm_model
import logging
from typing import Iterable
from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter

log = logging.getLogger(__name__)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")

class BranchAttributeValue(graphene.ObjectType):
    name = graphene.String()
    long_name = graphene.String()
    value_options = graphene.JSONString()

class FaultSystemLogicTreeSpec(graphene.ObjectType):
    short_name = graphene.String()
    long_name = graphene.String()
    branches = graphene.List(BranchAttributeValue)

class SourceLogicTreeSpec(graphene.ObjectType):
    fault_system_branches = graphene.List(FaultSystemLogicTreeSpec)

class NzshmModel(graphene.ObjectType):
    version = graphene.String()
    title = graphene.String()
    source_logic_tree = graphene.JSONString()
    source_logic_tree_spec = graphene.Field(SourceLogicTreeSpec)

    def resolve_source_logic_tree(root, info, **kwargs):
        log.info("resolve_source_logic_tree kwargs %s" % kwargs)
        model = nzshm_model.get_model_version(root.version)

        res = dataclasses.asdict(model.source_logic_tree())
        return res

    def resolve_source_logic_tree_spec(root, info, **kwargs):
        log.info("resolve_source_logic_tree_spec kwargs %s" % kwargs)
        model = nzshm_model.get_model_version(root.version)
        log.debug(model)
        # log.debug(model.source_logic_tree())

        slt = model.source_logic_tree()
        spec = slt.derive_spec()
        # print(spec)

        def build_branch_attribute_values(fslt_branches) -> Iterable:
            for fslt in fslt_branches:
                yield BranchAttributeValue(name = fslt.name, long_name = fslt.long_name, # value_options = get_values(fslt), value_type = get_value_type(fslt),
                    value_options = fslt.value_options)

        def build_fault_system_branches(spec) -> Iterable:
            for fslt in spec.fault_system_branches:
                yield FaultSystemLogicTreeSpec(short_name=fslt.short_name, long_name=fslt.long_name, branches = build_branch_attribute_values(fslt.branches) )

        return SourceLogicTreeSpec(fault_system_branches=build_fault_system_branches(spec))


class NzshmModelResult(graphene.ObjectType):
    ok = graphene.Boolean()
    models = graphene.List(NzshmModel)

