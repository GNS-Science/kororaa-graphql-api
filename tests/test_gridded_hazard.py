"""Tests for toshi_hazard_rev module."""

import unittest
import itertools
import random
from unittest import mock

from graphene.test import Client
from kororaa_graphql_api.schema import schema_root

# from toshi_hazard_store import model

from toshi_hazard_haste import model as thh_model  # to be mocked

# from nzshm_common.grids import RegionGrid

HAZARD_MODEL_ID = 'GRIDDED_THE_THIRD'
# grid_ids = ['A', 'B']
vs30s = [250, 350, 400]
imts = ['PGA', 'SA(0.5)']
aggs = ['mean', '0.10']

# import kororaa_graphql_api.schema.toshi_hazard.gridded_hazard

# locs = [CodedLocation(o['latitude'], o['longitude'], 0.001) for o in LOCATIONS_BY_ID.values()]


def build_hazard_aggregation_models():
    for (imt, vs30, agg) in itertools.product(imts, vs30s, aggs):
        obj = thh_model.GriddedHazard.new_model(
            hazard_model_id=HAZARD_MODEL_ID,
            location_grid_id="NZGRID_0_1",
            vs30=vs30,
            imt=imt,
            agg=agg,
            poe=0.02,
            grid_poes=[random.randint(0, 5e6) / 1e6 for x in range(100)],
        )
        print('OBJ', obj)
        yield obj


def mock_query_response(*args, **kwargs):
    return list(build_hazard_aggregation_models())


@mock.patch(
    'kororaa_graphql_api.schema.toshi_hazard.gridded_hazard.model.get_gridded_hazard', side_effect=mock_query_response
)
class TestHazardCurvesArbitrary(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema_root)

    def test_get_hazard_for_gridded_with_key_locations(self, mocked_qry):

        QUERY = """
        query {
            gridded_hazard (
                grid_id: "NZGRID_0_1"
                hazard_model_ids: ["%s"]
                imts: ["PGA", "SA(0.5)"]
                aggs: ["mean", "0.9"]
                vs30s: [400, 250]
                poes: [0.1, 0.02]
                )
            {
                ok
                gridded_hazard {
                    grid_id
                    hazard_model
                    imt
                    agg
                    vs30
                    values
                }
            }
        }
        """ % (
            HAZARD_MODEL_ID
        )  # , json.dumps(locs))

        executed = self.client.execute(QUERY)
        print(executed)
        res = executed['data']['gridded_hazard']
        self.assertEqual(res['ok'], True)
        self.assertEqual(mocked_qry.call_count, 1)

        mocked_qry.assert_called_with(
            "NZGRID_0_1", [0.1, 0.02], ['GRIDDED_THE_THIRD'], [400.0, 250.0], ['PGA', 'SA(0.5)'], aggs=["mean", "0.9"]
        )

        self.assertEqual(res['gridded_hazard'][0]['grid_id'], "NZGRID_0_1")
        self.assertEqual(len(res['gridded_hazard'][0]['values']), 100)