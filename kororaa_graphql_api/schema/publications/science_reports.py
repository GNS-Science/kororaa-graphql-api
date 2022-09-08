import io
import json
import logging
from datetime import datetime as dt
from typing import Dict, Iterator

import boto3
import dateutil.parser

from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter
from kororaa_graphql_api.config import PUBLICATIONS_KEY, S3_BUCKET_NAME

from .schema import Person, ProjectAreaEnum, ReportStatusEnum, ScienceReport, ScienceReportResult

log = logging.getLogger(__name__)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")


def fetch_data() -> Iterator:
    log.debug("fetch_data() %s from %s " % (PUBLICATIONS_KEY, S3_BUCKET_NAME))
    s3 = boto3.resource('s3')
    s3obj = s3.Object(S3_BUCKET_NAME, PUBLICATIONS_KEY)
    file_object = io.BytesIO()
    s3obj.download_fileobj(file_object)
    file_object.seek(0)
    return json.load(file_object)


def get_science_reports(kwargs):
    """Run query against S#"""
    t0 = dt.utcnow()

    def build_reviewers(obj: Dict) -> Iterator[Person]:
        for f in ["TAG Reviewer", "TAG Reviewer.1"]:
            if obj[f]:
                print("obj[f]", obj[f])
                yield Person(name=obj[f])

    def build_status_notes(obj: Dict):
        status = obj['Status']
        if status == 'published':
            return (ReportStatusEnum.Published, None)
        if 'done' in status:
            return (ReportStatusEnum.Review, status)
        return (ReportStatusEnum.Undefined, status)

    def build_science_reports() -> Iterator[ScienceReport]:
        log.info("build_science_reports")
        for obj in fetch_data():
            print(obj)
            reviewers = build_reviewers(obj)
            status, notes = build_status_notes(obj)
            yield ScienceReport(
                topic=obj['Report Topic'],
                title=obj['Title'],
                lead_author=Person(name=obj['Lead Author']),
                reviewers=reviewers,
                area=ProjectAreaEnum.get(obj['Area'].upper()),
                status=status,
                notes=notes,
                bibliographic_ref=obj["Bibliographic Reference"],
                report_number=obj['Report Number'],
                publication_date=dateutil.parser.isoparse(obj["Publication date"]),
            )
            # assert 0

    # print(list(build_science_reports()))

    res = ScienceReportResult(ok=True, reports=build_science_reports())
    db_metrics.put_duration(__name__, 'disaggregations', dt.utcnow() - t0)
    return res
