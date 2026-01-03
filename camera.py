import json
import time
import os
import datetime as dt
import numpy as np
import zwoasi as asi
import astropy.io.fits as fits
import win32com.client

from utils.configManager import ASI6200CAM_CFG

class CameraWrapper():
    def __init__(self):
        self.connected_flag = False
        self.filterWheel = None
        self.camera = None
        self.imageHeight = None
        self.imageWidth = None
        self.bitDepth = 8
        self.exposureTimeDelayMs = 0
        self.gain = 0
        self.binning = 1
        self.cameraProperty = None

    def connectFilterWheel(self):
        try:
            self.filterWheel = win32com.client.Dispatch("ASCOM.EFW2.FilterWheel")
            self.filterWheel.Connected = True
            print('Connected to filter wheel')
        except Exception as e:
            return f'Filter wheel connect failed: {str(e)}'

    def disconnectFilterWheel(self):
        try:
            self.filterWheel.Connected = False
            print('Disconnected from filter wheel')
        except Exception as e:
            return f'Filter wheel disconnect failed: {str(e)}'

    def _changeFilterPosition(self, filter_position):
        """ Change the current filter of the connected filterwheel, positions start from 1 to 7

        :param filter_position: int of target filter (1-7)
        :return: 0 if successful, 1 if not
        """
        try:
            assert filter_position in [1, 2, 3, 4, 5, 6]
        except AssertionError:
            raise ValueError("Given filter not in range 1-7!")

        try:
            self.filterWheel.Position = filter_position - 1
            while self.filterWheel.Position == -1:
                time.sleep(0.2)
        except Exception as e:
            raise Exception(f'Filter wheel position change failed: {str(e)}')

    def connectCamera(self):
        try:
            libraryFilePath = os.getenv('ZWO_ASI_LIB', os.path.join("lib", "ASICamera2.dll"))
            print(libraryFilePath)
            asi.init(libraryFilePath)
        except Exception as e:
            return f'Environment variable has wrong SDK library path or has not been set: {str(e)}'

        try:
            numberOfCameras = asi.get_num_cameras()
            if numberOfCameras == 0:
                print(f'No cameras found')
                raise
            cameraList = asi.list_cameras()
            if numberOfCameras == 1:
                camera_id = 0
                print(f'Found one camera: {cameraList[0]}')
            else:
                print(f'Found {numberOfCameras} cameras:')
                for n in range(numberOfCameras):
                    print(f'    {n}: {cameraList[n]}')
                camera_id = 0
                print(f'Using #{camera_id}: {cameraList[camera_id]}')
            self.camera = asi.Camera(camera_id)
        except Exception as e:
            self.connected_flag = False
            return f'No cameras found or failed to connect to camera: {str(e)}'

        try:
            self._updateCameraSettings()
        except Exception as e:
            return f"There was en error while configuring the camera:\n{str(e)}"
        self.connected_flag = True

    def disconnectCamera(self):
        try:
            self.camera.set_control_value(asi.ASI_COOLER_ON, False)
            self.camera.set_control_value(asi.ASI_FAN_ON, False)
            self.camera.close()
            print(f'Disconnected from Camera')
            self.connected_flag = False
        except Exception as e:
            return f'Camera disconnect failed: {str(e)}'

    def _updateCameraSettings(self):
        with open(ASI6200CAM_CFG, "r") as f:
            camera_settings = json.load(f)

        self.cameraProperty = self.camera.get_camera_property()

        self.gain = camera_settings['gain']['gain']
        self.camera.set_control_value(asi.ASI_GAIN, self.gain)
        print(f"Setting gain to : {self.gain}")
        maxBandwidth = self.camera.get_controls()['BandWidth']['MaxValue']
        minBandwidth = self.camera.get_controls()['BandWidth']['MinValue']
        chosenBandwidth = camera_settings['exposure']['usbBandwidth']
        if (chosenBandwidth > maxBandwidth) or (chosenBandwidth < minBandwidth):
            print(
                f'Bandwidth out of bounds, needs to be lower than {maxBandwidth} and higher than {minBandwidth}')
            chosenBandwidth = maxBandwidth
        self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, chosenBandwidth)
        # ANTI DEW HEATER = 21
        self.camera.set_control_value(21, camera_settings['cooling']['antiDew'])

        highSpeed = camera_settings['binning']['highSpeed']
        self.camera.set_control_value(asi.ASI_HIGH_SPEED_MODE, highSpeed)

        coolerOn = camera_settings['cooling']['cooling']
        self.camera.set_control_value(asi.ASI_COOLER_ON, coolerOn)
        if coolerOn:
            self.camera.set_control_value(asi.ASI_TARGET_TEMP, camera_settings['cooling']['cmosTemperature'])
        self.camera.set_control_value(asi.ASI_FAN_ON, camera_settings['cooling']['fan'])
        self.binning = camera_settings['binning']['binX']
        self.binMode = camera_settings['binning']['mode']
        bitDepth = camera_settings['gain']['bitDepth']
        # HW binning and 16 bit is possibly supported
        # if binMode=="HW" and bitDepth== 16:
        #    print("Hardware binning and 16-bit image is not supported, changing to 8-bit")
        #    bitDepth = 8
        if self.binMode == "SW" and self.binning <= 4:
            self.camera.set_control_value(asi.ASI_HARDWARE_BIN, 0)
            self.camera.set_control_value(asi.ASI_MONO_BIN, 1)
            self.exposureTimeDelayMs = camera_settings['delay']['swBinInMsMiddleReadoutLineBeginOfFrame']
        elif self.binning > 4:
            print(f'{self.binning}x{self.binning} binning is not supported, setting to 3!')
            self.binning = 3
            self.exposureTimeDelayMs = camera_settings['delay']['swBinInMsMiddleReadoutLineBeginOfFrame']
        elif self.binMode == "HW" and self.binning <= 3:
            self.camera.set_control_value(asi.ASI_HARDWARE_BIN, 1)
            self.camera.set_control_value(asi.ASI_MONO_BIN, 0)
            if self.binning <= 2:
                self.exposureTimeDelayMs = camera_settings['delay']['swBinInMsMiddleReadoutLineBeginOfFrame']
            elif self.binning == 3:
                self.exposureTimeDelayMs = camera_settings['delay']['hwBin3InMsMiddleReadoutLineBeginOfFrame']
        else:
            raise ValueError(f"Binning settings not supported!")


        cameraInfo = self.camera.get_camera_property()
        if camera_settings['ROI']['fullFrame']:
            maxWidth = cameraInfo['MaxWidth']
            maxHeight = cameraInfo['MaxHeight']
            newHeight = maxHeight / self.binning
            newHeight = int(newHeight - (newHeight % 2))
            newWidth = maxWidth / self.binning
            newWidth = int(newWidth - (newWidth % 8))
            startPosX = 0
            startPosY = 0
            if bitDepth == 16:
                self.camera.set_roi(startPosX, startPosY, newWidth, newHeight, self.binning, asi.ASI_IMG_RAW16)
            elif bitDepth == 8:
                self.camera.set_roi(startPosX, startPosY, newWidth, newHeight, self.binning, asi.ASI_IMG_RAW8)
        else:
            newWidth = camera_settings['ROI']['numX']
            newHeight = camera_settings['ROI']['numY']
            startPosX = camera_settings['ROI']['startX']
            startPosY = camera_settings['ROI']['startY']
            if bitDepth == 16:
                self.camera.set_roi(startPosX, startPosY, newWidth, newHeight, self.binning, asi.ASI_IMG_RAW16)
            elif bitDepth == 8:
                self.camera.set_roi(startPosX, startPosY, newWidth, newHeight, self.binning, asi.ASI_IMG_RAW8)
        self.camera_roi = self.camera.get_roi()
        self.imageWidth = self.camera_roi[2]
        self.imageHeight = self.camera_roi[3]
        self.startPosX = self.camera_roi[0]
        self.startPosY = self.camera_roi[1]
        self.bitDepth = bitDepth
        if self.filterWheel is not None:
            self._changeFilterPosition(1)
        else:
            raise Exception("Filter wheel not connected, can't change filter position")


    def setImageDimensions(self, width, height, binning, bit_depth):
        """
        Changes the image dimensions of the camera to centred width x height
        :param width: Target width in binned pixels
        :param height: Target height in binned pixels
        :param binning: Binning mode (1,2,3,4)
        :param bit_depth: Image type (8-bit, 16-bit)
        :return:
        """
        if bit_depth == 8:
            self.camera.set_roi(width=width, height=height, bins=binning, image_type=asi.ASI_IMG_RAW8)
            self.imageWidth = width
            self.imageHeight = height
            self.binning = binning
            self.bitDepth = 8
        elif bit_depth == 16:
            self.camera.set_roi(width=width, height=height, bins=binning, image_type=asi.ASI_IMG_RAW16)
            self.imageWidth = width
            self.imageHeight = height
            self.binning = binning
            self.bitDepth = 16
        else:
            print("Unrecognized bit depth!")

    def takeSingleImage(self, telescope, exposureTimeMs, filePath, img_number):
        try:
            try:
                # Force any single exposure to be halted
                self.camera.stop_video_capture()
                self.camera.stop_exposure()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass

            self.camera.set_control_value(asi.ASI_EXPOSURE, int(exposureTimeMs * 1000))
            currentDate = dt.datetime.now(dt.timezone.utc)
            currentDate = currentDate + dt.timedelta(milliseconds=self.exposureTimeDelayMs)
            self.camera.start_exposure(is_dark=False)
            time.sleep(self.exposureTimeDelayMs / 1000)

            # get telescope data for current image
            # refractionAutoslew = float(
            #     (self.ascomInterface.telescope.Action("telescope:reportrefraction", "")).replace(',', '.'))
            # pointing_correction = self.ascomInterface.telescope.CommandString("GetCorrections", True)
            azimuth, altitude = telescope.AZ_deg, telescope.EL_deg
            tel_status = telescope.get_tel_status()
            rightAscension, declination = tel_status['RigthAscension'], tel_status['Declination']
            timestamp_jd = tel_status['JulianDate']
            JD_UNIX_EPOCH = 2440587.5
            seconds_since_epoch = (timestamp_jd - JD_UNIX_EPOCH) * 86400
            utc_time = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=seconds_since_epoch)
            timestamp_utc = utc_time.isoformat()

            # # TODO: find out what the ASCOM Altitude actually is (+refrac+pointing, +refrac, just encoder)
            # enc_alt = altitude - math.degrees(float(pointing_correction.split('#')[1]))
            # enc_az = azimuth - math.degrees(float(pointing_correction.split('#')[0]))

            while self.camera.get_exposure_status() == asi.ASI_EXP_WORKING:
                time.sleep(0.01)
            imgBuffer = self.camera.get_data_after_exposure()

            if self.bitDepth == 8:
                nda = np.frombuffer(imgBuffer, dtype=np.uint8).reshape((self.imageHeight, self.imageWidth))
                nda = nda.astype(
                    np.uint16 * 257)  # Scale 8-bit to 16-bit, because some FITS viewers don't support 8-bit images
            elif self.bitDepth == 16:
                nda = np.frombuffer(imgBuffer, dtype=np.uint16).reshape((self.imageHeight, self.imageWidth))
            hdr = fits.Header()
            date_obs = currentDate.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            hdr['DATE-OBS'] = (date_obs, "Timestamp of observation in UTC")
            hdr['DATEDATA'] = (timestamp_utc, "Timestamp of position data request in UTC")
            # hdr['REFRACT'] = (refractionAutoslew, "ASA refraction value in arcsec")
            # hdr['CORRECT'] = (pointing_correction, "AltAz pointing correction of current model in radians")
            hdr['EXPTIME'] = (exposureTimeMs, "Exposure time in milliseconds")
            hdr['GAIN'] = (self.gain, "Set gain")
            hdr['OFFSET'] = (self.camera.get_control_value(asi.ASI_OFFSET)[0], "Set pixel offset i.e. brightness")
            hdr['EXTEND'] = (True, "File may contain extensions")
            # hdr['FOCALLEN'] = (5480, "Focal length of telescope")
            # hdr['IMAGETYP'] = ("Light Frame", "Image frame type")
            hdr['NAXIS'] = 2
            hdr['NAXIS1'] = (self.imageWidth, "Image width / X-axis")
            hdr['NAXIS2'] = (self.imageHeight, "Image height / Y-axis")
            hdr['STRTPOSX'] = (self.startPosX, "Starting position / X-axis")
            hdr['STRTPOSY'] = (self.startPosY, "Starting position / Y-axis")
            # hdr['ENCALT'] = (enc_alt, "Encoder altitude value in deg")
            # hdr['ENCAZ'] = (enc_az, "Encoder azimuth value in deg")
            hdr['ALT'] = (altitude, "Altitude in deg")
            hdr['AZ'] = (azimuth, "Azimuth in deg")
            hdr['RA'] = (rightAscension, "Right ascension topocentric value in deg")
            hdr['DEC'] = (declination, "Declination topocentric value in deg")
            # if self.camera.get_control_value(asi.ASI_HIGH_SPEED_MODE)[0]:
            #     hdr['READOUTM'] = ("High Speed", "Readout mode")
            # else:
            #     hdr['READOUTM'] = ("Default", "Readout mode")
            hdr['SIMPLE'] = True
            # hdr['SITELAT'] = (self.ascomInterface.latitude, 'Latitude of station in deg')
            # hdr['SITELON'] = (self.ascomInterface.longitude, 'Longitude of station in deg')
            # hdr['SITEELEV'] = (self.ascomInterface.elevation, 'Elevation of station in meters above ellipsoid')
            hdr['XBINNING'] = (self.binning, 'Binning level in X axis')
            # hdr['XORGSUBF'] = (self.startPosX, 'Starting position of subframe in X axis')
            # hdr['XPIXSZ'] = (self.cameraProperty['PixelSize'] * self.binning, 'Pixel size in um in X axis')
            hdr['YBINNING'] = (self.binning, 'Binning level in Y axis')
            # hdr['YORGSUBF'] = (self.startPosY, 'Starting position of subframe in Y axis')
            # hdr['YPIXSZ'] = (self.cameraProperty['PixelSize'] * self.binning, 'Pixel size in um in Y axis')
            hdr['XSCALE'] = (hdr['XPIXSZ'] / 1000 / 5480 * 180 / np.pi * 3600, 'Pixel scale in arcsec/pixel in X axis')
            hdr['YSCALE'] = (hdr['YPIXSZ'] / 1000 / 5480 * 180 / np.pi * 3600, 'Pixel scale in arcsec/pixel in Y axis')
            if self.camera.get_control_value(asi.ASI_HARDWARE_BIN)[0]:
                hdr['BIN-TYPE'] = ("HW", 'Type of binning (hardware/software)')
            elif self.camera.get_control_value(asi.ASI_MONO_BIN)[0]:
                hdr['BIN-TYPE'] = ("SW", 'Type of binning (hardware/software)')

            if self.filterWheel is not None:
                # Filter position in ASCOM goes from 0 to 6
                hdr['FILTPOS'] = (int(self.filterWheel.Position) + 1, 'Current filter position')
            else:
                hdr['FILTPOS'] = 'no-connection'

            hdu = fits.PrimaryHDU(nda, header=hdr)

            # if imgDataType == np.uint8:
            #     hdr['BITPIX'] = (16, "8-bit scaled up")
            # elif imgDataType == np.uint16:
            #     hdr['BITPIX'] = (16, "Native 16-bit")
            # hdr['BSCALE'] = (1, "Pixel scaling factor")
            # hdr['BZERO'] = (32768, "Pixel offset factor")

            img_number_padded = str(img_number).zfill(3)
            fileName = img_number_padded + "-Alt" + str(round(altitude)) + "-Az" + str(round(azimuth))

            img_file = os.path.join(filePath, fileName, ".fits")
            hdu.writeto(img_file, overwrite=True)

            # return img_file

        except Exception as e:
            print(f'Exposure failed, settings incorrect or camera failed: {str(e)}')
            raise