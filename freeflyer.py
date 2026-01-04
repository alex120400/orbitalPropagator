import os
import json
from time import time

from skyfield.api import load as sky_load

from utils.configManager import MISSION_PLAN_PATH, EOP_SW_CFG

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

        # Get path to runtime library
        self.ff_install_dir = ExampleUtilities.get_freeflyer_install_directory()
        print(self.ff_install_dir)
        self._update_EOP_and_SW()

    def _update_EOP_and_SW(self):
        tmp_path = "utils"
        data_path = os.path.join(self.ff_install_dir, "data", "misc")
        # update EOP (= Earth Orientation Parameters)
        try:
            with open(EOP_SW_CFG) as f:
                EOP_SW_data = json.load(f)
                for key in ["EOP", "space_weather"]:
                    url = EOP_SW_data[key]["url"]
                    file_name = EOP_SW_data[key]["file_name"]
                    tmp_file_name = os.path.join(tmp_path, file_name)
                    output_file_name = os.path.join(data_path, file_name)
                    if (time() - os.path.getmtime(tmp_file_name)) > (1 * 24 * 60 * 60): # download once every day
                        sky_load.download(url, tmp_file_name)
                        # os.replace(tmp_file_name, output_file_name) # will not work, load files in ff
        except OSError as e:
            print(f"Error while updating EOP and SW:\n{str(e)}")

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



