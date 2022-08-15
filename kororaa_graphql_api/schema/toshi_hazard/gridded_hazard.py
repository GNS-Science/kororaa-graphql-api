"""Build Gridded Hazard."""
import logging

import graphene
from toshi_hazard_haste import model

from .hazard_schema import GriddedLocation

log = logging.getLogger(__name__)


class GriddedHazard(graphene.ObjectType):
    grid_id = graphene.String(description="Grid ENUM")
    hazard_model = graphene.String()
    imt = graphene.String()
    agg = graphene.String()
    vs30 = graphene.Float()
    poe = graphene.Float()
    values = graphene.List(graphene.Float, description="Acceleration values.")
    grid_locations = graphene.List(GriddedLocation)


class GriddedHazardResult(graphene.ObjectType):
    gridded_hazard = graphene.Field(graphene.List(GriddedHazard))
    ok = graphene.Boolean()


def query_gridded_hazard(kwargs):
    """Run query against dynamoDB."""
    """
    yield model.GriddedHazard.new_model(
            hazard_model_id=hazard_model_id,
            location_grid_id=location_grid_id,
            vs30=vs30,
            imt=imt,
            agg=agg,
            poe=poe_lvl,
            grid_poes=grid_poes,
        )

    """

    def build_response_from_query(result):
        log.info("build_response_from_query %s" % result)
        for obj in result:
            yield GriddedHazard(
                grid_id=obj.location_grid_id,
                hazard_model=obj.hazard_model_id,
                vs30=obj.vs30,
                imt=obj.imt,
                agg=obj.agg,
                poe=obj.poe,
                values=obj.grid_poes,
            )
        """
        def calc_gridded_hazard(
            location_grid_id: str,
            poe_levels: Iterable[float],
            hazard_model_ids: Iterable[str],
            vs30s: Iterable[float],
            imts: Iterable[str],
            aggs: Iterable[str],
            filter_locations: Iterable[CodedLocation] = None,
        """

    response = model.get_gridded_hazard(
        kwargs['grid_id'],
        kwargs['poes'],
        kwargs['hazard_model_ids'],
        kwargs['vs30s'],
        kwargs['imts'],
        aggs=kwargs['aggs'],
    )
    print('response', response)
    return GriddedHazardResult(ok=True, gridded_hazard=build_response_from_query(response))
