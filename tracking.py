from alpaca.telescope import Telescope
import json
from math import pi

from utils.configManager import MIN_ALTITUDE_ElEVATION

class TelescopeWrapper():
    def __init__(self):
        self.telescope = None
        self.connected_flag = False
        self.tel_status = None
        self.sat_status = None
        self.RA_rad = None
        self.DE_rad = None

    def connect_telescope(self):
        try:
            self.telescope = Telescope('localhost:11111', 0)
            self.telescope.Connected = True
            self.connected_flag = True
            return None
        except Exception as e:
            return f'Telescope connection failed:\n{str(e)}'

    def disconnect_telescope(self):
        try:
            self.telescope.Connected = False
            self.connected_flag = False
            return None
        except Exception as e:
            return f'Telescope disconnect failed:\n{str(e)}'

    def start_track(self, eph_filepath):
        # Read all lines from the file
        with open(eph_filepath, "r") as file:
            lines = [line.rstrip('\n') for line in file]  # Strip newlines if needed

        # Serialize the list of lines to JSON
        lines_list_serialized = json.dumps(lines)
        try:
            self.telescope.Action("sat:ephlines", lines_list_serialized)

            # provide telescope with min elevation (=altitude) and start track
            self.telescope.Action("sat:startalt", MIN_ALTITUDE_ElEVATION)
            self.telescope.Action("sat:start", "")
            return None
        except Exception as e:
            return f"Tracking failed:\n{str(e)}"

    def get_telescope_status(self):
        if not self.connected_flag:
            return "Telescope not connected!"

        try:
            # Ask the telescope for its tel_status as JSON
            json_string = self.telescope.CommandString("GetTelStatus", True)
            # status byte is not so useful, tracking bit seems dead, slewing & parking only after home call in Autoslew
            # updated
            # but RA and DE sent were useful (in deg) -> use to minitor progress and update tel_status field in GUI
            # Parse JSON into a Python dict
            self.tel_status = json.loads(json_string)
            # will be dict of structure:
            # {'JulianDate': 2461006.2802302544,
            # 'RigthAscension': 3.2274482228661365,
            # 'Declination': 3.165783924470721, 'Status': 2,
            # 'ErrornumberAxis1': 0, 'ErrornumberAxis2': 2304}
            self.RA_rad = self.tel_status['RigthAscension'] / 180 * pi
            self.DE_rad = self.tel_status['Declination'] / 180 * pi
            print("Telescope Status is:")
            print(self.tel_status)
            print(f"RA: {self.RA_rad:.4f}, DE: {self.DE_rad:.4f}")
            return None

        except Exception as e:
            return f"Telescope status Request tailed:\n{str(e)}"

    def get_satellite_status(self):
        if not self.connected_flag:
            return "Telescope not connected!"

        try:
            # Ask the telescope for its tel_status as JSON
            json_string = self.telescope.CommandString("getSatStatus", True)

            # Parse JSON into a Python dict
            self.sat_status = json.loads(json_string)
            print("Satellite Status is:")
            print(self.sat_status)
            return None

        except Exception as e:
            return f"Satellite status Request tailed:\n{str(e)}"


