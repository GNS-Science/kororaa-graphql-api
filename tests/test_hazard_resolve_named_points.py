"""Tests for toshi_hazard_rev module."""

import unittest
import itertools
from unittest import mock

from graphene.test import Client
from kororaa_graphql_api.schema import schema_root
from toshi_hazard_store import model

from nzshm_common.location import CodedLocation
from nzshm_common.location.location import LOCATIONS_BY_ID

HAZARD_MODEL_ID = 'GRIDDED_THE_THIRD'
vs30s = [250, 350, 450]
imts = ['PGA', 'SA(0.5)']
aggs = ['mean', '0.10']

@mock.patch('toshi_hazard_store.query_v3.get_hazard_curves')
class TestHazardCurvesNamed(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema_root)

    def test_get_wlg_by_shortcode(self, mocked_qry):

        QUERY = """
        query {
            hazard_curves (
                locs: ["WLG"]
                hazard_model: "%s"
                imts: ["PGA"]
                aggs: ["mean"]
                vs30s: [400]
                )
            {
                ok
                curves {
                    hazard_model
                    curve {
                        levels
                        values
                    }
                }
            }
        }
        """ % (
            HAZARD_MODEL_ID
        )  # , json.dumps(locs))

        executed = self.client.execute(QUERY)
        try:
            res = executed['data']['hazard_curves']
        except:
            print(executed)

        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 1)
        mocked_qry.assert_called_with(
            ["-41.300~174.780"],  # the resolved codes for the respective cities by ID
            [400.0],
            ['GRIDDED_THE_THIRD'],
            ['PGA'],
            aggs=["mean"],
        )

    def test_get_wlg_by_latlon(self, mocked_qry):

        QUERY = """
        query {
            hazard_curves (
                locs: ["-41.30~174.78"]
                hazard_model: "%s"
                imts: ["PGA"]
                aggs: ["mean"]
                vs30s: [400]
                )
            {
                ok
                curves {
                    hazard_model
                    curve {
                        levels
                        values
                    }
                }
            }
        }
        """ % (
            HAZARD_MODEL_ID
        )  # , json.dumps(locs))

        executed = self.client.execute(QUERY)
        try:
            res = executed['data']['hazard_curves']
        except:
            print(executed)

        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 1)
        mocked_qry.assert_called_with(
            ["-41.300~174.780"],  # the resolved codes for the respective cities by ID
            [400.0],
            ['GRIDDED_THE_THIRD'],
            ['PGA'],
            aggs=["mean"])
