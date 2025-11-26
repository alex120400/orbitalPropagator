from alpaca.telescope import Telescope
import json

from utils.configManager import MIN_ALTITUDE_ElEVATION

class TelescopeWrapper():
    def __init__(self):
        self.telescope = None
        self.connected_flag = False
        self.status = None

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

    def get_status(self):
        if not self.connected_flag:
            return "Telescope not connected!"

        try:
            # Ask the telescope for its status as JSON
            json_string = self.telescope.CommandString("GetTelStatus", True)

            # Parse JSON into a Python dict
            self.status = json.loads(json_string)
            print("Telescope Status is:")
            print(self.status)
            return None

        except Exception as e:
            return f"Telescope status Request tailed:\n{str(e)}"


