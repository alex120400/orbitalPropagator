# This script contains functions to
# -) show fits files and their headers
# -) process fits files to calculate the centroid and center-distance of the satellite within the image
# -) convert pixel offsets to altitude and azimuth offsets
import numpy as np
import os
from astropy.io import fits
import matplotlib.pyplot as plt
import cv2


def show_fits_image_and_header(fits_file, smart_grey_scale=True):
    with fits.open(fits_file) as hdul:
        header = hdul[0].header
        image_np = hdul[0].data

    for key in header.keys():
        print(f"{key}:\t{header[key]}")

    image_np = image_np[:, :-8]

    if smart_grey_scale:
        vmin, vmax = np.percentile(image_np, (1, 99))
        plt.imshow(image_np, cmap="gray" , vmin=vmin, vmax=vmax)
    else:
        plt.imshow(image_np, cmap="gray")

    plt.colorbar()
    plt.show()


def detect_satellite(fits_path, visualize_flag=False, debug_flag=False, hw_bin_err_flag=True):
    # ---- Load FITS image ----
    image_np = fits.getdata(fits_path).astype(np.float32)
    err_bits = 8 # bit-size of white bar on the right
    if hw_bin_err_flag:
        image_np = image_np[:, :-2*err_bits] # need to remove twice the bar to keep center of image correct

    # Normalize to 8-bit for OpenCV
    image_np -= np.min(image_np)
    image_np /= np.max(image_np)
    image_np = (image_np * 255).astype(np.uint8)

    height, width = image_np.shape
    centerX = width / 2
    centerY = height / 2
    #print(f"im-center-X: {centerX}, im-center-Y: {centerY}")

    # ---- Preprocessing ----
    smooth_frame = cv2.GaussianBlur(image_np, (5, 5), 0)

    _, binary = cv2.threshold(smooth_frame, 63, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary,
        cv2.RETR_EXTERNAL, # only get outer contours of an object
        cv2.CHAIN_APPROX_SIMPLE # reduce stored points in contour
    )

    output_image = cv2.cvtColor(smooth_frame, cv2.COLOR_GRAY2BGR)

    satellite_candidates = []
    satellite_m00s = []
    satellite_centroids = []
    satellite_distances = []

    # ---- Satellite candidate detection ----
    if len(contours) == 0:
        if debug_flag:
            print("Did not find any contours!")
        return None, None, None

    circularity = -1
    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)

        if x is None or y is None:
            continue
        else:
            d = np.sqrt((x - centerX) ** 2 + (y - centerY) ** 2)

        M = cv2.moments(contour)
        sat_area = M['m00']
        if not (sat_area > 0):
            continue
        else:
            centroid = (M['m10'] / sat_area, M['m01'] / sat_area)  # x_bar, y_bar

        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        if perimeter == 0:
            continue
        else:
            circularity = 4 * np.pi * area / (perimeter ** 2)

        if 0.6 <= circularity <= 1.4: # good check if object is close to circular object
            center = (x, y)
            radius = radius
            satellite_candidates.append((center, radius))
            satellite_m00s.append(sat_area)
            satellite_centroids.append(centroid)
            satellite_distances.append(d)


    if debug_flag:
        print("Debugging")
        print(f"circularity: {circularity}")
        cv2.namedWindow("Input Image", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Input Image", 1000, 800)
        cv2.imshow("Input Image", image_np)
        cv2.waitKey(0)
        # cv2.namedWindow("Smoothed Image", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("Smoothed Image", 1000, 800)
        # cv2.imshow("Smoothed Image", smooth_frame)
        # cv2.waitKey(0)
        cv2.namedWindow("Binary Image", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Binary Image", 1000, 800)
        cv2.imshow("Binary Image", binary)
        cv2.waitKey(0)
        cv2.namedWindow("Detected Contours", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Detected Contours", 1000, 800)
        cv2.drawContours(output_image, contours, -1, (0, 255, 0), 3)  # show all found contours
        cv2.imshow("Detected Contours", output_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if not satellite_candidates:
        return None, None, None

    # ---- Select satellite with the highest ratio of brightness/size to distance ----
    satellite_m00s = np.array(satellite_m00s)
    satellite_distances = np.array(satellite_distances)
    satellite_scores = satellite_m00s / satellite_distances
    best_sat_idx = np.argmax(satellite_scores)

    best_centroid = satellite_centroids[best_sat_idx]
    #print(f"centroid-X: {best_centroid[0]}, centroid-y: {best_centroid[1]}")
    best_candidate = satellite_candidates[best_sat_idx]
    #print(f"enclosure-center-X: {best_candidate[0][0]}, enclosure-center-Y: {best_candidate[0][1]}")
    best_distance = satellite_distances[best_sat_idx]


    # ---- Visualization ----
    if visualize_flag:
        print(f"Satellites data: m00={satellite_m00s[best_sat_idx]}, d={satellite_distances[best_sat_idx]}")
        cv2.namedWindow("Detected Star", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Detected Star", 1000, 800)
        cv2.circle(output_image, best_candidate[0], int(best_candidate[1]), (0, 255, 0), 3)
        cv2.imshow("Detected Star", output_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return best_distance, best_candidate, best_centroid


def scan_entire_fits_folder(fits_folder_path):
    with os.scandir(fits_folder_path) as entries:
        i = 0
        missed_satellites_cnt = 0
        missed_satellites_idx = []
        d_array = []
        for entry in entries:
            # if (i % 20) == 0:
            #     v_flag = True
            # else:
            #     v_flag = False
            # if i > 333:
            #     v_flag = True
            #     debug_flag = True
            # else:
            #     v_flag = False
            #     debug_flag = False
            if entry.is_file() and entry.path.endswith(".fits"):
                v_flag = False
                debug_flag = False
                i += 1
                # fits_file_name = "001-Alt35-Az286.fits"
                fits_path = entry.path

                # fits_path = os.path.join(fits_folder, fits_file_name)
                # show_fits_image_and_header(fits_path)

                d, sat_center_radius, sat_centroid = detect_satellite(fits_path, v_flag, debug_flag)
                if d is not None:
                    print(f"result for image {i} is:")
                    print(f"distance to center (based on sat_center): {d}")
                    print(f"sat-center and radius: {sat_center_radius[0]}, {sat_center_radius[1]}")
                    print(f"sat centroid: {sat_centroid}")
                    d_array.append(d)
                else:
                    missed_satellites_cnt += 1
                    missed_satellites_idx.append(i)
                    detect_satellite(fits_path, True, True)

        d_array = np.array(d_array)
        d_average = np.average(d_array)
        d_min_idx = np.argmin(d_array)
        d_min = d_array[d_min_idx]
        d_max_idx = np.argmax(d_array)
        d_max = d_array[d_max_idx]

        print(f"{missed_satellites_cnt} frames of {i} did not show a definite satellite")
        print(f"Those frames are {missed_satellites_idx}.")
        print(f"{i- missed_satellites_cnt} satellites were found")
        print(f"The average distance to the center is: {d_average}")
        print(f"The distance range is: {d_min} <= d <= {d_max}")
        print(f"These ranges have been found in frame {d_min_idx+1} (min) and {d_max_idx+1} (max)")

        bin_width = 1  # pixels
        bins = np.arange(0, d_max + bin_width, bin_width)
        plt.hist(d_array, bins)
        plt.xlabel("Distance from image center [pixels]")
        plt.ylabel("Number of satellites")
        plt.title("Satellite distance distribution")
        plt.grid(True, alpha=0.3)
        plt.show()


def camera_to_altaz_projection(u, v, fx=0.424574272713/3600, fy=0.424574272713/3600, cx=3192/2, cy=2129/2, R=-64.7390513577836):
    """
    :param u: horizontal Pixel coordinate
    :type u: float

    :param v: vertical Pixel coordinates
    :type v: float

    :param fx: Conversion pixel -> degree (or focal scale) in x
    :type fx: float

    :param fy: Conversion pixel -> degree (or focal scale) in y
    :type fy: float

    :param cx: Image horizontal center coordinate
    :type cx: float

    :param cy: Image vertical center coordinate
    :type cy: float

    :param R : Rotation angle in degrees
    :type R: float

    :return: alt-, az- value of centroid to image center offset
    :rtype: Tuple
    """

    # Pixel vector (homogeneous coordinates)
    pixel_vector = np.array([u, v, 1.0])

    # Intrinsic camera matrix
    intrinsic_matrix = np.array([
        [1.0 / fx, 0.0,        cx],
        [0.0,       1.0 / fy,  cy],
        [0.0,       0.0,       1.0]
    ])

    # Inverse intrinsic matrix
    inv_intrinsic = np.linalg.inv(intrinsic_matrix)

    # Project pixel into camera coordinates
    projected_pixel_vector = inv_intrinsic @ pixel_vector

    # Camera rotation matrix (about optical axis)
    R_rad = np.deg2rad(R)
    camera_rotation = np.array([
        [np.cos(R_rad), -np.sin(R_rad), 0.0],
        [np.sin(R_rad),  np.cos(R_rad), 0.0],
        [0.0,            0.0,           1.0]
    ])

    # Inverse camera rotation
    inv_camera_rotation = np.linalg.inv(camera_rotation)

    # Final 3D direction vector
    xyz = inv_camera_rotation @ projected_pixel_vector

    # Output mapping (same sign convention as MATLAB)
    az = -xyz[0]   # NORTH: ABOVE PIXEL CENTER => ALTITUDE +
    alt = -xyz[1]  # WEST: LEFT OF PIXEL CENTER => AZIMUTH +

    return alt, az


def get_abs_arcsec_offset_from_single_image(fits_image_path, hw_bin_err_flag=True):
    _, _, centroid = detect_satellite(fits_image_path, hw_bin_err_flag=hw_bin_err_flag)
    if centroid is None:
        return None
    dx, dy = centroid
    image_np = fits.getdata(fits_image_path).astype(np.float32)
    err_bits = 8  # bit-size of white bar on the right
    if hw_bin_err_flag:
        image_np = image_np[:, :-2 * err_bits]  # need to remove twice the bar to keep center of image correct

    im_height, im_width = image_np.shape
    cX = im_width / 2
    cY = im_height / 2

    d_alt, d_az = camera_to_altaz_projection(dx, dy, cx=cX, cy=cY)

    d_abs_deg = np.sqrt(d_az**2+d_alt**2)
    d_abs_arcsec = d_abs_deg*3600
    # print(f"offset [arcsec]: {d_abs_arcsec}")
    return d_abs_arcsec


def get_abs_arcsec_offset_from_folder_for_HybridTracks(fits_folder_path, split_frac_of_day, ASC_TYPE, hw_bin_err_flag=True):
    safety_span = int((3 / (3600 * 24)) * 1e8) # 3 seconds in both directions of the split epoch will be ignored
    TLE_offsets = list()
    OD_offsets = list()

    with os.scandir(fits_folder_path) as entries:
        for entry in list(entries)[1:-1]: # exclude first and last image, usually buggy
            if entry.is_file() and entry.path.endswith(".fits"):
                fits_path, fits_name = os.path.split(entry.path)
                arcsec_offset = get_abs_arcsec_offset_from_single_image(entry.path, hw_bin_err_flag)
                if arcsec_offset is None:
                    print(f"Could not process image {fits_name}")
                    detect_satellite(entry.path, hw_bin_err_flag=hw_bin_err_flag, debug_flag=True)
                    continue

                fits_path, fits_name = os.path.split(entry.path)
                frac_of_the_day_str = fits_name[-13:-5] # get last 8 characters, which are frac of the day
                cont_numb = fits_name[0:3]
                try:
                    frac_of_the_day_int = int(frac_of_the_day_str)
                except ValueError:
                    print(f"Could not convert {frac_of_the_day_str} to int")
                    continue
                if frac_of_the_day_int < (split_frac_of_day - safety_span):
                    if ASC_TYPE == "TLE":
                        # print(f"TLE exported: {cont_numb}")
                        TLE_offsets.append(arcsec_offset)
                    else:
                        OD_offsets.append(arcsec_offset)
                elif frac_of_the_day_int > (split_frac_of_day + safety_span):
                    if ASC_TYPE == "TLE":
                        OD_offsets.append(arcsec_offset)
                        #print(f"OD exported: {cont_numb}")
                    else:
                        TLE_offsets.append(arcsec_offset)
                else:
                    # in safety region which is excluded
                    #print(f"Skipped: {cont_numb}")
                    continue
    return np.array(TLE_offsets), np.array(OD_offsets)


def load_offsets(folder_path):
    """ loads OD and TLE offset files from a folder

    :param folder_path: path to tracking folder
    :type folder_path: str

    :return: OD offsets, TLE offsets
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    od = np.loadtxt(os.path.join(folder_path, "OD_offsets.txt"), skiprows=1)
    tle = np.loadtxt(os.path.join(folder_path, "TLE_offsets.txt"), skiprows=1)
    return od, tle


if __name__ == "__main__":
    # fits_folder = "tracking\\2026Jan04__17_07__90\\RIGIDSPHERE-2-(LCS-4)"

    # show_fits_image_and_header(fits_folder+"\\001-Alt26-Az143.fits")
    # scan_entire_fits_folder(fits_folder)

    # get_abs_arcsec_offset_from_single_image(fits_folder+"\\002-Alt26-Az143.fits")



    #hybrid_fits_folder = "tracking\\2026Jan04__17_17__90\\SDA_1675_FracOfDay"

    # base_folder = r"tracking\\2026Jan19__15_55__130"
    # hybrid_fits_folder = r"tracking\\2026Jan19__15_55__130\\1\\HYB_COSMOS-2170"
    # args = 72050347.2, "OD"
    # idx = 1
    # hybrid_fits_folder = r"tracking\\2026Jan19__15_55__130\\2\\HYB_ONEWEB-0715"
    # args = 72598958.3, "TLE"
    # idx = 2
    # hybrid_fits_folder = r"tracking\\2026Jan19__15_55__130\\3\\HYB_ONEWEB-0098"
    # args = 73185763.9, "OD"
    # idx = 3
    # hybrid_fits_folder = r"tracking\\2026Jan19__15_55__130\\4\\HYB_DELTA-1-DEB"
    # args =74008680.6, "OD"
    # idx = 4
    # hybrid_fits_folder = r"tracking\\2026Jan19__15_55__130\\5\\HYB_CZ-4-DEB" # only descending images available, very few work
    # args = 74519097.2, "TLE"
    # idx = 5

    # base_folder = r"tracking\\2026Jan20__16_00__120"
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\1\\HYB_COSMOS-2170"
    # args = 67057291.7, "OD"
    # idx = 1
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\2\\HYB_DELTA-1-DEB"
    # args = 68102430.6, "TLE"
    # idx = 2
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\3\\HYB_SL-8-R-B"
    # args = 70831597.2, "OD"
    # idx = 3
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\4\\HYB_KITSAT-3"
    # args = 72046875.0, "TLE"
    # idx=4
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\5\\HYB_ONEWEB-0399"
    # args = 72630208.3, "TLE"
    # idx = 5
    # hybrid_fits_folder = r"tracking\\2026Jan20__16_00__120\\6\\HYB_NOAA-6"
    # args = 74237847.2, "TLE"
    # idx = 6


    # tle_arcsec_offsets, od_arcsec_offsets = get_abs_arcsec_offset_from_folder_for_HybridTracks(hybrid_fits_folder,  *args)
    #
    # np.savetxt(f"{base_folder}\\{idx}\\TLE_offsets.txt",
    #            tle_arcsec_offsets,
    #            header="abs offset [arcsec]"
    #            )
    # np.savetxt(f"{base_folder}\\{idx}\\OD_offsets.txt",
    #            od_arcsec_offsets,
    #            header="abs offset [arcsec]"
    #            )


    # ---- Measurement 1, Monday Jan 19 ----
    # base_dir = "2026Jan19__15_55__130" # has folders 1, 2, 3, 4
    # labels = ["COSMOS-2170\nOD asc\n1409 km\n31° max El.",
    #           "ONEWEB-0715\nTLE asc\n1214 km\n38° max El.",
    #           "ONEWEB-0098\nOD asc\n1214 km\n42° max El.",
    #           "DELTA-1-DEB\nOD asc\n1605 km\n44° max El."]
    # folders = ["1", "2", "3", "4"]

    # ---- Measurement 2, Tuesday Jan 20 ----
    base_dir = "2026Jan20__16_00__120" # has folders 1, 2, 3, 4, 5, 6
    labels = ["COSMOS-2170 (21784)\nOD asc\n1409 km\n67° max El.",
              "DELTA-1-DEB (12217U)\nTLE asc\n809 km\n40° max El.",
              "SL-8 R/B (13034U)\nOD asc\n977 km\n52° max El.",
              "KITSAT 3 (25756U)\nTLE asc\n704 km\n56° max El.",
              "ONEWEB-0399 (50479U)\nTLE asc\n1215 km\n40° max El.",
              "NOAA 6 (11416U)\nTLE asc\n771 km\n77° max El."]
    folders = ["1", "2", "3", "4", "5", "6"]


    # ---- load data ----
    od_data = []
    tle_data = []

    for f in folders:
        od, tle = load_offsets(os.path.join("tracking",base_dir, f))
        od_data.append(od)
        tle_data.append(tle)

    # ---- plotting ----
    fig, ax = plt.subplots(figsize=(12, 6))

    group_centers = np.arange(len(folders)) * 2 + 1
    offset = 0.3

    positions_od = group_centers - offset
    positions_tle = group_centers + offset

    ax.boxplot(
        od_data,
        positions=positions_od,
        widths=0.4,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
        showfliers=False
    )

    ax.boxplot(
        tle_data,
        positions=positions_tle,
        widths=0.4,
        patch_artist=True,
        boxprops=dict(facecolor="orange"),
        showfliers=False
    )

    # ---- axes formatting ----
    ax.set_xticks(group_centers)
    ax.set_xticklabels(labels, rotation=20)

    ax.set_ylabel("Offsets [arcsec]")
    ax.set_xlabel("Tracking Sets")
    ax.set_title("OD vs TLE Tracking Offset Comparison for Measurement folder: " + base_dir)

    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # ---- legend (manual) ----
    ax.plot([], [], color="lightblue", label="OD")
    ax.plot([], [], color="orange", label="TLE")
    ax.legend()

    plt.tight_layout()
    plt.show()




