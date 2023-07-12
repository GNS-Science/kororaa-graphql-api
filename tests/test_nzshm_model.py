import json
from graphene.test import Client

from moto import mock_cloudwatch
with mock_cloudwatch():
    from kororaa_graphql_api.schema import schema_root

import nzshm_model
import pytest


@pytest.fixture(scope='module')
def client():
    return Client(schema_root)


class TestNzshmModel:
    def test_get_models(self, client):
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

        executed = client.execute(QUERY)
        print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        assert res['version'] == 'NSHM_1.0.0'
        assert res['title'] == 'Initial version'

    def test_get_models_with_slt(self, client):

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

        executed = client.execute(QUERY)
        print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        fsb = res['source_logic_tree']['fault_system_branches']
        assert res['version'] == 'NSHM_1.0.0'

        assert fsb[0]['short_name'] == 'PUY'
        assert fsb[0]['branches'][-1]['values'][0]['name'] == 'dm'
        assert fsb[0]['branches'][-1]['values'][0]['json_value'] == json.dumps('0.7')

        assert fsb[0]['branches'][-1]['values'][1]['name'] == 'bN'
        assert fsb[0]['branches'][-1]['values'][1]['json_value'] == json.dumps([0.902, 4.6])
        assert fsb[0]['branches'][-1]['onfault_nrml_id'] == "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcyOQ=="
        # "distributed_nrml_id": "RmlsZToxMzA3NTM=",
        # "inversion_solution_id": "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTE4NTQ2",
        # "inversion_solution_type": "ScaledInversionSolution"

    def test_get_models_with_spec(self, client):
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

        executed = client.execute(QUERY)
        print(executed)
        res = executed['data']['nzshm_models'][0]['model']
        fsb = res['source_logic_tree_spec']['fault_system_branches']

        assert res['version'] == 'NSHM_1.0.0'
        assert fsb[0]['short_name'] == 'PUY'
        assert fsb[0]['branches'][0]['long_name'] == 'deformation model'
        assert fsb[0]['branches'][0]['value_options'] == json.dumps(['0.7'])

        assert fsb[0]['branches'][1]['name'] == 'bN'
        assert fsb[0]['branches'][1]['value_options'] == json.dumps([(0.902, 4.6)])

    @pytest.mark.parametrize(
        "model_id,expected", [("NSHM_1.0.0", json.dumps([(0.902, 4.6)])), ("NSHM_1.0.4", json.dumps([(0.902, 4.6)]))]
    )
    def test_get_model_version(self, client, model_id, expected):
        QUERY = """
        query get_model_query( $model_id: String!) {
            nzshm_model (version: $model_id ) {
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

        executed = client.execute(QUERY, variable_values={"model_id": model_id})

        print(executed)
        res = executed['data']['nzshm_model']['model']
        assert res['version'] == model_id
        fsb = res['source_logic_tree_spec']['fault_system_branches']
        assert fsb[0]['short_name'] == 'PUY'
        assert fsb[0]['branches'][0]['long_name'] == 'deformation model'
        assert fsb[0]['branches'][0]['value_options'] == json.dumps(['0.7'])
        assert fsb[0]['branches'][1]['name'] == 'bN'
        assert fsb[0]['branches'][1]['value_options'] == expected
