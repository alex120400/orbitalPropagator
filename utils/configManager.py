import os

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(UTILS_DIR, '..'))

# ASI385CAM_CFG = os.path.join(UTILS_DIR, "ASI386MCConfig.json")
# ASI6200CAM_CFG = os.path.join(UTILS_DIR, "ASI6200MMPROConfig.json")
# POINT_GRID_CFG = os.path.join(UTILS_DIR, "pointingGrid.json")
STATION_CFG = os.path.join(UTILS_DIR, "stationInformation.json")
# TEL_LIMITS_CFG = os.path.join(UTILS_DIR, "telescopeLimits.json")
# SAT_TRACK_CFG = os.path.join(UTILS_DIR, "satelliteTracking.json")

# HORIZON_PATH = os.path.join(BASE_DIR, "pointing","data","Horizon.ini")
# ASTROMETRY_PATH = '/usr/local/astrometry/bin/solve-field'
# ASTAP_PATH = '"C:/Program Files/astap/astap_cli.exe"'
# SOFA_LIB = os.path.join(BASE_DIR, "libs","sofa","SOFALibrary.dll")
# IERS_DATA_PATH = os.path.join(BASE_DIR, "pointing","libWrapper","iecs_data.npy")
# REFRACT_PARAM_PATH = os.path.join(BASE_DIR, "sensorData","refract_param.dat")
# XHIP_PATH = os.path.join(BASE_DIR, "libs","hipparcos","xhip","main_xhip.dat")
# XHIP_PHOTO_PATH = os.path.join(BASE_DIR, "libs","hipparcos","xhip","photometric_xhip.dat")
# POINT_GRID_DATA_PATH = os.path.join(BASE_DIR, "pointing","data","pointingGrid.csv")
# POINT_HIP_STAR_PARAMS = os.path.join(BASE_DIR, "pointing","data","hipStarParamsJ2000.csv")
# CPF_PATH = 'D://SpecTrackular//Tracking//CPF'
TLE_DATA_PATH = os.path.join(BASE_DIR, "TLE_data")
OGS_TLE_FILE = os.path.join(TLE_DATA_PATH, "ogs_tle", "Stations.tle") # sample tle file, uses more
LEO_TLE_FILE = os.path.join(TLE_DATA_PATH, "elsetsSpaceTrackLEOMostRecent.tle")
SPACE_TRACK_CFG = os.path.join(UTILS_DIR, "space_track.json")

MISSION_PLAN_PATH = os.path.join(BASE_DIR, "missionplans")
EPHEMERIDES_PATH = os.path.join(BASE_DIR, "ephemerides")