import os
from utils.configManager import MISSION_PLAN_PATH
try:
    from aisolutions.ExampleUtilities import ExampleUtilities
    from aisolutions.freeflyer.runtimeapi.RuntimeApiEngine import RuntimeApiEngine
    from aisolutions.freeflyer.runtimeapi.RuntimeApiException import RuntimeApiException
except ImportError:
    print("Import error!")



mission_plan_path = os.path.join(MISSION_PLAN_PATH,
                                 "20260114TLEs_data_generation_plans",
                                 "OD_PointSolution_approach_simulation.MissionPlan")
observation_data_path = os.path.join(MISSION_PLAN_PATH,
                                    "20260114TLEs_data_generation_plans",
                                    "observation_data")
ff_install_dir = ExampleUtilities.get_freeflyer_install_directory()

try:
    for obs_file_name in os.listdir(observation_data_path):
        with RuntimeApiEngine(ff_install_dir) as engine:
            _, _, ID, sc_name, _ = obs_file_name.split("_")
            print(f"ID: {ID}, Name: {sc_name}, file: {obs_file_name}")
            observation_file_path = os.path.join(".", "observation_data", obs_file_name)

            # run now mission plan
            engine.loadMissionPlanFromFile(mission_plan_path)

            engine.prepareMissionPlan()

            engine.executeUntilApiLabel("Python-Input")

            engine.setExpressionString("SpaceCraftName", sc_name)
            engine.setExpressionString("OD_samples_file", observation_file_path)
            engine.setExpressionString("ID", ID)
            engine.executeRemainingStatements()

            engine.cleanupMissionPlan()

except RuntimeApiException as e:
    print(str(e))

except FileNotFoundError as e:
    print(str(e))

except Exception as e:
    print(str(e))



