from alpaca.telescope import Telescope
import json
import numpy as np
from numpy import pi

from skyfield.api import load as sky_load
from skyfield.api import wgs84 as sky_wgs84

from utils.configManager import MIN_ALTITUDE_ElEVATION
from preprocessing import load_StationLatLongAlt

class TelescopeWrapper():
    def __init__(self):
        self._telescope = None
        self.connected_flag = False
        self.tracking_flag = None
        self._tel_status = None
        self._sat_status = None
        self.AZ_deg = None
        self._AZ_deg_list = []
        self.EL_deg = None
        self._EL_deg_list = []
        self.mjd = None
        self._mjd_list = []
        self.tracking_bit = 0
        self.slewing_bit = 0

        self._ts = sky_load.timescale()
        self._gnd_station = sky_wgs84.latlon(*load_StationLatLongAlt())

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

    def start_track(self, eph_tle_filepath, tle_only_flag=False):
        # check if tracking is not ongoing
        if self.tracking_flag:
            return "Track is ongoing! Cannot start a new one!"
        # Read all lines from the file
        with open(eph_tle_filepath, "r") as file:
            lines = [line.rstrip('\n') for line in file]  # Strip newlines if needed

        try:
            if tle_only_flag:
                # send TLE data to telescope
                self._telescope.Action("sat:name", lines[0][2:]) # ignore '0 ' at beginning
                self._telescope.Action("sat:line1", lines[1]) # TLE Line 1
                self._telescope.Action("sat:line2", lines[2]) # TLE Line 2
            else:
                # Serialize the list of lines to JSON
                lines_list_serialized = json.dumps(lines)
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
            # slewing-bit useful as it indicates whether telescope has arrived at waiting position or not
            self.slewing_bit = (self._tel_status['Status'] >> 2) # bit 2 is relevant
            RA_deg, DE_deg = self._tel_status['RigthAscension'], self._tel_status['Declination']
            jd = self._tel_status['JulianDate']
            self.mjd = jd - 2400000.5 # might need adjustments
            self.AZ_deg, self.EL_deg = self._topo_radec_to_azel(RA_deg, DE_deg, jd)



            # Ask the telescope for its sat_status as JSON
            json_string = self._telescope.CommandString("getSatStatus", True)
            self._sat_status = json.loads(json_string) # Parse JSON into a Python dict
            # will be dict with structure:
            # {'status': 0, # bit 0: tracking info (works!), bit 1: sunlight (only for cpf or tle tracks, not eph)
            # 'TrackErrAx1': -0.00045685676708373535, # mrad
            # 'TrackErrAx2': -0.0057915890411264215} # mrad
            self.tracking_bit = self._sat_status['status'] & 0b1

            if self.tracking_bit:
                # append data to lists if tracking bit is on
                self._mjd_list.append(self.mjd)
                self._AZ_deg_list.append(self.AZ_deg)
                self._EL_deg_list.append(self.EL_deg)
            return None
        except Exception as e:
            return f"Status Request failed:\n{str(e)}"

    def get_tel_status(self):
        return self._tel_status

    def save_tracking_data(self, full_file_path):
        data = np.column_stack((self._mjd_list, self._AZ_deg_list, self._EL_deg_list))
        np.savetxt(full_file_path, data, delimiter=";", header="Epoch (mjd);Azimuth (deg),Elevation (deg)")
        # reset data for next measurements
        self._mjd_list = []
        self._EL_deg_list = []
        self._AZ_deg_list = []


    def _topo_radec_to_azel(self, ra_deg, dec_deg, jd):
        """ Convert topocentric RA/Dec in degrees to Azimuth and Elevation in degrees.

        :param ra_deg: Right Ascension in degrees (topocentric)
        :type ra_deg: float
        :param dec_deg: Declination in degrees (topocentric)
        :type dec_deg: float
        :param jd: Julian Date (TT or UTC, converted to TT internally)
        :type jd: float

        :returns: az_deg, el_deg: Azimuth and Elevation in degrees
        """
        # Convert RA/Dec to radians
        ra = np.radians(ra_deg)
        dec = np.radians(dec_deg)
        lat = np.radians(self._gnd_station.latitude.degrees)

        # Time as Terrestrial Time (TT)
        t = self._ts.tt_jd(jd)  # Terrestrial Time

        # Local Apparent Sidereal Time (LAST) in hours
        lst_hours = self._gnd_station.lst_hours_at(t)
        lst_rad = np.radians(lst_hours * 15.0)  # convert hours → degrees (=> *360/24) → radians

        # Hour Angle
        ha = lst_rad - ra

        # Elevation
        sin_alt = np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha)
        alt = np.arcsin(sin_alt)

        # Azimuth
        cos_az = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
        az = np.arccos(np.clip(cos_az, -1.0, 1.0))

        # Correct quadrant: if sin(HA) > 0, az = 360° - az
        az = np.where(np.sin(ha) > 0, 2 * np.pi - az, az)

        # Convert to degrees
        az_deg = np.degrees(az)
        el_deg = np.degrees(alt)

        return az_deg, el_deg




