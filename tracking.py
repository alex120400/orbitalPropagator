from alpaca.telescope import Telescope
import json
from math import pi

from utils.configManager import MIN_ALTITUDE_ElEVATION

class TelescopeWrapper():
    def __init__(self):
        self._telescope = None
        self.connected_flag = False
        self.tracking_flag = None
        self._tel_status = None
        self._sat_status = None
        self.RA_rad = None
        self.DE_rad = None
        self.tracking_bit = 0
        self.slewing_bit = 0

    def connect_telescope(self):
        try:
            self._telescope = Telescope('localhost:11111', 0)
            self._telescope.Connected = True
            self.connected_flag = True
            return None
        except Exception as e:
            return f'Telescope connection failed:\n{str(e)}'

    def disconnect_telescope(self):
        try:
            self._telescope.Connected = False
            self.connected_flag = False
            return None
        except Exception as e:
            return f'Telescope disconnect failed:\n{str(e)}'

    def start_track(self, eph_filepath):
        # check if tracking is not ongoing
        if self.tracking_flag:
            return "Track is ongoing! Cannot start a new one!"
        # Read all lines from the file
        with open(eph_filepath, "r") as file:
            lines = [line.rstrip('\n') for line in file]  # Strip newlines if needed

        # Serialize the list of lines to JSON
        lines_list_serialized = json.dumps(lines)
        try:
            self._telescope.Action("sat:ephlines", lines_list_serialized)

            # provide telescope with min elevation (=altitude) and start track
            self._telescope.Action("sat:startalt", MIN_ALTITUDE_ElEVATION)
            self._telescope.Action("sat:start", "")
            self.tracking_flag = True
            return None
        except Exception as e:
            return f"Tracking failed:\n{str(e)}"

    def update_status(self):
        if not self.connected_flag:
            return "Telescope not connected!"
        try:
            # Ask the telescope for its tel_status as JSON
            json_string = self._telescope.CommandString("GetTelStatus", True)
            # status byte is not so useful, tracking bit seems dead, slewing & parking only
            # after home call in Autoslew updated
            # but RA and DE useful (in deg) -> use to minitor progress and update fields in GUI
            self._tel_status = json.loads(json_string) # Parse JSON into a Python dict
            # will be dict of structure:
            # {'JulianDate': 2461006.2802302544,
            # 'RigthAscension': 3.2274482228661365, 'Declination': 3.165783924470721,
            # 'Status': 2, # bit 0: tracking (not working); bit 1: at park; bit 2: slewing
            # 'ErrornumberAxis1': 0, 'ErrornumberAxis2': 2304}
            # slewing bit useful as it indicates whether or not telescope has arrived at waiting position
            self.slewing_bit = self._tel_status['Status'] & 0b100
            self.RA_rad = (self._tel_status['RigthAscension'] / 180) * pi
            self.DE_rad = (self._tel_status['Declination'] / 180) * pi
            print(f"RA: {self.RA_rad:.4f}, DE: {self.DE_rad:.4f}")

            # Ask the telescope for its tel_status as JSON
            json_string = self._telescope.CommandString("getSatStatus", True)
            self._sat_status = json.loads(json_string) # Parse JSON into a Python dict
            # will be dict with structure:
            # {'status': 0, # bit 0: tracking info (works!), bit 1: sunlight (only for cpf or tle tracks, not eph)
            # 'TrackErrAx1': -0.00045685676708373535, # mrad
            # 'TrackErrAx2': -0.0057915890411264215} # mrad
            self.tracking_bit = self._sat_status['status'] & 0b1
            return None
        except Exception as e:
            return f"Status Request failed:\n{str(e)}"




