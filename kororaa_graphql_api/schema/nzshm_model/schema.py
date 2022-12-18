"""The nzshm_model API schema."""

import logging
from typing import Iterable

import graphene
import nzshm_model

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter

log = logging.getLogger(__name__)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")


class BranchAttributeValueSpec(graphene.ObjectType):
    name = graphene.String()
    long_name = graphene.String()
    value_options = graphene.JSONString()


class FaultSystemLogicTreeSpec(graphene.ObjectType):
    short_name = graphene.String()
    long_name = graphene.String()
    branches = graphene.List(BranchAttributeValueSpec)


class SourceLogicTreeSpec(graphene.ObjectType):
    fault_system_branches = graphene.List(FaultSystemLogicTreeSpec)


class BranchAttributeValue(graphene.ObjectType):
    name = graphene.String()
    long_name = graphene.String()
    json_value = graphene.JSONString()


class SourceLogicTreeBranch(graphene.ObjectType):
    weight = graphene.Float()
    onfault_nrml_id = graphene.String()
    distributed_nrml_id = graphene.String()
    inversion_solution_id = graphene.String()
    inversion_solution_type = graphene.String()
    values = graphene.List(BranchAttributeValue)


class FaultSystemLogicTree(graphene.ObjectType):
    short_name = graphene.String()
    long_name = graphene.String()
    branches = graphene.List(SourceLogicTreeBranch)


class SourceLogicTree(graphene.ObjectType):
    fault_system_branches = graphene.List(FaultSystemLogicTree)


class NzshmModel(graphene.ObjectType):
    version = graphene.String()
    title = graphene.String()
    source_logic_tree = graphene.Field(SourceLogicTree)
    source_logic_tree_spec = graphene.Field(SourceLogicTreeSpec)

    def resolve_source_logic_tree(root, info, **kwargs):
        log.info("resolve_source_logic_tree kwargs %s" % kwargs)
        model = nzshm_model.get_model_version(root.version)

        slt = model.source_logic_tree()

        def build_branch_attribute_values(source_branch) -> Iterable:
            for value in source_branch.values:
                yield BranchAttributeValue(name=value.name, long_name=value.long_name, json_value=value.value)

        def build_source_branches(fslt) -> Iterable:
            for source_branch in fslt.branches:
                log.debug(source_branch)
                yield SourceLogicTreeBranch(
                    weight=source_branch.weight,
                    onfault_nrml_id=source_branch.onfault_nrml_id,
                    distributed_nrml_id=source_branch.distributed_nrml_id,
                    inversion_solution_id=source_branch.inversion_solution_id,
                    inversion_solution_type=source_branch.inversion_solution_type,
                    values=build_branch_attribute_values(source_branch),
                )

        def build_fault_system_branches(slt) -> Iterable:
            for fslt in slt.fault_system_branches:
                yield FaultSystemLogicTree(
                    short_name=fslt.short_name, long_name=fslt.long_name, branches=build_source_branches(fslt)
                )

        return SourceLogicTree(fault_system_branches=build_fault_system_branches(slt))

    def resolve_source_logic_tree_spec(root, info, **kwargs):
        log.info("resolve_source_logic_tree_spec kwargs %s" % kwargs)
        model = nzshm_model.get_model_version(root.version)

        slt = model.source_logic_tree()
        spec = slt.derive_spec()

        def build_branch_attribute_values(fslt) -> Iterable:
            for branch in fslt.branches:
                yield BranchAttributeValueSpec(
                    name=branch.name, long_name=branch.long_name, value_options=branch.value_options
                )

        def build_fault_system_branches(spec) -> Iterable:
            for fslt in spec.fault_system_branches:
                yield FaultSystemLogicTreeSpec(
                    short_name=fslt.short_name, long_name=fslt.long_name, branches=build_branch_attribute_values(fslt)
                )

        return SourceLogicTreeSpec(fault_system_branches=build_fault_system_branches(spec))


class NzshmModelResult(graphene.ObjectType):
    model = graphene.Field(NzshmModel)
    ok = graphene.Boolean()
