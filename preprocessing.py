import os
from datetime import timedelta, timezone

import numpy as np
import requests
import json
from skyfield.api import load as sky_load
from skyfield.api import wgs84 as sky_wgs84
import skyfield.api as sky
from skyfield.iokit import parse_tle_file as sky_parse_tle_file

from utils.configManager import STATION_CFG, SPACE_TRACK_CFG, LEO_TLE_FILE, TLE_DATA_PATH, OGS_TLE_FILE

minimum_elevation = 26 # deg, minimum elevation for a spacecraft to be visible


def load_StationLatLongAlt() -> (float, float, float):
    """ returns the latitude, longitude and altitude of ground station provided via json

    :returns: latitude, longitude in degree, altitude in meters
    :rtype: Tuple(float, float, float)
    """
    try:
        with open(STATION_CFG) as f:
            station_information = json.load(f)
        latitude = station_information["location"]["latitude"]
        longitude = station_information["location"]["longitude"]
        altitude = station_information["location"]["altitude"]
        # elevation = station_information["location"]["altitude"]
        return latitude, longitude, altitude
    except Exception as e:
        print(f'JSON file f{STATION_CFG} can not be loaded: {str(e)}')
        return 0, 0

def update_LEO_TLE_data() -> bool:
    """ updates LEO TLE data from space-track.org

    :return: flag indicating success
    :rtype: bool
    """
    uriBase = "https://www.space-track.org"
    requestLogin = "/ajaxauth/login"

    with open(SPACE_TRACK_CFG) as f:
        space_track_data = json.load(f)
        space_track_user = space_track_data["credentials"]["username"]
        space_track_pswd = space_track_data["credentials"]["password"]
        recent_LEO_query = space_track_data["queries"]["most_recent_LEO_query"]
    try:
        with requests.Session() as session:
            # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
            siteCred = {'identity': space_track_user, 'password': space_track_pswd}
            resp = session.post(uriBase + requestLogin, data=siteCred)
            if resp.status_code != 200:
                print("Space Track failed on login")
                return False

            resp = session.get(recent_LEO_query)
            if resp.status_code != 200:
                print("failed to download TLE data")
                return False
            else:
                with open(LEO_TLE_FILE, "w") as file:
                    file.write(resp.text)
                    return True
    except Exception as e:
        print(f"Error occurred while updating LEO TLEs:\n{str(e)}")
        return False

def update_ogs_TLE_data() -> bool:
    """ updates TLE data used in SW at OGS ground station

    :return: flag indicating success
    :rtype: bool
    """
    try:
        file_path = os.path.join(TLE_DATA_PATH, "ogs_tle", "tle_sources.txt")
        with open(file_path, "r") as file:
            for line in file.readlines():
                url, group = line.split("#")
                url = url.strip()
                group = group.strip()
                output_file = os.path.join(TLE_DATA_PATH, "ogs_tle", group+".tle")
                sky_load.download(url, output_file)
        return True
    except Exception as e:
        print(f"Error occurred while updating OGS TLEs:\n{str(e)}")
        return False

def get_TLE_data_aga(ogs_flag:bool=False) -> int:
    """ returns the age of TLE data in rounded days

    :param ogs_flag: indicates whether to check ogs or leo source
    :type ogs_flag: bool

    :return: age of tle source in rounded days
    :rtype: int
    """

    if ogs_flag:
        return round(sky_load.days_old(OGS_TLE_FILE))
    else:
        return round(sky_load.days_old(LEO_TLE_FILE))

