import json
import unittest
import boto3
import io
from graphene.test import Client
from moto import mock_s3

# from kororaa_graphql_api.datastore import *
from kororaa_graphql_api.schema import schema_root
from kororaa_graphql_api.config import S3_BUCKET_NAME

DISAGGS_KEY = 'DISAGGS/disaggs.json'
DISAGGS = [
    {
        "model_id": "SLT_v8_gmm_v2",
        "location": "-41.300~174.780",
        "location_name": "Wellington",
        "imt": "PGA",
        "poe": 2,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
    {
        "model_id": "SLT_v8_gmm_v2",
        "location": "-41.300~174.780",
        "location_name": "Wellington",
        "imt": "SA(0.5)",
        "poe": 2,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
    {
        "model_id": "SLT_v8_gmm_v2",
        "location": "-41.300~174.780",
        "location_name": "Wellington",
        "imt": "SA(0.5)",
        "poe": 10,
        "inv_time": 50,
        "report_url": "http://fake-plastic-trees/DATA/slt_v8_gmm_v2/diagreport_report/XXX",
    },
]


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
        self.assertEqual(obj[0]['model_id'], "SLT_v8_gmm_v2")

    @unittest.skip('not implemented')
    def test_get_disaggs(self):
        QUERY = """
        query {
            disaggregations {
                ok
                disaggregations {
                    model_id
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
        res = executed['data']['disaggregations']['disaggregations']
        self.assertEqual(len(res), 3)
