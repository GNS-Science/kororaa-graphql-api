import json
import unittest
import boto3
import io
import dateutil.parser
from graphene.test import Client
from moto import mock_s3

from kororaa_graphql_api.schema import schema_root
from kororaa_graphql_api.config import S3_BUCKET_NAME, PUBLICATIONS_KEY


raw = '''
[
    {
      "index":0,
      "Report Topic":"NSHM Framework Plan",
      "Lead Author":"Matt Gerstenberger",
      "TAG Reviewer":"Full TAG",
      "TAG Reviewer.1":null,
      "Publication date":"2021-10-01T00:00:00.000Z",
      "Associated output and location":"x",
      "Area":"Core",
      "Status":"published",
      "Title":"New Zealand National Seismic Hazard Model Framework Plan",
      "Bibliographic Reference":"Gerstenberger MC, Van Houtte C, Abbott ER, Van Dissen RJ, Kaiser\u00a0AE, Bradley B, Nicol A, Rhoades DA, Stirling MW, Thingbaijam\u00a0KKS, NSHM Team. 2020. New Zealand National Seismic Hazard Model framework plan. Lower Hutt (NZ): GNS\u00a0Science. 25\u00a0p. (GNS Science report; 2020\/38). doi:10.21420\/NB8W-GA79.",
      "Report Number":"SSR 2020/38",
      "Associated data set":"none"
    },
    {
      "index":1,
      "Report Topic":"Seismogenic Thickness Maps",
      "Lead Author":"Susan Ellis",
      "TAG Reviewer":"John Townend",
      "TAG Reviewer.1":"Trevor Allen",
      "Publication date":"2021-04-01T00:00:00.000Z",
      "Associated output and location":"x",
      "Area":"SRM",
      "Status":"nearly done",
      "Title":null,
      "Bibliographic Reference":null,
      "Report Number":null,
      "Associated data set":null
    }
]
'''  # noqa
raw = raw.replace('\/', '/')  # noqa
# print(raw)
# assert 0
PUBS = json.loads(raw)


def setup_publications():
    s3 = boto3.resource('s3')
    object = s3.Object(S3_BUCKET_NAME, PUBLICATIONS_KEY)
    object.put(Body=json.dumps(PUBS))


class TestDisaggsWithS3(unittest.TestCase):
    mock_s3 = mock_s3()

    def setUp(self):
        self.client = Client(schema_root)
        self.mock_s3.start()
        self._s3 = boto3.resource('s3')
        self._s3.create_bucket(Bucket=S3_BUCKET_NAME)
        self._bucket = self._s3.Bucket(S3_BUCKET_NAME)
        setup_publications()

    def tearDown(self):
        self.mock_s3.stop()

    def test_s3_create_publications(self):

        print(f"S3_BUCKET_NAME {S3_BUCKET_NAME}")
        assert S3_BUCKET_NAME == "S3_BUCKET_NAME_unconfigured"
        s3obj = self._s3.Object(S3_BUCKET_NAME, PUBLICATIONS_KEY)
        file_object = io.BytesIO()
        s3obj.download_fileobj(file_object)
        file_object.seek(0)

        obj = json.load(file_object)
        self.assertEqual(len(obj), 2)
        self.assertEqual(obj[1]['Report Topic'], "Seismogenic Thickness Maps")

    # @unittest.skip('not implemented')
    def test_get_publications(self):
        QUERY = """
        query {
            science_reports {
                ok
                reports {
                    topic
                    area
                    title
                    status
                    notes
                    report_number
                    lead_author { name }
                    reviewers { name }
                    publication_date
                    bibliographic_ref
                    # related_datasets { name }
                }
            }
        }
        """
        biblio = "Gerstenberger MC, Van Houtte C, Abbott ER, Van Dissen RJ, Kaiser\u00a0AE, Bradley B, Nicol A, Rhoades DA, Stirling MW, Thingbaijam\u00a0KKS, NSHM Team. 2020. New Zealand National Seismic Hazard Model framework plan. Lower Hutt (NZ): GNS\u00a0Science. 25\u00a0p. (GNS Science report; 2020/38). doi:10.21420/NB8W-GA79."  # noqa

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['science_reports']['reports']
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['topic'], "NSHM Framework Plan")
        self.assertEqual(res[0]['title'], "New Zealand National Seismic Hazard Model Framework Plan")
        self.assertEqual(res[0]['reviewers'][0]['name'], "Full TAG")
        self.assertEqual(res[1]['lead_author']['name'], "Susan Ellis")
        self.assertEqual(res[0]['area'], 'Core')
        self.assertEqual(res[0]['status'], 'Published')
        self.assertEqual(res[0]['notes'], None)
        self.assertEqual(res[1]['status'], 'Review')
        self.assertEqual(res[1]['notes'], 'nearly done')
        self.assertEqual(res[0]['bibliographic_ref'], biblio)

        self.assertEqual(res[0]['report_number'], "SSR 2020/38")
        pubdate = dateutil.parser.isoparse("2021-10-01T00:00:00.000Z")
        self.assertEqual(res[0]['publication_date'], pubdate.isoformat())
        # self.assertEqual(res[0]['related_datasets'], [])
