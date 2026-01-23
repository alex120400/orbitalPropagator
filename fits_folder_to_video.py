import os
import cv2
import numpy as np
from astropy.io import fits


def stretch_fits_image(image):
    """
    Apply background subtraction + asinh stretch to a FITS image.
    Returns an 8-bit uint image suitable for video writing.
    """

    # Remove singleton dimensions
    image = np.squeeze(image)

    if image.ndim != 2:
        raise ValueError(f"Expected 2D image, got {image.shape}")

    # Crop last 8 columns (as in your original code)
    if image.shape[1] > 8:
        image = image[:, :-2*8]

    # --- Background subtraction ---
    background = np.median(image)
    x = image - background
    x[x < 0] = 0

    # --- Stretch limits ---
    vmax = np.percentile(x, 99.9)

    if vmax <= 0:
        return np.zeros_like(x, dtype=np.uint8)

    # --- Normalize ---
    x = np.clip(x, 0, vmax)
    x = x / vmax

    # --- Strong asinh stretch ---
    a = 30
    x = np.arcsinh(a * x) / np.arcsinh(a)

    return (x * 255).astype(np.uint8)


def draw_center_cross(img_bgr, size=40, thickness=3):
    """
    Draw a red cross at the center of a BGR image.
    """

    h, w = img_bgr.shape[:2]
    cx, cy = w // 2, h // 2
    red = (0, 0, 255)

    cv2.line(
        img_bgr,
        (cx - size, cy),
        (cx + size, cy),
        red,
        thickness
    )
    cv2.line(
        img_bgr,
        (cx, cy - size),
        (cx, cy + size),
        red,
        thickness
    )


def fits_folder_to_video(
    fits_dir,
    output_video,
    fps=10,
    cross_size=20,
    cross_thickness=2
):
    """
    Create a video from a folder of FITS files using astro-friendly stretching
    and draw a center cross on every frame.
    """

    fits_files = sorted(
        f for f in os.listdir(fits_dir)
        if f.lower().endswith(".fits")
    )

    if not fits_files:
        raise ValueError("No FITS files found in folder.")

    video_writer = None

    for i, fname in enumerate(fits_files):
        path = os.path.join(fits_dir, fname)

        # --- Load FITS ---
        with fits.open(path) as hdul:
            image = hdul[0].data

        # --- Stretch image ---
        stretched = stretch_fits_image(image)

        # Convert grayscale → BGR
        frame = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)

        # --- Draw center cross ---
        draw_center_cross(
            frame,
            size=cross_size,
            thickness=cross_thickness
        )

        # --- Initialize video writer ---
        if video_writer is None:
            h, w = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(
                output_video,
                fourcc,
                fps,
                (w, h)
            )

        video_writer.write(frame)
        print(f"Added frame {i + 1}/{len(fits_files)}: {fname}")

    video_writer.release()
    print(f"\nVideo written to: {output_video}")


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    fits_folder_to_video(
        fits_dir=r"tracking/2026Jan20__16_00__120/4/HYB_KITSAT-3",
        output_video="output.mp4",
        fps=15,
        cross_size=40,
        cross_thickness=3
    )
