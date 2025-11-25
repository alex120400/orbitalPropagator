from alpaca.telescope import Telescope
import json

class TelescopeWrapper():
    def __init__(self):
        self.telescope = None

    def connect_telescope(self):
        try:
            self.telescope = Telescope('localhost:11111', 0)
            self.telescope.Connected = True
            print('Connected to Telescope')
        except Exception as e:
            print(f'Telescope connect failed: {str(e)}')

    def disconnect_telescope(self):
        try:
            self.telescope.Connected = False
            print('Disconnected from Telescope')
        except Exception as e:
            print(f'Telescope disconnect failed: {str(e)}')

    def start_track(self, eph_filepath):
        # Read all lines from the file
        with open(eph_filepath, "r") as file:
            lines = [line.rstrip('\n') for line in file]  # Strip newlines if needed

        # Serialize the list of lines to JSON
        lines_list_serialized = json.dumps(lines)

        # Send the serialized data to the telescope
        self.telescope.Action("sat:ephlines", lines_list_serialized)

        # provide telescope with min elevation (=altitude) and start track
        minAltitude = 30
        self.telescope.Action("sat:startalt", minAltitude)
        self.telescope.Action("sat:start", "")


if __name__ == "__main__":
    import os
    tel = TelescopeWrapper()

    tel.connect_telescope()

    tel.start_track(os.path.join("ephemerides", "2025Nov25__13_10_00", "ASATrackingData_STARLINK-1306.eph"))
