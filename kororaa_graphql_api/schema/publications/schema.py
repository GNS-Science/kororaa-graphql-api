"""The publications API schema."""

import graphene

"""
nshm_reports {
    ok
    reports {
        topic
        area
        title
        report_number
        lead_author
        reviewers { name }
        publication_date
        bibliographic_ref
        related_datasets { name }
"""


class Person(graphene.ObjectType):
    name = graphene.String()


class ProjectAreaEnum(graphene.Enum):
    Core = "CORE"
    GMCM = "GMCM"
    SRM = "SRM"


class ReportStatusEnum(graphene.Enum):
    Undefined = 'UNDEFINED'
    Review = "REVIEW"
    Published = "PUBLISHED"


class ProjectDataset(graphene.ObjectType):
    name = graphene.String()


class ScienceReport(graphene.ObjectType):
    """NSHM Science report publication details."""

    title = graphene.String(required=False)
    topic = graphene.String()
    area = graphene.Field(ProjectAreaEnum)
    status = graphene.Field(ReportStatusEnum)
    notes = graphene.String(description="Internal notes, not for UI.")
    publication_date = graphene.DateTime(description="publication date")
    report_number = graphene.String(required=False)
    lead_author = graphene.Field(Person)
    reviewers = graphene.List(Person)
    bibliographic_ref = graphene.String()
    # related_datasets = graphene.List(ProjectDataset)


class ScienceReportResult(graphene.ObjectType):
    ok = graphene.Boolean()
    reports = graphene.List(ScienceReport)
