import json
import unittest
from graphene.test import Client

from kororaa_graphql_api.schema import schema_root
import nzshm_model

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
                    source_logic_tree {
                        fault_system_branches {
                            short_name
                            long_name
                            branches {
                                weight
                                onfault_nrml_id
                                values {
                                    name
                                    long_name
                                    json_value
                                }
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

        # slt = dacite.from_dict(data_class=SourceLogicTree, data=json.loads(res['source_logic_tree']))
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['short_name'],  'PUY')
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['branches'][-1]['values'][0]['name'],  'dm')
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['branches'][-1]['values'][0]['json_value'],  json.dumps('0.7'))
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['branches'][-1]['values'][1]['name'],  'bN')
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['branches'][-1]['values'][1]['json_value'],  json.dumps([0.902, 4.6]))
        self.assertEqual(res['source_logic_tree']['fault_system_branches'][0]['branches'][-1]['onfault_nrml_id'], "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcyOQ==")
        # "distributed_nrml_id": "RmlsZToxMzA3NTM=",
        # "inversion_solution_id": "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE4NTQ2",
        # "inversion_solution_type": "ScaledInversionSolution"


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