def create_satellite_data_list(startTime:sky.Time, durationMin:int, ogs_flag:bool=False) -> (list, dict):
    """ creates a list with satellite data and a dictionary mapping the satellite ID to its TLE data

    :param startTime: skyfield Time object marking the beginning of observation time
    :type startTime: skyfield.api.Time

    :param durationMin: duration of watch window in minutes
    :type durationMin: int

    :param ogs_flag: flag indicating which source to use
    :type ogs_flag: bool

    :returns: Tuple with list of satellite-data and a satellite-dict mapping ID -> TLE data
                satellite-data is a tuple with
                    0: name
                    1: NoradID
                    2: rise-time-delta to starting point in decimal minutes with resolution of seconds
                    3: time visible in minutes with second resolution
                    4: percentage of flight time in sunlight
                    5: distance to earth surface in km
                    6: maximum elevation in degree
                satellite-dict:
                    keys: satellite NoradID's
                    item: Tuple with line0, line1, line2 as strings
    :rtype: tuple
    """
    ts = sky_load.timescale()

    satellites_dict = dict()
    satellite_data_list = list()
    if ogs_flag:
        satellites = []
        for ogs_tle_file in os.listdir(os.path.join(TLE_DATA_PATH, "ogs_tle")):
            if ogs_tle_file.endswith(".tle"):
                with sky_load.open(os.path.join(TLE_DATA_PATH, "ogs_tle", ogs_tle_file)) as f:
                    satellites += list(sky_parse_tle_file(f, ts))
                with open(os.path.join(TLE_DATA_PATH, "ogs_tle", ogs_tle_file)) as f:
                    # modified for format received by celes-track (ogs data)
                    line0, line1, line2 = "", "", ""
                    idx = 0
                    for line in f.readlines():
                        if line.startswith("1"):
                            line1 = line.strip().strip("\n")
                            idx += 1
                        elif line.startswith("2"):
                            line2 = line.strip().strip("\n")
                            idx += 1
                        else:
                            line0 = line.strip().strip("\n")
                            if not line0.startswith("0"):
                                line0 = "0 " + line0
                            idx += 1

                        if idx == 3:
                            idx = 0
                            satellites_dict[line1[2:8]] = (line0+"\n", line1+"\n", line2+"\n")
    else:
        with sky_load.open(LEO_TLE_FILE) as f:
            satellites = list(sky_parse_tle_file(f, ts))
        with open(LEO_TLE_FILE) as f:
            # modified for format received by Space-track (LEO data)
            line0, line1, line2 = "", "", ""
            idx = 0
            for line in f.readlines():
                if line.startswith("0"):
                    line0 = line.strip().strip("\n")
                    if not line0.startswith("0"):
                        line0 = "0 " + line0
                    idx += 1
                elif line.startswith("1"):
                    line1 = line.strip().strip("\n")
                    idx += 1
                elif line.startswith("2"):
                    line2 = line.strip().strip("\n")
                    idx += 1
                else:
                    continue
                if idx == 3:
                    idx = 0
                    satellites_dict[line1[2:8]] = (line0+"\n", line1+"\n", line2+"\n")

    print('Loaded', len(satellites), 'satellites')

    gnd_lat, gnd_long, gnd_alt = load_StationLatLongAlt()
    gnd_station = sky_wgs84.latlon(gnd_lat, gnd_long, gnd_alt)

    # define time at which a satellite position shall be available

    t0 = startTime
    t1 = ts.utc(startTime.utc.year, startTime.utc.month, startTime.utc.day,
                         startTime.utc.hour + durationMin // 60,
                         startTime.utc.minute + durationMin % 60
                         )

    for sat in satellites:
        name = sat.name
        # intDes = sat.intldesg
        noradID = sat.model.satnum_str + sat.model.classification
        height = (sat.model.a - 1) * sat.model.radiusearthkm # a is given in earth_radii

        t, events = sat.find_events(gnd_station, t0, t1, altitude_degrees=minimum_elevation) #
        # events[i] = 0 — Satellite rose above altitude_degrees.
        # events[i] = 1 — Satellite culminated and started to descend again.
        # events[i] = 2 — Satellite fell below altitude_degrees.
        rise_time_delta, set_time_delta = None, None
        maximum_elevation = 0
        for time_stamp, event in zip(t, events):
            if event == 0 and rise_time_delta is None:
                rise_time_delta = (time_stamp.utc.hour*60 + time_stamp.utc.minute + time_stamp.utc.second/60) \
                                  - (startTime.utc.hour*60 + startTime.utc.minute)
            elif event == 1:
                elevation = (sat-gnd_station).at(time_stamp).altaz()[0].degrees
                if elevation > maximum_elevation:
                    maximum_elevation = elevation
            elif event == 2 and set_time_delta is None and rise_time_delta is not None:
                set_time_delta = (time_stamp.utc.hour*60 + time_stamp.utc.minute + time_stamp.utc.second/60) \
                                  - (startTime.utc.hour*60 + startTime.utc.minute)
                flight_duration = set_time_delta - rise_time_delta
        if set_time_delta is None or flight_duration < 1:
            # ignore flights that do not set or are not even visible for just a minute
            continue

        # if set_time_delta is not None: # satellite does set in given window -> calculate time in sunlight
        # minute resolution sucks -> change to 5 second resolution
        time_points = int(flight_duration*60/5)
        watch_times = ts.from_datetimes([startTime.utc_datetime().replace(tzinfo=timezone.utc)
                                        + timedelta(minutes=rise_time_delta) # accepts partial minutes
                                        + timedelta(seconds=step*5)
                                        for step in range(time_points)
        ])

        eph = sky_load('de421.bsp')
        sunlit = sat.at(watch_times).is_sunlit(eph) # returns array of [False, False, True, ..., False]
        sunlit_percentage = np.array(sunlit, dtype=bool).sum() / len(sunlit) * 100

        # finally fill all data into list
        #if rise_time_delta is not None and set_time_delta is not None:
        satellite_data_list.append((name, noradID, f"{rise_time_delta:.2f} min", f"{flight_duration:.2f} min",
                                    f"{sunlit_percentage:.2f} %", f"{height:.2f} km",
                                    f"{maximum_elevation:.2f} °" if maximum_elevation != 0 else "----"
                                    ))

    return satellite_data_list, satellites_dict


