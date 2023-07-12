import json
import unittest
import io
import os
from graphene.test import Client
import boto3

from moto import mock_s3, mock_cloudwatch
import pytest

with mock_cloudwatch():
    from kororaa_graphql_api.schema import schema_root
    from kororaa_graphql_api.config import S3_BUCKET_NAME, DISAGGS_KEY

DISAGGS = [
    {
        "hazard_model": "SLT_v8_gmm_v2",
        "location_code": "-41.300~174.780",
        "location_key": "WLG",
        "imt": "PGA",
        "vs30": 400,
        "poe": 0.02,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
    {
        "hazard_model": "SLT_v8_gmm_v2",
        "location_code": "-41.300~174.780",
        "location_key": "WLG",
        "imt": "SA(0.5)",
        "vs30": 400,
        "poe": 0.02,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
    {
        "hazard_model": "SLT_v8_gmm_v2",
        "location_code": "-41.300~174.780",
        "location_key": "WLG",
        "imt": "SA(0.5)",
        "vs30": 400,
        "poe": 0.1,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
]

# def test_create_bucket(s3):
#     # s3 is a fixture defined above that yields a boto3 s3 client.
#     # Feel free to instantiate another boto3 S3 client -- Keep note of the region though.
#     s3.create_bucket(Bucket="somebucket")

#     result = s3.list_buckets()
#     assert len(result["Buckets"]) == 1
#     assert result["Buckets"][0]["Name"] == "somebucket"

def setup_disaggs():
    s3 = boto3.resource('s3')
    object = s3.Object(S3_BUCKET_NAME, DISAGGS_KEY)
    object.put(Body=json.dumps(DISAGGS))

class TestDisaggsWithS3(unittest.TestCase):
    mock_s3 = mock_s3()

    def setUp(self):
        self.client = Client(schema_root)
        self.mock_s3.start()
        self._s3 = boto3.resource('s3')
        self._s3.create_bucket(Bucket=S3_BUCKET_NAME)
        self._bucket = self._s3.Bucket(S3_BUCKET_NAME)
        setup_disaggs()

    def tearDown(self):
        self.mock_s3.stop()

    def test_s3_create_disaggs(self):

        print(f"S3_BUCKET_NAME {S3_BUCKET_NAME}")
        assert S3_BUCKET_NAME == "S3_BUCKET_NAME_unconfigured"
        s3obj = self._s3.Object(S3_BUCKET_NAME, DISAGGS_KEY)
        file_object = io.BytesIO()
        s3obj.download_fileobj(file_object)
        file_object.seek(0)

        obj = json.load(file_object)
        self.assertEqual(len(obj), 3)
        self.assertEqual(obj[0]['hazard_model'], "SLT_v8_gmm_v2")

    # @unittest.skip('not implemented')
    def test_get_disaggs(self):
        QUERY = """
        query {
            disaggregation_reports {
                ok
                reports {
                    hazard_model
                    location {
                        name
                        code
                        key
                    }
                    imt
                    poe
                    inv_time
                    report_url
                }
            }
        }
        """

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['disaggregation_reports']['reports']
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]['hazard_model'], "SLT_v8_gmm_v2")
        self.assertEqual(res[0]['location']['code'], "-41.30~174.78")
        self.assertEqual(res[0]['location']['name'], "Wellington")
