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

    if smart_grey_scale:
        vmin, vmax = np.percentile(image_np, (1, 99))
        plt.imshow(image_np, cmap="gray" , vmin=vmin, vmax=vmax)
    else:
        plt.imshow(image_np, cmap="gray")

    plt.colorbar()
    plt.show()


def detect_satellite(fits_path, visualize_flag=False, debug_flag=False):
    # ---- Load FITS image ----
    image_np = fits.getdata(fits_path).astype(np.float32)

    # Normalize to 8-bit for OpenCV
    image_np -= np.min(image_np)
    image_np /= np.max(image_np)
    image_np = (image_np * 255).astype(np.uint8)

    height, width = image_np.shape
    centerX = width // 2
    centerY = height // 2

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
        return None, None, None

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
            center = (int(x), int(y))
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
    best_candidate = satellite_candidates[best_sat_idx]
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

if __name__ == "__main__":
    fits_folder = "tracking\\2026Jan04__17_07__90\\RIGIDSPHERE-2-(LCS-4)"

    scan_entire_fits_folder(fits_folder)







