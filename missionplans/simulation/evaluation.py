import os
import numpy as np
import matplotlib.pyplot as plt

import skyfield.api as sky
from skyfield.api import load as sky_load
from skyfield.iokit import parse_tle_file as sky_parse_tle_file

plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 18,
    "figure.titlesize": 20
})
# ==========================
# USER SETTINGS
# ==========================
TLE_FILE = "TLE_export.tle"
BASE_DIR = os.path.join(".", "pos_error_data_20sOBS_10sSTEP")             # directory containing satellite folders
RMS_WINDOW_HOURS = 3.0     # duration of each RMS window
TOTAL_DURATION_DAYS = 5.0  # total analysis duration

DELIMITER = ";"            # CSV delimiter
TIME_COLUMN = 0
ERROR_COLUMN = 1

# Derived constants
WINDOW_SECONDS = RMS_WINDOW_HOURS * 3600.0
TOTAL_DURATION_SECONDS = TOTAL_DURATION_DAYS * 24.0 * 3600.0

# ==========================
# HELPER FUNCTIONS
# ==========================

def load_csv(filepath):
    """ loads elapsed time and absolute position error from a CSV file

    :param filepath: path to the CSV file
    :type filepath: str

    :return: elapsed time array [s] and absolute position error array [km]
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    data = np.genfromtxt(
        filepath,
        delimiter=DELIMITER,
        skip_header=1
    )

    _time = data[:, TIME_COLUMN]
    _error = data[:, ERROR_COLUMN]

    return _time, _error


def compute_segmented_rms(time_arr:np.ndarray, error_arr:np.ndarray, window_seconds:float, total_duration_seconds:float):
    """ computes RMS position error over contiguous fixed-duration time windows

    Windows overlap at their boundaries and fully cover the total duration.

    :param time_arr: elapsed time values [s]
    :type time_arr: np.ndarray

    :param error_arr: absolute position error values [km]
    :type error_arr: np.ndarray

    :param window_seconds: duration of one RMS window [s]
    :type window_seconds: float

    :param total_duration_seconds: total duration to analyze [s]
    :type total_duration_seconds: float

    :return: RMS window start times and RMS values
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    rms_values = []
    rms_times = []

    num_windows = int(total_duration_seconds // window_seconds)

    for k in range(num_windows):
        t_start = k * window_seconds
        t_end = (k + 1) * window_seconds

        mask = (time_arr >= t_start) & (time_arr <= t_end) # overlapping boarders between windows
        # print(mask.sum()) # check segment length

        segment_errors = error_arr[mask]

        rms = np.sqrt(np.mean(segment_errors ** 2))

        rms_values.append(rms)
        rms_times.append((t_end - window_seconds/2)/3600) # middle hour of segment

    return np.array(rms_times), np.array(rms_values)


# ==========================
# MAIN PROCESSING LOOP
# ==========================

# +1 to compensate for overlapping borders, 5 as we have samples for 2T, 4T, 1d, 2d, 3d, TLE
labels = {"n": "TLE reference", "4T":"4 orbits", "1d":"1 day", "2d":"2 days", "3d":"3 days"}
colors = {"n":"tab:purple", "4T":"tab:red", "1d":"tab:blue", "2d":"tab:orange", "3d":"tab:green"}
mean_rms_array = np.zeros((int(TOTAL_DURATION_SECONDS/ WINDOW_SECONDS), 6))
sat_amount = 0
ts = sky_load.timescale()
with sky_load.open(TLE_FILE) as f:
    satellites = list(sky_parse_tle_file(f, ts))

for satellite_name in sorted(os.listdir(BASE_DIR)):
    sat_amount += 1
    satellite_path = os.path.join(BASE_DIR, satellite_name)
    c = 0
    if not os.path.isdir(satellite_path):
        continue

    print(f"Processing satellite: {satellite_name}")
    for sat in satellites:
        if sat.name == satellite_name:
            range_km = (sat.model.a - 1) * sat.model.radiusearthkm
            T_mins = (2*np.pi)/ sat.model.no_kozai
            print(f"Range = {range_km} km")
            print(f"T = {T_mins} mins")

    plt.figure(figsize=(10, 6))
    for file_name in sorted(os.listdir(satellite_path)):
        if not file_name.endswith(".csv"):
            continue

        file_path = os.path.join(satellite_path, file_name)

        time, error = load_csv(file_path)

        rms_time, rms_error = compute_segmented_rms(time, error, WINDOW_SECONDS, TOTAL_DURATION_SECONDS)
        mean_rms_array[:, c] += rms_error
        kind, _, _, _, ID, sc_name = file_name.replace(".csv", "").split("_")
        c += 1
        lw = 1.5
        if ID == "n":
            _TLE_c_idx = c - 1
            lw = 2
        elif ID == "2T":
            _2T_c_idx = c - 1
            continue
        elif ID == "4T":
            _4T_c_idx = c - 1
            #continue
        elif ID == "1d":
            _1d_c_idx = c - 1
        elif ID == "2d":
            _2d_c_idx = c - 1
        elif ID == "3d":
            _3d_c_idx = c - 1
        else:
            raise FileExistsError(f"there is an ID marker that's not recognized: {ID}")

        plt.plot(rms_time,
                 rms_error,
                 marker = "o",
                 linewidth=lw,
                 label=labels[ID],
                 color=colors[ID])


    plt.xlabel("Elapsed time [hours]")
    plt.ylabel("RMS position error [km]")
    if T_mins > 60:
        plt.title(f"RMS Position Error for {sc_name}" +
                  f"\nWindow = {RMS_WINDOW_HOURS} h, Total = {TOTAL_DURATION_DAYS} d" +
                  f"\nHeight = {np.round(range_km):.0f} km, T = {T_mins // 60:.0f} h {np.round(T_mins % 60):.0f} min"
        )
    else:
        plt.title(f"RMS Position Error for {sc_name}" +
                  f"\nWindow = {RMS_WINDOW_HOURS} h, Total = {TOTAL_DURATION_DAYS} d" +
                  f"\nHeight = {np.round(range_km):.0f} km, T = {np.round(T_mins):.0f} min"
                  )
    plt.grid(True)
    plt.legend()
    plt.xlim(0, TOTAL_DURATION_DAYS * 24.0)
    plt.tight_layout()
    plt.savefig(f"RMS_pos_error_{sc_name}.pdf")
    plt.savefig(f"RMS_pos_error_{sc_name}.png")
    plt.show()

mean_rms_array = mean_rms_array / sat_amount

plt.figure(figsize=(10, 6))
plt.plot(rms_time, mean_rms_array[:, _TLE_c_idx], marker='o', linewidth=2,
                 label=labels["n"], color=colors["n"])
# plt.plot(rms_time, mean_rms_array[:, _2T_c_idx], marker='o', label="2 orbits")
plt.plot(rms_time, mean_rms_array[:, _4T_c_idx], marker='o', linewidth=1.5,
                 label=labels["4T"], color=colors["4T"])
plt.plot(rms_time, mean_rms_array[:, _1d_c_idx], marker='o', linewidth=1.5,
                 label=labels["1d"], color=colors["1d"])
plt.plot(rms_time, mean_rms_array[:, _2d_c_idx], marker='o', linewidth=1.5,
                 label=labels["2d"], color=colors["2d"])
plt.plot(rms_time, mean_rms_array[:, _3d_c_idx], marker='o', linewidth=1.5,
                 label=labels["3d"], color=colors["3d"])

plt.title(f"Mean RMS Position Error over all satellites" )
plt.xlabel("Elapsed time [hours]")
plt.ylabel("Mean RMS position error [km]")
plt.grid(True)
plt.legend()
plt.xlim(0, TOTAL_DURATION_DAYS * 24.0)
plt.tight_layout()
plt.savefig("mean_RMS_pos_error.pdf")
plt.savefig("mean_RMS_pos_error.png")
plt.show()
