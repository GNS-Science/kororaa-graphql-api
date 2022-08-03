"""Tests for `kororaa_graphql_api` package."""

import unittest
from unittest import mock

from graphene.test import Client
from kororaa_graphql_api.schema import schema_root
from toshi_hazard_store import model

HAZ_MODEL_ID = "GRIDDED"
def mock_query_response(*args, **kwargs):

    lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, 11)))
    # print(lvps)

    obj = model.ToshiOpenquakeHazardCurveStats(
        haz_sol_id="ABCDE",
        imt_loc_agg_rk="350:SA(0.5):WLG:0.1",
        loc="WLG",
        agg="0.1",
        imt="SA(0.5)",
        values=lvps,
    )
    return [obj, obj, obj]

@mock.patch('toshi_hazard_store.query.get_hazard_stats_curves', side_effect=mock_query_response)
class TestHazardCurvesArbitrary(unittest.TestCase):
    """

    """

    def setUp(self):
        self.client = Client(schema_root)

    def test_get_hazard_uncertainty(self, mocked_qry):

        QUERY = """
        query {
            hazard_curves (
                hazard_model: "GRIDDED"
                imts: ["PGA", "SA(0.5)"]
                locs: ["WLG", "ZQN"]
                aggs: ["mean", "0.005", "0.995", "0.1", "0.9"]
                vs30s: [400, 250]
                )
            {
                ok
                curves {
                    hazard_model
                    imt
                    loc
                    agg
                    vs30
                    curve {
                        levels
                        values
                    }
                }
            }
        }
        """

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['hazard_curves']

        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 0)

