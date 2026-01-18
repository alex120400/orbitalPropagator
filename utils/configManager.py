import os

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(UTILS_DIR, '..'))

MISSION_PLAN_PATH = os.path.join(BASE_DIR, "missionplans")
MISSION_PLAN_SUPPORT_PATH = os.path.join(MISSION_PLAN_PATH, "Support_Files")
TRACKING_PATH = os.path.join(BASE_DIR, "tracking")
TLE_DATA_PATH = os.path.join(BASE_DIR, "TLE_data")


STATION_CFG = os.path.join(UTILS_DIR, "stationInformation.json")
MIN_ALTITUDE_ElEVATION = 26

ASI6200CAM_CFG = os.path.join(UTILS_DIR, "ASI6200MMPROConfig.json")

EARTH_DATA_CFG = os.path.join(UTILS_DIR, "earth_data.json") # gps ephemeris
EOP_SW_CFG = os.path.join(UTILS_DIR, "EOP_SW.json")
SPACE_TRACK_CFG = os.path.join(UTILS_DIR, "space_track.json")

OGS_TLE_FILE = os.path.join(TLE_DATA_PATH, "ogs_tle", "Stations.tle")
LEO_TLE_FILE = os.path.join(TLE_DATA_PATH, "elsetsSpaceTrackLEOMostRecent.tle")





