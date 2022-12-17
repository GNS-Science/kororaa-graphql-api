import json
import unittest
import boto3
import io
from graphene.test import Client
from moto import mock_s3

from kororaa_graphql_api.schema import schema_root
from kororaa_graphql_api.config import S3_BUCKET_NAME, DISAGGS_KEY


#used for test comparisons only
import nzshm_model
import dacite
from nzshm_model.source_logic_tree.logic_tree import (
    Branch,
    BranchAttributeSpec,
    BranchAttributeValue,
    FaultSystemLogicTree,
    SourceLogicTree,
)

class TestNzshmModel(unittest.TestCase):

    def setUp(self):
        self.client = Client(schema_root)

    def test_get_models(self):
        QUERY = """
        query get_models_query {
            nzshm_models {
                model {
                    version
                    title
                }
            }
        }
        """

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        self.assertEqual(res['version'], 'NSHM_1.0.0')
        self.assertEqual(res['title'], 'Initial version')

    def test_get_models_with_slt(self):

        for version in nzshm_model.versions.keys():
            print(version)

        QUERY = """
        query get_models_query {
            nzshm_models {
                model {
                    version
                    source_logic_tree
                }
            }
        }
        """

        executed = self.client.execute(QUERY)
        # print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        self.assertEqual(res['version'], 'NSHM_1.0.0')

        slt = dacite.from_dict(data_class=SourceLogicTree, data=json.loads(res['source_logic_tree']))
        self.assertEqual(slt.version, 'SLT_v8')
        self.assertEqual(slt.fault_system_branches[0].short_name,  'PUY')
        self.assertEqual(slt.fault_system_branches[0].branches[-1].values[0].name,  'dm')
        self.assertEqual(slt.fault_system_branches[0].branches[-1].values[0].value,  '0.7')
        self.assertEqual(slt.fault_system_branches[0].branches[-1].values[1].name,  'bN')
        self.assertEqual(slt.fault_system_branches[0].branches[-1].values[1].value,  [0.902, 4.6])

    def test_get_models_with_spec(self):
        QUERY = """
        query get_models_query {
            nzshm_models {
                model {
                    version
                    title
                    source_logic_tree_spec {
                        fault_system_branches {
                            short_name
                            long_name
                            branches {
                                name
                                long_name
                                value_options
                            }
                        }
                    }
                }
            }
        }
        """

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        self.assertEqual(res['version'], 'NSHM_1.0.0')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['short_name'], 'PUY')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][0]['long_name'], 'deformation model')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][0]['value_options'], json.dumps(['0.7']))

        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][1]['name'], 'bN')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][1]['value_options'], json.dumps([(0.902, 4.6)]))

    def test_get_model_version(self):
        QUERY = """
        query get_model_query {
            nzshm_model (version: "NSHM_1.0.0" ) {
                model {
                    version
                    title
                    source_logic_tree_spec {
                        fault_system_branches {
                            short_name
                            long_name
                            branches {
                                name
                                long_name
                                value_options
                            }
                        }
                    }
                }
            }
        }
        """

        executed = self.client.execute(QUERY)

        print(executed)
        res = executed['data']['nzshm_model']['model']
        self.assertEqual(res['version'], 'NSHM_1.0.0')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['short_name'], 'PUY')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][0]['long_name'], 'deformation model')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][0]['value_options'], json.dumps(['0.7']))

        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][1]['name'], 'bN')
        self.assertEqual(res['source_logic_tree_spec']['fault_system_branches'][0]['branches'][1]['value_options'], json.dumps([(0.902, 4.6)]))
