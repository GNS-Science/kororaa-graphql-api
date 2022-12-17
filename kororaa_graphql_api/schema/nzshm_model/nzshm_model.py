#! nzshm_model.py

import logging
from datetime import datetime as dt
from typing import Iterator

import nzshm_model
from kororaa_graphql_api.cloudwatch import ServerlessMetricWriter
from .schema import NzshmModel, NzshmModelResult

log = logging.getLogger(__name__)

db_metrics = ServerlessMetricWriter(metric_name="MethodDuration")

def get_nzshm_models(kwargs) -> Iterator:
    t0 = dt.utcnow()

    for model_version, model in nzshm_model.versions.items():
        yield NzshmModelResult(model=NzshmModel(version=model.version, title=model.title), ok = True)
    db_metrics.put_duration(__name__, 'get_nzshm_models', dt.utcnow() - t0)


def get_nzshm_model(kwargs) -> NzshmModel:
    t0 = dt.utcnow()
    version = kwargs.get('version')
    model = nzshm_model.get_model_version(version)
    res = NzshmModelResult(model=NzshmModel(version=model.version, title=model.title), ok = True)
    db_metrics.put_duration(__name__, 'get_nzshm_model', dt.utcnow() - t0)
    return res
