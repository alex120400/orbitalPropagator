import os
import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 18,
    "figure.titlesize": 20
})

def load_along_track_file(file_path):
    """ loads along-track separation file

    :param file_path: path to AlongTrackSeparation file
    :type file_path: str

    :return: elapsed time [days], TLE separation [km], OD separation [km]
    :rtype: tuple[np.ndarray, np.ndarray, np.ndarray]
    """
    data = np.genfromtxt(
        file_path,
        encoding="utf-16",  # <-- CRITICAL
        skip_header=2,
        dtype=float
    )

    time = data[:, 0]
    tle_sep = data[:, 1]
    od_sep = data[:, 3]

    return time, tle_sep, od_sep


# ---- configuration ----
base_dir = ".\\5d_simulation_10sSteps"
suffixes = ["4T", "1d", "2d", "3d"]
labels = {"4T":"4 orbits", "1d":"1 day", "2d":"2 days", "3d":"3 days"}
colors = {"4T":"tab:red", "1d":"tab:blue", "2d":"tab:orange", "3d":"tab:green"}

files = [
    # os.path.join(base_dir, f"AlongTrackSeparation_STELLA{suffix}.txt")
    os.path.join(base_dir, f"CrossTrackSeparation_STELLA{suffix}.txt")
    for suffix in suffixes
]

# ---- load reference (TLE) from first file ----
time, tle_sep, _ = load_along_track_file(files[0])

# ---- load all OD curves ----
od_curves = {}

for suffix, file_path in zip(suffixes, files):
    _, _, od_sep = load_along_track_file(file_path)
    od_curves[suffix] = od_sep


# ---- plotting ----
fig, ax = plt.subplots(figsize=(10, 6))

# TLE reference
ax.plot(
    time,
    tle_sep,
    color="tab:purple",
    linewidth=2,
    label="TLE reference"
)

# OD curves
for suffix, od_sep in od_curves.items():
    ax.plot(
        time,
        od_sep,
        linewidth=1.5,
        label=labels[suffix],
        color=colors[suffix]
    )

ax.set_xlabel("Elapsed Time [days]")
ax.set_ylabel("Along-Track Separation [km]")
ax.set_ylabel("Cross-Track Separation [km]")
# ax.set_title("Along-Track Separation: TLE vs OD\nDifferent observation periods")
# ax.set_title("Cross-Track Separation: TLE vs OD\nDifferent observation periods")
ax.grid(True, linestyle="--", alpha=0.6)
ax.legend()

plt.tight_layout()
# plt.savefig("AlongTrack_Stella.png")
# plt.savefig("AlongTrack_Stella.pdf")
plt.savefig("CrossTrack_Stella.png")
plt.savefig("CrossTrack_Stella.pdf")
plt.show()

