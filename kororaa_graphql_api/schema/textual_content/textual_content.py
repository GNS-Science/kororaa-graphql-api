import io
import json
import logging
from datetime import datetime as dt
from typing import Dict, Iterator, List

import boto3
import dateutil.parser

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter
from kororaa_graphql_api.config import S3_BUCKET_NAME, TEXT_CONTENT_INDEX_KEY

from .schema import ContentFormatEnum, ContentStatusEnum, TextualContent, TextualContentResult

log = logging.getLogger(__name__)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")
s3 = boto3.resource('s3')


def fetch_index_data() -> Iterator:
    log.debug("fetch_index_data() %s from %s " % (TEXT_CONTENT_INDEX_KEY, S3_BUCKET_NAME))
    s3 = boto3.resource('s3')
    s3obj = s3.Object(S3_BUCKET_NAME, TEXT_CONTENT_INDEX_KEY)
    file_object = io.BytesIO()
    s3obj.download_fileobj(file_object)
    file_object.seek(0)
    return json.load(file_object)


def get_textual_content(kwargs):
    """Run query against S#"""
    t0 = dt.utcnow()

    def build_date(obj: Dict):
        try:
            return dateutil.parser.isoparse(obj["created"])
        except:  # noqa
            return

    def build_textual_content(index: str, tags: List[str]) -> Iterator[TextualContent]:
        log.info("build_textual_content")
        for obj in fetch_index_data():

            # return everything
            if not index and not tags:
                yield TextualContent(
                    index=obj['index'],
                    content_type=ContentFormatEnum.get(obj['content_type']),
                    author=obj['author'],
                    tags=obj['tags'],
                    status=ContentStatusEnum.get(obj['status']),
                    created=build_date(obj),
                )
                continue

            # index, ignore tags
            if index and index == obj['index']:
                yield TextualContent(
                    index=obj['index'],
                    content_type=ContentFormatEnum.get(obj['content_type']),
                    author=obj['author'],
                    tags=obj['tags'],
                    status=ContentStatusEnum.get(obj['status']),
                    created=build_date(obj),
                )
                return

            # check tags
            if tags and set(tags).intersection(set(obj['tags'])):
                yield TextualContent(
                    index=obj['index'],
                    content_type=ContentFormatEnum.get(obj['content_type']),
                    author=obj['author'],
                    tags=obj['tags'],
                    status=ContentStatusEnum.get(obj['status']),
                    created=build_date(obj),
                )

    index = kwargs.get('index')
    tags = kwargs.get('tags')
    res = TextualContentResult(ok=True, content=build_textual_content(index, tags))
    db_metrics.put_duration(__name__, 'get_textual_content', dt.utcnow() - t0)
    return res
