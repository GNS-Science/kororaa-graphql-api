import json
import unittest
import boto3
import io
import dateutil.parser
from graphene.test import Client
from moto import mock_s3, mock_cloudwatch
from pathlib import Path, PurePath

with mock_cloudwatch():
    from kororaa_graphql_api.schema import schema_root
    from kororaa_graphql_api.config import S3_BUCKET_NAME, TEXT_CONTENT_INDEX_KEY, TEXT_CONTENT_FOLDER_KEY

json_index = Path(__file__).parent / 'fixtures' / 'textual_content_index.json'
TC_INDEX = json.load(open(json_index, 'r'))

markdown_sample = Path(__file__).parent / 'fixtures' / 'help_getting_stopped.md'
MD_SAMPLE = open(markdown_sample, 'r').read()


def setup_content():
    s3 = boto3.resource('s3')
    object = s3.Object(S3_BUCKET_NAME, TEXT_CONTENT_INDEX_KEY)
    object.put(Body=json.dumps(TC_INDEX))

    object = s3.Object(S3_BUCKET_NAME, str(PurePath(TEXT_CONTENT_FOLDER_KEY, TC_INDEX[1]['index'])))
    object.put(Body=MD_SAMPLE)


class TestTextContentS3(unittest.TestCase):
    mock_s3 = mock_s3()

    def setUp(self):
        self.client = Client(schema_root)
        self.mock_s3.start()
        self._s3 = boto3.resource('s3')
        self._s3.create_bucket(Bucket=S3_BUCKET_NAME)
        self._bucket = self._s3.Bucket(S3_BUCKET_NAME)
        setup_content()

    def tearDown(self):
        self.mock_s3.stop()

    def test_s3_create_textual_index(self):

        print(f"S3_BUCKET_NAME {S3_BUCKET_NAME}")
        assert S3_BUCKET_NAME == "S3_BUCKET_NAME_unconfigured"
        s3obj = self._s3.Object(S3_BUCKET_NAME, TEXT_CONTENT_INDEX_KEY)
        file_object = io.BytesIO()
        s3obj.download_fileobj(file_object)
        file_object.seek(0)

        obj = json.load(file_object)
        self.assertEqual(len(obj), 2)
        self.assertEqual(obj[1]['index'], "help_getting_stopped.md")

    def test_s3_create_textual_content(self):

        print(f"S3_BUCKET_NAME {S3_BUCKET_NAME}")
        s3obj = self._s3.Object(S3_BUCKET_NAME, str(PurePath(TEXT_CONTENT_FOLDER_KEY, TC_INDEX[1]['index'])))

        file_object = io.BytesIO()
        s3obj.download_fileobj(file_object)
        file_object.seek(0)

        content = file_object.read().decode('utf-8')
        print(content)
        self.assertTrue("# Help getting stopped" in content)

    def test_get_all_textual_content(self):
        QUERY = """
        query {
                textual_content {
                    ok
                    content {
                        index
                        content_type # RAW, MD
                        text
                        created
                        author
                        tags
                        status
                    }
                }
            }
        """
        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['textual_content']['content']
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['index'], "help_getting_started.md")
        self.assertEqual(res[0]['author'], "Joni Mitchell")
        self.assertEqual(res[0]['tags'], ['help'])
        self.assertEqual(res[0]['status'], 'Published')

        created = dateutil.parser.isoparse("2021-10-01T00:00:00.000+12:00")
        self.assertEqual(res[0]['created'], created.isoformat())

    def test_get_one_textual_content(self):
        QUERY = """
        query {
                textual_content(index: "help_getting_stopped.md") {
                    ok
                    content {
                        index
                        text
                        author
                    }
                }
            }
        """
        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['textual_content']['content']
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['index'], "help_getting_stopped.md")
        self.assertEqual(res[0]['author'], "Hambone Walker")
        self.assertEqual(res[0]['text'], MD_SAMPLE)

    def test_get_tagged_textual_content_one_tag(self):
        QUERY = """
        query {
                textual_content(tags: ["glossary"]) {
                    ok
                    content {
                        index
                        text
                        author
                    }
                }
            }
        """
        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['textual_content']['content']
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['index'], "help_getting_stopped.md")
        self.assertEqual(res[0]['author'], "Hambone Walker")
        self.assertEqual(res[0]['text'], MD_SAMPLE)

    def test_get_tagged_textual_content_two_tag(self):
        QUERY = """
        query {
                textual_content(tags: ["help", "glossary"]) {
                    ok
                    content {
                        index
                        author
                    }
                }
            }
        """
        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['textual_content']['content']
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1]['index'], "help_getting_stopped.md")
        self.assertEqual(res[1]['author'], "Hambone Walker")
