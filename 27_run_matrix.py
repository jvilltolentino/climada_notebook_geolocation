# SCENARIO MAPPING
# CLIMADA uses RCP labels internally for its data API
scenarios = {
    'SSP1-1.9': 'rcp26',   # Proxy: using SSP1-2.6 data
    'SSP2-4.5': 'rcp45',
    'SSP3-7.0': 'rcp70',
}
 
# TIME FRAME to REFERENCE YEAR
timeframes = {
    'Short (0-3yr)':   '2030',
    'Medium (3-10yr)': '2040',
    'Long (10+yr)':    '2060',
}
 
# HAZARD TYPES to CLIMADA MODULES
hazard_config = {
    'Flooding': {
        'module': 'river_flood',
        'impf_id': 'FL',
    },
    'Storms': {
        'module': 'tropical_cyclone',
        'impf_id': 'TC',
    },
    'Extreme precip.': {
        'module': 'river_flood',   # Derived from rainfall
        'impf_id': 'FL',
    },
}
