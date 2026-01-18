import os
import json
from time import time
import requests
import gzip
import shutil
import queue

from skyfield.api import load as sky_load

from utils.configManager import MISSION_PLAN_PATH, MISSION_PLAN_SUPPORT_PATH, EOP_SW_CFG, EARTH_DATA_CFG

try:
    from aisolutions.ExampleUtilities import ExampleUtilities
    from aisolutions.freeflyer.runtimeapi.RuntimeApiEngine import RuntimeApiEngine
    from aisolutions.freeflyer.runtimeapi.RuntimeApiException import RuntimeApiException
except ImportError:
    print("Import error!")


class MissionPlanRunner:
    """ Runs Mission Plans """

    def __init__(self):
        self.missionplan_success_flag = None
        self.error_msg = None
        self._ts = sky_load.timescale()
        self._gps_available_flag = False
        self._gps_eph_file = None

        # OD and hybrid plan related variables
        self.obs_length_days = 3 # days
        self.OD_status_queue = queue.Queue()
        self.HYB_ascending_sc_type = "TLE"


        # Get path to runtime library
        self.ff_install_dir = ExampleUtilities.get_freeflyer_install_directory()
        self._update_EOP_and_SW()
        # self._update_GPS_eph_data(force_update_flag=True)


    @staticmethod
    def _update_EOP_and_SW():
        # update EOP (= Earth Orientation Parameters)
        try:
            with open(EOP_SW_CFG) as f:
                EOP_SW_data = json.load(f)
                for key in ["EOP", "space_weather"]:
                    url = EOP_SW_data[key]["url"]
                    file_name = EOP_SW_data[key]["file_name"]
                    output_file_name = os.path.join(MISSION_PLAN_SUPPORT_PATH, file_name)
                    if (time() - os.path.getmtime(output_file_name)) > (1 * 24 * 60 * 60): # download once every day
                        sky_load.download(url, output_file_name)
        except OSError as e:
            print(f"Error while updating EOP and SW:\n{str(e)}")


    def _update_GPS_eph_data(self, force_update_flag=False):
        """ updates GPS ephemeris data for the day and the day before """
        start_up_datetime = self._ts.now().utc_datetime()
        doy = start_up_datetime.timetuple().tm_yday
        yyyy = start_up_datetime.year
        yy = yyyy % 2000 # should work a long time...
        with open(EARTH_DATA_CFG) as f:
            earth_data_data = json.load(f)
            earth_data_user = earth_data_data["credentials"]["username"]
            earth_data_pswd = earth_data_data["credentials"]["password"]
            url_base = earth_data_data["query_base"]
        try:
            self._gps_eph_file = os.path.join(MISSION_PLAN_SUPPORT_PATH, f"brdc{doy:03d}0.{yy}n")
            if os.path.exists(self._gps_eph_file) and not force_update_flag: # check if app was already started today
                self._gps_available_flag = True
                return
            tmp_path = os.path.join(MISSION_PLAN_SUPPORT_PATH, "tmp")
            os.mkdir(tmp_path)  # gps eph zip file will be put there
            gz_file_path = os.path.join(tmp_path, f"brdc{doy:03d}0.{yy}n.gz")
            url = url_base + f"{yyyy}/brdc/brdc{doy:03d}0.{yy}n.gz"
            with requests.Session() as session:
                session.auth = (earth_data_user, earth_data_pswd)
                r1 = session.request('get', url)
                r = session.get(r1.url, auth=(earth_data_user, earth_data_pswd), stream=True)
                r.raise_for_status()
                # Save the gzip file
                with open(gz_file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            # Unzip the file
            with gzip.open(gz_file_path, "rb") as f_in:
                with open(self._gps_eph_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            shutil.rmtree(tmp_path, ignore_errors=False) # remove tmp folder again
            self._gps_available_flag = True
            print("GPS ephemeris updated")
        except Exception as e:
            print(f"Error while updating todays GPS Ephemeris:\n{str(e)}")
            self._gps_available_flag = False


    def run_SGP4_EPH_plan(self, durationMin: float, startTimeUTCString: str):
        """ Runs the sgp4_eph_simulated_tracking_data missionplan which creates eph files to track sgp4 propagated satellites """

        mission_plan_path = os.path.join(MISSION_PLAN_PATH, "SGP4_EPH_simulated_tracking_data.MissionPlan")

        try:
            with RuntimeApiEngine(self.ff_install_dir) as engine:
                with open(os.path.join(MISSION_PLAN_PATH, "TLE_export.tle"), "r") as tle_export_file:
                    for line in tle_export_file.readlines():
                        if line.startswith("0"): # got name of TLE
                            sat_name = line[2:].strip("\n") # remove "0 " and "\n"

                            # run now mission plan
                            engine.loadMissionPlanFromFile(mission_plan_path)

                            engine.prepareMissionPlan()

                            engine.executeUntilApiLabel("Python-Input")

                            engine.setExpressionString("SpaceCraftName", sat_name)
                            engine.setExpressionString("startTime_String", startTimeUTCString)
                            engine.assignExpression("watchWindow_Timespan", f"TIMESPAN({durationMin} minutes)")

                            engine.executeRemainingStatements()
                            engine.cleanupMissionPlan()
                            self.missionplan_success_flag = True

        except RuntimeApiException as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)

        except FileNotFoundError as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)

        except Exception as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)


    def run_OD_HYB_EPH_plan(self, durationMin: float, startTimeUTCString: str, hybrid_flag:bool=False):
        """ Runs one of the missionplans which create eph files to track numerically propagated satellites """

        observation_plan_path = os.path.join(MISSION_PLAN_PATH, "generate_orbit_observations.MissionPlan")

        if hybrid_flag:
            mission_plan_path = os.path.join(MISSION_PLAN_PATH, "HYBRID_EPH_simulated_tracking_data.MissionPlan")
        else:
            mission_plan_path = os.path.join(MISSION_PLAN_PATH, "OD_EPH_simulated_tracking_data.MissionPlan")
        start_time = time()
        try:
            with RuntimeApiEngine(self.ff_install_dir) as engine:
                with open(os.path.join(MISSION_PLAN_PATH, "TLE_export.tle"), "r") as tle_export_file:
                    for line in tle_export_file.readlines():
                        if line.startswith("0"): # got name of TLE
                            sat_name = line[2:].strip("\n") # remove "0 " and "\n"
                            msg_base = f"Analyzing satellite {sat_name}:"
                            self.OD_status_queue.put(msg_base)
                            # generate observation file
                            engine.loadMissionPlanFromFile(observation_plan_path)
                            engine.prepareMissionPlan()
                            engine.executeUntilApiLabel("Python-Input")
                            engine.setExpressionString("SpaceCraftName", sat_name)
                            engine.assignExpression("obs_length", f"TIMESPAN({self.obs_length_days} days)")

                            engine.executeRemainingStatements()
                            engine.cleanupMissionPlan()
                            msg = msg_base + "\nFinished Observation generation"
                            self.OD_status_queue.put(msg)

                            # run now mission plan
                            engine.loadMissionPlanFromFile(mission_plan_path)
                            engine.prepareMissionPlan()
                            engine.executeUntilApiLabel("Python-Input")

                            engine.setExpressionString("SpaceCraftName", sat_name)
                            engine.setExpressionString("startTime_String", startTimeUTCString)
                            engine.assignExpression("watchWindow_Timespan", f"TIMESPAN({durationMin} minutes)")
                            if hybrid_flag:
                                engine.setExpressionString("AscendingSCType", self.HYB_ascending_sc_type)

                            batch_pos_error = 1
                            batch_vel_error = 1
                            # same while exists loop in mission plan
                            self.OD_status_queue.put(msg_base+"\nStarting OD iteration 1")
                            while batch_pos_error > 0.00001 and batch_vel_error > 0.00001:
                                engine.executeUntilApiLabel("Iteration-Finished")
                                finished_it_number = engine.getExpressionVariable("BatchIterationCount")
                                batch_pos_error = engine.getExpressionVariable("batch_pos_change")
                                batch_vel_error = engine.getExpressionVariable("batch_vel_change")
                                msg = msg_base + f"\nCurrent OD iteration: {finished_it_number + 1}"
                                msg += f"\nLast position update: {batch_pos_error:.5f} km"
                                msg += f"\nLast velocity update: {batch_vel_error:.5f} km/s"
                                self.OD_status_queue.put(msg)
                            engine.executeUntilApiLabel("All-Iterations-Finished")
                            msg = msg_base + "\nFinished iterating, now calculating ephemeris"
                            self.OD_status_queue.put(msg)

                            engine.executeRemainingStatements()
                            engine.cleanupMissionPlan()
                            self.OD_status_queue.put(msg_base + f"\nFinished satellite {sat_name}")
                # after iteration through TLE export file
                self.missionplan_success_flag = True
                print(f"Elapsed time with {self.obs_length_days} days obs-length: {time() - start_time}")

        except RuntimeApiException as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)

        except FileNotFoundError as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)

        except Exception as e:
            self.missionplan_success_flag = False
            self.error_msg = str(e)
        finally:
            self.OD_status_queue.put(f"Finished")
