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

    # ---------- Load tracking data ----------
    csv_data_list = []
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

    # Store line pairs per label
    line_map = {}
    # plot tracking curves
    for (mjd, az, alt), label in zip(csv_data_list, tracking_label_list):
        az_line, = az_ax.plot(mjd, az, label=label)
        alt_line, = alt_ax.plot(mjd, alt, label=label)
        line_map[label] = (az_line, alt_line)

    for ax, eph, y_label in zip([az_ax, alt_ax], [az_eph, alt_eph], ["Azimuth [deg]", "Altitude [deg]"]):
        ax.plot(mjd_eph, eph, "--", label=eph_label)
        ax.set_ylabel(y_label)
        ax.legend()
        ax.grid(True, alpha=0.3)

    alt_ax.set_xlabel("Epoch [mjd]")

    # ---------- Interactive legend ----------
    leg = az_ax.legend()
    for legline in leg.get_lines():
        legline.set_picker(True)
        legline.set_pickradius(5)

    label_from_legend = {
        legline: text.get_text()
        for legline, text in zip(leg.get_lines(), leg.get_texts())
    }

    def on_pick(event):
        legline = event.artist
        label = label_from_legend[legline]

        if label not in line_map:
            return

        az_line, alt_line = line_map[label]
        visible = not az_line.get_visible()

        az_line.set_visible(visible)
        alt_line.set_visible(visible)

        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("pick_event", on_pick)
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

    # add delay of 16 h and 20 minutes to epochs in eph_base_file, run only once
    # delay_ephemeris(eph_base_file, delayed_eph_file, 16*60 + 20)

    tle_track_file = "trackingReport_RIGIDSPHERE-2-(LCS-4)_tle_based.csv"
    # eph_track_file_delayed = "trackingReport_RIGIDSPHERE-2-(LCS-4)_eph_based_delayed.csv"
    eph_track_file_delay_reversed = "trackingReport_RIGIDSPHERE-2-(LCS-4)_eph_based_delay_reversed.csv"
    ff_observation_track_w_li_c_file = "FFGroundObservations_RIGIDSPHERE-2-(LCS-4)_w_li_c_converted.csv"
    ff_observation_track_w_to_c_file = "FFGroundObservations_RIGIDSPHERE-2-(LCS-4)_w_to_c_converted.csv"
    ff_observation_track_wo_c_file = "FFGroundObservations_RIGIDSPHERE-2-(LCS-4)_wo_corrections_converted.csv"

    # remove delay of 16 h and 20 minutes from epochs in measured csv track file, run only once
    # reverse_delay_csv(eph_track_file_delayed, eph_track_file_delay_reversed, 16*60 + 20)

    compare_tracking_to_ephemeris(
        [tle_track_file, eph_track_file_delay_reversed,
         ff_observation_track_w_li_c_file, ff_observation_track_w_to_c_file,
         ff_observation_track_wo_c_file],
        eph_base_file,
        ["TLE based track", "Eph based track",
                        "ff obs w li c", "ff obs w to c",
                        "ff obs wo corr"]
    )