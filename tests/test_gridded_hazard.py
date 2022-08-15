"""Tests for toshi_hazard_rev module."""

import unittest
import itertools
import random
import json
from unittest import mock

from graphene.test import Client
from kororaa_graphql_api.schema import schema_root

from toshi_hazard_haste import model as thh_model  # to be mocked
from nzshm_common.grids import RegionGrid

HAZARD_MODEL_ID = 'GRIDDED_THE_THIRD'
# grid_ids = ['A', 'B']
vs30s = [250, 350, 400]
imts = ['PGA', 'SA(0.5)']
aggs = ['mean', '0.10']


def build_hazard_aggregation_models(*args, **kwargs):
    print('args', args)
    grid_id = args[1]['location_grid_ids'][0]
    try:
        grid_size = len(RegionGrid[grid_id].load())
    except KeyError:
        grid_size = 100

    for (imt, vs30, agg) in itertools.product(imts, vs30s, aggs):

        obj = thh_model.GriddedHazard.new_model(
            hazard_model_id=HAZARD_MODEL_ID,
            location_grid_id=grid_id,
            vs30=vs30,
            imt=imt,
            agg=agg,
            poe=0.02,
            grid_poes=[random.randint(0, 5e6) / 1e6 for x in range(grid_size)],
        )
        print('OBJ', obj)
        yield obj


def mock_query_response(*args, **kwargs):
    return list(build_hazard_aggregation_models(args, kwargs))


@mock.patch(
    'kororaa_graphql_api.schema.toshi_hazard.gridded_hazard.model.get_gridded_hazard', side_effect=mock_query_response
)
class TestGriddedHazard(unittest.TestCase):
    def setUp(self):
        self.client = Client(schema_root)

    def test_get_gridded_hazard_values(self, mocked_qry):

        QUERY = """
        query {
            gridded_hazard (
                grid_id: WLG_0_01_nb_1_1
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
            hazard_model_ids=['GRIDDED_THE_THIRD'],
            location_grid_ids=['WLG_0_01_nb_1_1'],
            vs30s=[400.0, 250.0],
            imts=['PGA', 'SA(0.5)'],
            aggs=['mean', '0.9'],
            poes=[0.1, 0.02],
        )

        self.assertEqual(res['gridded_hazard'][0]['grid_id'], "WLG_0_01_nb_1_1")
        self.assertEqual(len(res['gridded_hazard'][0]['values']), 764)

    def test_get_gridded_hazard_geojson(self, mocked_qry):

        QUERY = """
        query {
            gridded_hazard (
                grid_id: NZ_0_2_NB_1_1
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
                    geojson( color_scale: "inferno", color_scale_vmax:10.0, fill_opacity:0.5)
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
            hazard_model_ids=['GRIDDED_THE_THIRD'],
            location_grid_ids=['NZ_0_2_NB_1_1'],
            vs30s=[400.0, 250.0],
            imts=['PGA', 'SA(0.5)'],
            aggs=['mean', '0.9'],
            poes=[0.1, 0.02],
        )

        self.assertEqual(res['gridded_hazard'][0]['grid_id'], "NZ_0_2_NB_1_1")
        self.assertEqual(len(res['gridded_hazard'][0]['values']), 1057)

        df_json = json.loads(res['gridded_hazard'][0]['geojson'])
        print()
        print(df_json.get('features')[0])
        self.assertEqual(len(res['gridded_hazard'][0]['values']), len(df_json.get('features')))