if __name__ == "__main__":
    ts = sky_load.timescale() # needed many times

    use_ogs_tle_flag = True # set tle source
    if use_ogs_tle_flag:
        print(f"OGS sources are {sky_load.days_old(OGS_TLE_FILE)} days old")
    else:
        print(f"LEO sources are {sky_load.days_old(LEO_TLE_FILE)} days old")

    sat_data_list, sat_dict = create_satellite_data_list(ts.now(), durationMin=90, ogs_flag=True)
    print(sat_dict)

    # create satellite objects from most recent TLE data
    if use_ogs_tle_flag:
        satellites = []
        for ogs_tle_file in os.listdir(os.path.join(TLE_DATA_PATH, "ogs_tle")):
            if ogs_tle_file.endswith(".tle"):
                with sky_load.open(os.path.join(TLE_DATA_PATH, "ogs_tle", ogs_tle_file)) as f:
                    satellites += list(sky_parse_tle_file(f, ts))
        satellites = np.array(satellites)
    else:
        with sky_load.open(LEO_TLE_FILE) as f:
            satellites = np.array(list(sky_parse_tle_file(f, ts)))

    print('Loaded', len(satellites), 'satellites')


    # create observer station as object
    stat_lat, stat_long, stat_alt = load_StationLatLongAlt()
    station = sky_wgs84.latlon(stat_lat, stat_long, stat_alt)

    # define time at which a satellite shall be available
    # Define one-hour range with 15s step
    duration = 90*60  # seconds
    step = 15  # seconds
    num_steps = duration // step

    start_time = ts.now()  # for testing, should be provided by user via GUI later on
    times = ts.utc(
        [start_time.utc.year] * num_steps,
        [start_time.utc.month] * num_steps,
        [start_time.utc.day] * num_steps,
        [start_time.utc.hour] * num_steps,
        [start_time.utc.minute] * num_steps,
        [start_time.utc.second + i * step for i in range(num_steps)]
    )

    rise_time_ar = np.ones(len(satellites)) * -1 # -1 as value if satellite does not rise within time window

    for idx, satellite in enumerate(satellites):
        vect_diff = satellite - station
        topocentric = vect_diff.at(times)
        alt, az, distance = topocentric.altaz()

        args = np.argwhere(alt.degrees > minimum_elevation)
        if len(args) > 0:
            rise_time_ar[idx] = args.flatten()[0] * 0.25





    print("hihi")





