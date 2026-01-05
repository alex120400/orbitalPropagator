import numpy as np
import matplotlib.pyplot as plt

def compare_tracking_to_ephemeris(tracking_csv_list, eph_base_file, tracking_label_list, eph_label="Base Eph"):
    """
    :param tracking_csv_list: List of paths to CSV files with tracking data (MJD;Az;Alt)
    :type tracking_csv_list: List[str]

    :param eph_base_file: Path to ephemeris file (.eph) containing MJD, AZI, ELE
    :type eph_base_file: str

    :param tracking_label_list: List of label for measured tracking data
    :type tracking_label_list: List[str]

    :param eph_label: Label for ephemeris data
    :type eph_label: str
    """

    csv_data_list = []
    # ---------- Load tracking data ----------
    for file_path in tracking_csv_list:
        tracking_data = np.loadtxt(file_path, delimiter=";", skiprows=1)
        mjd_track, az_track, alt_track = tracking_data.T

        csv_data_list.append((mjd_track, az_track, alt_track))

    # ---------- Load ephemeris data ----------
    eph_data = np.loadtxt(eph_base_file)
    mjd_eph = eph_data[:, 0]
    az_eph = eph_data[:, 5]
    alt_eph = eph_data[:, 6]

    # ---------- Plot data ----------
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 6), sharex=True)
    fig.suptitle("Track measurements based on eph and tle compared against base ephemeris")
    az_ax, alt_ax = axes
    for data, label in zip(csv_data_list, tracking_label_list):
        mjd_track, az_track, alt_track = data
        az_ax.plot(mjd_track, az_track, label=label)
        alt_ax.plot(mjd_track, alt_track, label=label)
    for ax, eph, y_label in zip([az_ax, alt_ax], [az_eph, alt_eph], ["Azimuth [deg]", "Altitude [deg]"]):
        ax.plot(mjd_eph, eph, "--", label=eph_label)
        ax.set_ylabel(y_label)
        ax.legend()
        ax.grid(True, alpha=0.3)
    alt_ax.set_xlabel("Epoch [mjd]")
    plt.tight_layout()
    plt.show()

def delay_ephemeris(eph_file, output_file, delay_minutes=10):
    """
    :param eph_file: Path to the original ephemeris file (.eph)
    :type eph_file: str

    :param output_file: Path to save the delayed ephemeris file
    :type output_file: str

    :param delay_minutes: Delay to add to each epoch in minutes
    :type delay_minutes: float
    """

    # Convert minutes to days
    delay_days = delay_minutes / (24 * 60)

    with open(eph_file, "r") as fin, open(output_file, "w") as fout:
        for line in fin:
            stripped = line.strip()
            if stripped.startswith("#") or len(stripped) == 0:
                # Keep comments and empty lines unchanged
                fout.write(line)
            else:
                # Split numeric columns, add delay to first column (MJD)
                parts = line.split()
                mjd = float(parts[0])

                mjd_delayed = mjd + delay_days
                # Reformat line: first column delayed, rest unchanged
                new_line = f"{mjd_delayed:14.8f}" + line[14:]
                fout.write(new_line)

def reverse_delay_csv(csv_file, output_file, delay_minutes=10):
    """
    :param csv_file: Path to CSV file containing tracking data (JD;Az;Alt)
    :type csv_file: str

    :param output_file: Path to write the corrected tracking CSV
    :type output_file: str

    :param delay_minutes: Delay to remove from each epoch in minutes
    :type delay_minutes: float

    """

    # Convert minutes to days
    delay_days = delay_minutes / (24.0 * 60.0)

    # Load CSV (skip header)
    data = np.loadtxt(csv_file, delimiter=";", skiprows=1)

    mjd, az, alt = data.T

    # Reverse the delay
    mjd_corrected = mjd - delay_days

    # Write corrected file
    with open(csv_file, "r") as fin:
        header = fin.readline().strip()

    corrected_data = np.column_stack((mjd_corrected, az, alt))

    np.savetxt(
        output_file,
        corrected_data,
        delimiter=";",
        header=header,
        comments="",
    )


if __name__ == "__main__":
    eph_base_file = "ASATrackingData_RIGIDSPHERE-2-(LCS-4).eph"
    delayed_eph_file = "ASATrackingData_RIGIDSPHERE-2-(LCS-4)_delayed.eph"

    # add delay of 17 h and 20 minutes to epochs in eph_base_file, run only once
    delay_ephemeris(eph_base_file, delayed_eph_file, 17*60 + 20)

    tle_track_file = "trackingReport_RIGIDSPHERE-2-(LCS-4).csv"
    #eph_track_file_delayed = "trackingReport_COSMOS-1506_delayed.csv"
    #eph_track_file_delay_reversed = "trackingReport_COSMOS-1506_delay_reversed.csv"
    ff_observation_track_w_lc_file = "FFGroundObservations_RIGIDSPHERE-2-(LCS-4)_with_light_corrections_converted.csv"
    ff_observation_track_wo_lc_file = "FFGroundObservations_RIGIDSPHERE-2-(LCS-4)_without_light_corrections_converted.csv"

    # remove delay of 10 minutes from epochs in measured csv track file, run only once
    # reverse_delay_csv(eph_track_file_delayed, eph_track_file_delay_reversed, 10)

    # compare_tracking_to_ephemeris(
    #     [tle_track_file, ff_observation_track_w_lc_file, ff_observation_track_wo_lc_file],
    #     eph_base_file,
    #     ["TLE based track", "ff obs w lc", "ff obs wo lc"]
    # )