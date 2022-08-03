"""Handl;e Hazard curves from the dataframe JSON."""
import itertools
import logging
from pathlib import Path

import pandas as pd
from .hazard_schema import ToshiHazardCurveResult, ToshiHazardResult, ToshiHazardCurve
from .toshi_hazard_rev0 import lookup_site_code

CWD = Path(__file__)
DF_JSON = str(Path(CWD.parent, '../../resources/FullLT_allIMT_nz34_all_aggregates.json'))
log = logging.getLogger(__name__)


def df_with_site_codes(df):
    """Add site codes to the datframe"""

    def calc_new_col(row):
        return lookup_site_code(lat=row['lat'], lon=row['lon'])

    df["loc"] = df.apply(calc_new_col, axis=1)
    return df


def df_with_vs30s(df):
    """Add vs30 column"""

    def new_col(row):
        return 400

    df["vs30"] = df.apply(new_col, axis=1)
    return df


SLT_TAG_FINAL_DF = df_with_vs30s(df_with_site_codes(pd.read_json(DF_JSON, dtype={'lat': str, 'lon': str})))


def hazard_curves_dataframe(kwargs):
    """Run query against the demo dataframe."""
    assert kwargs.get('hazard_model') == 'DEMO_SLT_TAG_FINAL'

    # print(SLT_TAG_FINAL_DF)
    imts = kwargs.get('imts')
    aggs = kwargs.get('aggs')
    locs = kwargs.get('locs')
    vs30s = kwargs.get('vs30s')

    def filter_df(df, imts, locs, aggs, vs30s):
        imt_filter = df['imt'].isin(imts)
        vs30_filter = df['vs30'].isin(vs30s)
        agg_filter = df['agg'].isin(aggs)
        loc_filter = df['loc'].isin(locs)
        return df[imt_filter & agg_filter & loc_filter & vs30_filter]

    def build_curve(filtered_df, imt, loc, agg, vs30):
        df = filter_df(filtered_df, [imt], [loc], [agg], [vs30])
        log.info("build_curve dataframe: %s" % df)
        levels, values = df['level'].tolist(), df['hazard'].tolist()
        if levels and values:
            return ToshiHazardCurve(levels=levels, values=values)

    def build_response_from_query(df, imts, locs, aggs, vs30s):
        """Todo add vs30s."""

        for (imt, loc, agg, vs30) in itertools.product(imts, locs, aggs, vs30s):
            curve = build_curve(df, imt, loc, agg, vs30)
            if curve:
                yield ToshiHazardResult(
                    hazard_model=kwargs.get('hazard_model'), vs30=vs30, imt=imt, loc=loc, agg=agg, curve=curve
                )

    fdf = filter_df(SLT_TAG_FINAL_DF, imts, locs, aggs, vs30s)
    log.info("hazard_curves_dataframe dataframe: %s" % fdf)
    curves = build_response_from_query(fdf, imts, locs, aggs, vs30s)
    return ToshiHazardCurveResult(ok=True, curves=curves)
