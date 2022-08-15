"""Tests for `kororaa_graphql_api` package."""

# from unittest import mock

# import datetime as dt
import unittest
from unittest import mock

# from dateutil.tz import tzutc

from graphene.test import Client

from kororaa_graphql_api.schema import schema_root
from kororaa_graphql_api.kororaa_graphql_api import create_app
from toshi_hazard_store import model


class TestFlaskApp(unittest.TestCase):
    """Tests the basic app create."""

    def test_create_app(self):
        app = create_app()
        print(app)
        assert app


class TestSchemaAboutResolver(unittest.TestCase):
    """
    A simple `About` resolver returns some metadata about the API.
    """

    def setUp(self):
        self.client = Client(schema_root)

    def test_get_about(self):

        QUERY = """
        query {
            about
        }
        """

        executed = self.client.execute(QUERY)
        print(executed)
        self.assertTrue('Hello World' in executed['data']['about'])


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
class TestHazardCurvesResolver(unittest.TestCase):
    """
    The masthead feature of this  API rev0.
    """

    def setUp(self):
        self.client = Client(schema_root)

    def test_get_about(self, mocked_qry):

        QUERY = """
        query {
            hazard_curves (
                hazard_model: "TEST1"
                imts: ["PGA", "SA(0.5)"]
                locs: ["WLG", "QZN"]
                aggs: ["0.1", "mean"]
                vs30s: [250]
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

        self.assertEqual(mocked_qry.call_count, 1)
        self.assertEqual(res['ok'], True)
        self.assertEqual(len(res['curves']), 3)
        self.assertEqual(res['curves'][0]['hazard_model'], "TEST1")
        self.assertEqual(res['curves'][0]['vs30'], 250)
