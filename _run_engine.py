"""Full engine loop from load_exposure.ipynb — run all 27 combinations."""
import pandas as pd
import numpy as np
from climada.entity import Exposures, ImpactFuncSet, ImpfTropCyclone, ImpactFunc
from climada.hazard import Hazard
from climada.util.api_client import Client
from climada.engine import Impact

# --- exposure ---
sites = pd.DataFrame({
    'latitude':      [14.5995, 51.5074, 1.3521, 48.8566],
    'longitude':     [120.9842, -0.1278, 103.8198, 2.3522],
    'value':         [5_000_000, 12_000_000, 8_000_000, 3_000_000],
    'site_name':     ['Manila WH', 'London HQ', 'Singapore DC', 'Paris Office'],
    'headcount':     [120, 450, 85, 200],
    'business_area': ['Logistics', 'Corporate HQ', 'Data Center', 'Sales'],
    'criticality':   ['High', 'Critical', 'Critical', 'Medium'],
    'impf_TC':       [1, 1, 1, 1],
    'impf_FL':       [1, 1, 1, 1],
})
exp = Exposures(sites)

# --- scenarios ---
scenarios = {
    'SSP1-1.9': 'rcp26',
    'SSP2-4.5': 'rcp60',
    'SSP3-7.0': 'rcp85',
}

SITE_COUNTRY = {
    'Manila WH': 'PHL', 'London HQ': 'GBR',
    'Singapore DC': 'SGP', 'Paris Office': 'FRA',
}

hazard_config = {
    'Flooding': {
        'haz_type': 'river_flood', 'impf_id': 'FL', 'time_prop': 'year_range',
        'timeframes': {
            'Short (0-3yr)': '2010_2030',
            'Medium (3-10yr)': '2030_2050',
            'Long (10+yr)': '2050_2070',
        },
        'countries': list(SITE_COUNTRY.values()),
    },
    'Storms': {
        'haz_type': 'tropical_cyclone', 'impf_id': 'TC', 'time_prop': 'ref_year',
        'timeframes': {
            'Short (0-3yr)': '2040',
            'Medium (3-10yr)': '2060',
            'Long (10+yr)': '2080',
        },
        'countries': None,
    },
    'Extreme Precip.': {
        'haz_type': 'river_flood', 'impf_id': 'FL', 'time_prop': 'year_range',
        'timeframes': {
            'Short (0-3yr)': '2010_2030',
            'Medium (3-10yr)': '2030_2050',
            'Long (10+yr)': '2050_2070',
        },
        'countries': list(SITE_COUNTRY.values()),
    },
}

# --- impact functions ---
impf_tc = ImpfTropCyclone.from_emanuel_usa()
impf_fl = ImpactFunc(
    id=1, haz_type='FL', name='Flood damage - general',
    intensity=np.array([0, 0.5, 1, 1.5, 2, 3, 5, 10]),
    mdd=np.array([0, 0.15, 0.30, 0.45, 0.55, 0.70, 0.85, 1.0]),
    paa=np.ones(8),
)
impf_sets = {'TC': ImpactFuncSet([impf_tc]), 'FL': ImpactFuncSet([impf_fl])}

# --- engine loop ---
client = Client()
all_results = []

for haz_name, haz_cfg in hazard_config.items():
    for ssp_name, rcp_code in scenarios.items():
        for tf_name, tf_value in haz_cfg['timeframes'].items():
            print(f"Running: {haz_name} | {ssp_name} | {tf_name}...", flush=True)
            try:
                base_props = {'climate_scenario': rcp_code, haz_cfg['time_prop']: tf_value}

                if haz_cfg['countries']:
                    country_hazards = []
                    for iso3 in haz_cfg['countries']:
                        h = client.get_hazard(
                            haz_cfg['haz_type'],
                            properties={**base_props, 'country_iso3alpha': iso3},
                        )
                        country_hazards.append(h)
                    hazard = Hazard.concat(country_hazards)
                else:
                    hazard = client.get_hazard(
                        haz_cfg['haz_type'],
                        properties={**base_props, 'spatial_coverage': 'global'},
                    )

                imp = Impact()
                imp.calc(exp, impf_sets[haz_cfg['impf_id']], hazard, save_mat=True)

                for idx, (_, row) in enumerate(sites.iterrows()):
                    all_results.append({
                        'site_name':     row['site_name'],
                        'latitude':      row['latitude'],
                        'longitude':     row['longitude'],
                        'headcount':     row['headcount'],
                        'business_area': row['business_area'],
                        'criticality':   row['criticality'],
                        'hazard':        haz_name,
                        'scenario':      ssp_name,
                        'timeframe':     tf_name,
                        'eal':           imp.eai_exp[idx],
                    })
                print(f"  -> OK", flush=True)

            except Exception as e:
                print(f"  Skipped — {e}", flush=True)

results_df = pd.DataFrame(all_results)
out_path = 'c:/Users/engrj/OneDrive/Python/CLIMADA/e1_2_climada_results.csv'
results_df.to_csv(out_path, index=False)
print(f"\nDone. {len(results_df)} rows written to e1_2_climada_results.csv")

# --- disclosure table ---
if not results_df.empty:
    pivot = results_df.pivot_table(
        index=['site_name', 'hazard', 'business_area', 'headcount'],
        columns=['scenario', 'timeframe'],
        values='eal',
        aggfunc='sum',
    )
    summary = results_df.groupby(['scenario', 'timeframe']).agg(
        total_eal=('eal', 'sum'),
        max_site_eal=('eal', 'max'),
        sites_at_risk=('eal', lambda x: (x > 0).sum()),
    ).reset_index()

    pivot.to_excel('c:/Users/engrj/OneDrive/Python/CLIMADA/e1_2_disclosure_table.xlsx')
    print("\n=== SUMMARY ===")
    print(summary.to_string(index=False))
