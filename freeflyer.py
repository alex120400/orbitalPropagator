import os
from utils.configManager import MISSION_PLAN_PATH

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

    def run_SGP4_EPH_plan(self, durationMin: float, startTimeUTCString: str):
        """ Runs the sgp4_eph missionplan which creates eph files to track sgp4 propagated satellites """

        mission_plan_path = os.path.join(MISSION_PLAN_PATH, "SGP4_EPH.MissionPlan")

        try:
            with RuntimeApiEngine(self.ff_install_dir) as engine:
                with open(os.path.join(MISSION_PLAN_PATH, "TLE_export.tle"), "r") as tle_export_file:
                    for line in tle_export_file.readlines():
                        if line.startswith("0"): # got name of TLE
                            sat_name = line[2:].strip("\n") # remove "0 " and "\n"

                            # run now mission plan
                            print("Load the Mission Plan.")
                            engine.loadMissionPlanFromFile(mission_plan_path)

                            print("Prepare to execute statements.")
                            engine.prepareMissionPlan()

                            print("Run to the 'Python-Input' label.")
                            engine.executeUntilApiLabel("Python-Input")

                            print("assign satellite name, watchwindow and startTime")

                            engine.setExpressionString("SpaceCraftName", sat_name)
                            engine.setExpressionString("startTime_String", startTimeUTCString)
                            engine.assignExpression("watchWindow_Timespan", f"TIMESPAN({durationMin} minutes)")

                            print("Execute the remaining Mission Plan.")
                            engine.executeRemainingStatements()

                            print("Clean up the Mission Plan.")
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



