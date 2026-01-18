import os
from datetime import datetime
from astropy.io import fits
import shutil


def fractional_day_from_datetime(dt):
    """ returns fractional day from a datetime object

    :param dt: datetime object (UTC)
    :type dt: datetime.datetime

    :return: fractional day
    :rtype: float
    """

    seconds_in_day = (
        dt.hour * 3600 +
        dt.minute * 60 +
        dt.second +
        dt.microsecond / 1e6
    )
    return seconds_in_day / 86400.0


def rename_fits_by_fractional_day(src_folder_path, dst_folder_path):
    """ renames FITS files using fractional day from DATE-OBS header

    :param src_folder_path: path to folder containing FITS files
    :type src_folder_path: str

    :param dst_folder_path: path to folder where renamed FITS files will be stored
    :type dst_folder_path: str
    """

    for filename in os.listdir(src_folder_path):

        if not filename.lower().endswith(".fits"):
            continue

        file_path = os.path.join(src_folder_path, filename)

        try:
            with fits.open(file_path) as hdul:
                header = hdul[0].header
                date_obs = header["DATE-OBS"]

            # Parse DATE-OBS (ISO 8601)
            dt = datetime.fromisoformat(date_obs)

            frac_day = fractional_day_from_datetime(dt)
            frac_day_8dec_int = int(frac_day * 1e8)
            # name was xxx-Alt26-Az223.fits, keep only xxx
            cont_file_number = filename[0:3]
            new_name = cont_file_number + "-FracOfDay"+ f"{frac_day_8dec_int}.fits"
            new_path = os.path.join(dst_folder_path, new_name)

            # Overwrite if necessary
            shutil.copy2(file_path, new_path)

            print(f"{filename}  ->  {new_name}")

        except Exception as e:
            print(f"Skipping {filename}: {e}")


if __name__ == "__main__":
    SRC_FOLDER = r"SDA_1675_AltAz"
    DST_FOLDER = r"SDA_1675_FracOfDay"
    rename_fits_by_fractional_day(SRC_FOLDER, DST_FOLDER)
