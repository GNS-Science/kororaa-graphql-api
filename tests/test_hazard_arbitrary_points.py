"""Tests for `kororaa_graphql_api` package."""

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

locs = [CodedLocation(o['latitude'], o['longitude'], 0.001) for o in LOCATIONS_BY_ID.values()]


def build_hazard_aggregation_models():

    n_lvls = 29
    lvps = list(map(lambda x: model.LevelValuePairAttribute(lvl=x / 1e3, val=(x / 1e6)), range(1, n_lvls)))
    for (loc, vs30, agg) in itertools.product(locs[:5], vs30s, aggs):
        for imt, val in enumerate(imts):
            yield model.HazardAggregation(
                values=lvps,
                vs30=vs30,
                agg=agg,
                imt=val,
                hazard_model_id=HAZARD_MODEL_ID,
            ).set_location(loc)


def mock_query_response(*args, **kwargs):
    return build_hazard_aggregation_models()


class TestResolveArbitraryLocationToGridded(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema_root)

    # @unittest.skip('not implemented')
    def test_get_gridded_location(self):

        QUERY = """
        query {
            gridded_location (
                lat: %s
                lon: %s
                resolution: %s
                )
            {
                ok
                location {
                    lat
                    lon
                    code
                }
            }
        }
        """ % (
            locs[0].lat,
            locs[0].lon,
            0.1,
        )

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['gridded_location']

        self.assertEqual(res['ok'], True)

        expected = locs[0].downsample(0.1)
        self.assertEqual(res['location']['lon'], expected.lon)
        self.assertEqual(res['location']['lat'], expected.lat)
        self.assertEqual(res['location']['code'], expected.code)
        # assert 0


@mock.patch('toshi_hazard_store.query_v3.get_hazard_curves', side_effect=mock_query_response)
class TestHazardCurvesArbitrary(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema_root)

    def test_get_hazard_for_gridded_with_key_locations(self, mocked_qry):

        # loc_wlg = LOCATIONS_BY_ID['WLG']
        # loc_dud = LOCATIONS_BY_ID['DUD']

        # print(loc_wlg, loc_dud)
        # print()
        # wlg = CodedLocation(loc_wlg['latitude'], loc_wlg['longitude'], 0.1)
        # dud = CodedLocation(loc_dud['latitude'], loc_dud['longitude'], 0.1)
        # locs = [wlg.code, dud.code]

        QUERY = """
        query {
            hazard_curves (
                hazard_model: "%s"
                imts: ["PGA", "SA(0.5)"]
                locs: ["WLG", "DUD"]
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
        """ % (
            HAZARD_MODEL_ID
        )  # , json.dumps(locs))

        executed = self.client.execute(QUERY)
        # print(executed)
        res = executed['data']['hazard_curves']

        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 1)

        # {'id': 'WLG', 'name': 'Wellington', 'latitude': -41.3, 'longitude': 174.78}
        # {'id': 'DUD', 'name': 'Dunedin', 'latitude': -45.87, 'longitude': 170.5}

        mocked_qry.assert_called_with(
            ["-41.300~174.780", "-45.870~170.500"],  # These are the resolved codes for the repective cities by ID
            [400.0, 250.0],
            ['GRIDDED_THE_THIRD'],
            ['PGA', 'SA(0.5)'],
            aggs=["mean", "0.005", "0.995", "0.1", "0.9"],
        )

    def test_get_hazard_for_gridded_with_arb_locations(self, mocked_qry):

        QUERY = """
        query {
            hazard_curves (
                hazard_model: "%s"
                imts: ["PGA", "SA(0.5)"]
                locs: ["-36.9~174.8"]
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
        """ % (
            HAZARD_MODEL_ID
        )

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['hazard_curves']

        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 1)

        mocked_qry.assert_called_with(
            ['-36.900~174.800'],
            [400.0, 250.0],
            ['GRIDDED_THE_THIRD'],
            ['PGA', 'SA(0.5)'],
            aggs=["mean", "0.005", "0.995", "0.1", "0.9"],
        )
