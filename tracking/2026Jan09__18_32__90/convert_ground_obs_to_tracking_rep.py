import numpy as np
from astropy import time

# copy file to any location, insert file names here
groundstation_observation_input_file = "FFGroundObservations_STARLINK-1364_wo_corr.txt"
tracking_report_output_file = "FFGroundObservations_STARLINK-1364_wo_corr_converted.csv"


def convert_GO_to_TR(ground_obs_txt_file, tracking_rep_csv_file):
    # Load azi, alt and epoch data
    data = np.loadtxt(ground_obs_txt_file, usecols=(2, 3, 4))
    az, alt, mjd_tai_ff = data.T
    # az and alt are in rad -> convert to degree
    az = np.rad2deg(az)
    alt = np.rad2deg(alt)
    # epoch is TAI in Modified Julian format, freeflyer uses 1941 as reference instead of 1858 (asa)
    # -> add 29999.5 to compensate years and subtract leap seconds
    mjd_tai_asa = mjd_tai_ff + 29999.5
    mjd_tai_asa = time.Time(mjd_tai_asa, format='mjd', scale='tai')
    mjd_utc_asa = mjd_tai_asa.utc.mjd

    converted_data = np.column_stack((mjd_utc_asa, az, alt))

    np.savetxt(
        tracking_rep_csv_file,
        converted_data,
        delimiter=";",
        header="Epoch (mjd);Azimuth (deg),Elevation (deg)",
        comments="",
    )

if __name__ == '__main__':
    convert_GO_to_TR(groundstation_observation_input_file, tracking_report_output_file)





