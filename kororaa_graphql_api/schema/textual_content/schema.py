"""The textual content API schema."""

import io
import logging
from datetime import datetime as dt
from pathlib import PurePath

import boto3
import graphene

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter
from kororaa_graphql_api.config import S3_BUCKET_NAME, TEXT_CONTENT_FOLDER_KEY

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")
log = logging.getLogger(__name__)


class ContentStatusEnum(graphene.Enum):
    Undefined = 'UNDEFINED'
    Draft = "DRAFT"
    Published = "PUBLISHED"
    Deprecated = "DEPRECATED"


class ContentFormatEnum(graphene.Enum):
    Raw = "RAW"
    Markdown = "MD"


class TextualContent(graphene.ObjectType):
    """NSHM textual content details."""

    index = graphene.String()
    content_type = graphene.Field(ContentFormatEnum)
    author = graphene.String()
    tags = graphene.List(graphene.String)
    status = graphene.Field(ContentStatusEnum)
    created = graphene.DateTime(description="created date")
    text = graphene.String()

    def resolve_text(root, info, **args):
        """Resolve text."""
        t0 = dt.utcnow()
        log.info('resolve_text root.index: %s' % root.index)
        s3 = boto3.resource('s3')

        s3obj = s3.Object(S3_BUCKET_NAME, str(PurePath(TEXT_CONTENT_FOLDER_KEY, root.index)))
        file_object = io.BytesIO()
        s3obj.download_fileobj(file_object)
        file_object.seek(0)
        content = file_object.read().decode('utf-8')
        db_metrics.put_duration(__name__, 'resolve_text', dt.utcnow() - t0)
        return content


class TextualContentResult(graphene.ObjectType):
    ok = graphene.Boolean()
    content = graphene.List(TextualContent)
