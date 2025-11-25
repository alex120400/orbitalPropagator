#################################################################################
# FreeFlyer Runtime API                                                         #
# Copyright a.i. solutions, Inc.                                                #
#                                                                               #
# This file is a part of the FreeFlyer Runtime API distribution and you are     #
# free to modify this item or use it in its current form for your own projects. #
#                                                                               #
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES      #
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF              #
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR       #
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES        #
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN         #
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF       #
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.                #
#                                                                               #
#################################################################################
# pylint: disable=C0301
# aisolutions.freeflyer.runtimeapi package

"""
    Contains the primary class for interfacing with a FreeFlyer Runtime API engine.
"""

import ctypes

from ctypes import byref

import threading

from .CInterfaceWrapper import CInterfaceWrapper
from .Utilities import Utilities
from .GetFreeFlyerVersionResult import GetFreeFlyerVersionResult
from .GetMissionPlanDiagnosticsResult import GetMissionPlanDiagnosticsResult
from .ConsoleOutputProcessingMethod import ConsoleOutputProcessingMethod
from .Result import Result
from .GetLocationResult import GetLocationResult
from .GetRuntimeApiVersionResult import GetRuntimeApiVersionResult
from .FFTimeSpan import FFTimeSpan

class RuntimeApiEngine:
    """
        An instance of a FreeFlyer Runtime API engine
    """

    _DllHandleLock = threading.RLock()
    _Initialized = False

    FREEFLYER_RUNTIME_API_CLIENT_VERSION_MAJOR = 3
    """ The major version of the runtime api this client is written against. """

    FREEFLYER_RUNTIME_API_CLIENT_VERSION_MINOR = 0
    """ The minor version of the runtime api this client is written against. """

    def __init__(self, ffInstallPath, consoleOutputProcessingMethod=None, windowedOutputMode=None):

        self._EngineHandle = ctypes.c_void_p()
        self._IsClosed = False
        self.initialize(ffInstallPath, consoleOutputProcessingMethod, windowedOutputMode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroyEngine()

    def initialize(self, ffInstallPath, consoleOutputProcessingMethod=None, windowedOutputMode=None):
        """
            Attempts to create a new Runtime API engine.

            :param ffInstallPath:                 The path to the FreeFlyer installation to use.

            :param consoleOutputProcessingMethod: Determines how console output from the engine will be handled

            :param windowedOutputMode:            Determines how output windows will be handled when running through the
                                                  Runtime API.

            :raises: RuntimeApiException Possible errors include:

                     -   The referenced FreeFlyer installation does not have a valid license.
                     -   The path does not exist or does not point to a FreeFlyer installation
                     -   The referenced FreeFlyer installation does not match the 'bitness' of this host application.
                     -   The referenced FreeFlyer installation is not recent enough.
                     -   The referenced FreeFlyer installation is corrupt.
        """
        with RuntimeApiEngine._DllHandleLock:
            if not RuntimeApiEngine._Initialized:
                CInterfaceWrapper.initialize(ffInstallPath)
                RuntimeApiEngine._Initialized = True

        if consoleOutputProcessingMethod is None:
            consoleOutputProcessingMethod = ConsoleOutputProcessingMethod.RedirectToRuntimeApi

        if windowedOutputMode is None:
            Utilities.checkResult(CInterfaceWrapper.lib.ffCreateEngine(
                ctypes.c_int32(self.FREEFLYER_RUNTIME_API_CLIENT_VERSION_MAJOR),
                ctypes.c_int32(self.FREEFLYER_RUNTIME_API_CLIENT_VERSION_MINOR),
                ctypes.c_int32(consoleOutputProcessingMethod),
                byref(self._EngineHandle)))
        else:
            Utilities.checkResult(CInterfaceWrapper.lib.ffCreateEngineWithOutputWindowSupport(
                ctypes.c_int32(self.FREEFLYER_RUNTIME_API_CLIENT_VERSION_MAJOR),
                ctypes.c_int32(self.FREEFLYER_RUNTIME_API_CLIENT_VERSION_MINOR),
                ctypes.c_int32(consoleOutputProcessingMethod),
                ctypes.c_int32(windowedOutputMode),
                byref(self._EngineHandle)))

    def destroyEngine(self):
        """
            Destroys the engine instance.
        """
        if not self._IsClosed:
            Utilities.checkResult(CInterfaceWrapper.lib.ffDestroyEngine(self._EngineHandle))
            self._IsClosed = True

    def synchronize(self, timeout):
        """
            Blocks until the engine completes all asynchronous operations or the timeout is reached.

            :param timeout: The timeout period in milliseconds.

            :type timeout: int.

            :returns:  GetRuntimeApiVersionResult -- a GetRuntimeApiVersionResult object containing the result of the function.

            :raises: IllegalStateException, RuntimeApiException
        """

        if self._IsClosed:
            raise RuntimeError('A closed engine cannot be used')

        asyncResult = ctypes.c_int32()
        syncResult = CInterfaceWrapper.lib.ffSynchronize(self._EngineHandle, timeout, byref(asyncResult))

        Utilities.checkResult(syncResult)
        Utilities.checkResult(asyncResult.value)

        return Utilities.getResult(syncResult) == Result.Success

    def getRuntimeApiVersion(
            self
    ):
        """
        Attempts to retrieve the Runtime API major and minor versions of the current Runtime
        API instance.


        :returns:       Returns a :class:'GetRuntimeApiVersionResult' object containing the result of the function.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        major = ctypes.c_int32()
        minor = ctypes.c_int32()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetRuntimeApiVersion(
                byref(major)
                ,
                byref(minor)
            )
        )

        result = GetRuntimeApiVersionResult(
            major.value
            ,
            minor.value
        )

        return result

    def getFreeFlyerVersion(
            self
    ):
        """
        Attempts to retrieve the FreeFlyer version being used with this Runtime API instance.


        :returns:       Returns a :class:'GetFreeFlyerVersionResult' object containing the result of the function.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        major = ctypes.c_int32()
        minor = ctypes.c_int32()
        build = ctypes.c_int32()
        revision = ctypes.c_int32()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetFreeFlyerVersion(
                byref(major)
                ,
                byref(minor)
                ,
                byref(build)
                ,
                byref(revision)
            )
        )

        result = GetFreeFlyerVersionResult(
            major.value
            ,
            minor.value
            ,
            build.value
            ,
            revision.value
        )

        return result

    def killEngine(
            self
    ):
        """
        Attempts to kill the specified engine.

        .. note::

            Forces the engine to exit immediately. The state of any data or results produced
            by the engine will be undefined.
            It is preferrable to destroy an engine by waiting until it's idle and then calling
            {aisolutions.freeflyer.runtimeApi.RuntimeApiEngine.__exit__}. This function should
            only be used when a engine has become unresponsive.

        :param engine:      The handle to the FreeFlyer engine instance to kill.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffKillEngine(
                self._EngineHandle
            )
        )

    def isEngineIdle(
            self
    ):
        """
        Attempts to determine if the specified engine is idle.

        .. note::

            An idle engine is defined as currently processing no requests.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           A value indicating whether the engine is idle.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        isIdle = ctypes.c_bool()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffIsEngineIdle(
                self._EngineHandle
                ,
                byref(isIdle)
            )
        )

        return isIdle.value

    def getConsoleOutput(
            self
    ):
        """
        Attempts to retrieve the merged contents of the standard out and standard error
        streams for the specified engine.

        .. note::

            The output buffer will be cleared after this function is called. Therefore, subsequent
            calls will return an empty string until the engine writes more output to either
            the standard out or standard error streams.
            This function does not synchronize the engine.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           The merged contents of the standard out and standard error streams at the time of
                            the call.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        consoleOutput = ctypes.c_char_p()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetConsoleOutput(
                self._EngineHandle
                ,
                byref(consoleOutput)
            )
        )

        return Utilities.nativeToPythonString(consoleOutput)

    def loadMissionPlanFromFile(
            self
            ,
            missionPlanPath
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:              The handle to the target FreeFlyer engine.
        :param missionPlanPath:     The file path of the Mission Plan to load.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                             -   The specified file was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanPath is None:
            raise TypeError("The argument 'missionPlanPath' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromFile(
                self._EngineHandle
                ,
                Utilities.encodeString(missionPlanPath)
            )
        )

    def loadMissionPlanFromFileAsync(
            self
            ,
            missionPlanPath
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:              The handle to the target FreeFlyer engine.
        :param missionPlanPath:     The file path of the Mission Plan to load.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                             -   The specified file was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanPath is None:
            raise TypeError("The argument 'missionPlanPath' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromFileAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(missionPlanPath)
            )
        )

    def loadMissionPlanFromFileDynamicAsync(
            self
            ,
            missionPlanPath
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:              The handle to the target FreeFlyer engine.
        :param missionPlanPath:     The file path of the Mission Plan to load.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                             -   The specified file was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanPath is None:
            raise TypeError("The argument 'missionPlanPath' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromFileDynamicAsync(
                self._EngineHandle
                ,
                missionPlanPath.getNativeData()
            )
        )

    def loadMissionPlanFromString(
            self
            ,
            missionPlanContents
            ,
            initialCurrentDirectory
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param missionPlanContents:         The contents of the Mission Plan to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified string was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanContents is None:
            raise TypeError("The argument 'missionPlanContents' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromString(
                self._EngineHandle
                ,
                Utilities.encodeString(missionPlanContents)
                ,
                Utilities.encodeString(initialCurrentDirectory)
            )
        )

    def loadMissionPlanFromStringAsync(
            self
            ,
            missionPlanContents
            ,
            initialCurrentDirectory
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param missionPlanContents:         The contents of the Mission Plan to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified string was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanContents is None:
            raise TypeError("The argument 'missionPlanContents' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromStringAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(missionPlanContents)
                ,
                Utilities.encodeString(initialCurrentDirectory)
            )
        )

    def loadMissionPlanFromStringDynamicAsync(
            self
            ,
            missionPlanContents
            ,
            initialCurrentDirectory
    ):
        """
        Attempts to load the specified Mission Plan into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param missionPlanContents:         The contents of the Mission Plan to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified string was not a valid Mission Plan.
                             -   A data file specified in the Mission Plan did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The Mission Plan contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if missionPlanContents is None:
            raise TypeError("The argument 'missionPlanContents' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffLoadMissionPlanFromStringDynamicAsync(
                self._EngineHandle
                ,
                missionPlanContents.getNativeData()
                ,
                initialCurrentDirectory.getNativeData()
            )
        )

    def loadFreeFlyerScriptFromFile(
            self
            ,
            freeFlyerScriptPath
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param freeFlyerScriptPath:     The path to the FreeFlyer Script to load.
        :param timeSpanMode:            Determines whether the specified FreeFlyer script will be run in millisecond mode
                                        or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScriptPath is None:
            raise TypeError("The argument 'freeFlyerScriptPath' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFile(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScriptPath)
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFile2(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScriptPath)
                    ,
                    timeSpanMode
                )
            )

    def loadFreeFlyerScriptFromFileAsync(
            self
            ,
            freeFlyerScriptPath
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param freeFlyerScriptPath:     The path to the FreeFlyer Script to load.
        :param timeSpanMode:            Determines whether the specified FreeFlyer script will be run in millisecond mode
                                        or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScriptPath is None:
            raise TypeError("The argument 'freeFlyerScriptPath' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFileAsync(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScriptPath)
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFile2Async(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScriptPath)
                    ,
                    timeSpanMode
                )
            )

    def loadFreeFlyerScriptFromFileDynamicAsync(
            self
            ,
            freeFlyerScriptPath
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param freeFlyerScriptPath:     The path to the FreeFlyer Script to load.
        :param timeSpanMode:            Determines whether the specified FreeFlyer script will be run in millisecond mode
                                        or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToLoadMissionPlan - The specified Mission Plan could not be loaded. Some possible reasons are:

                             -   The specified file did not exist.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScriptPath is None:
            raise TypeError("The argument 'freeFlyerScriptPath' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFileDynamicAsync(
                    self._EngineHandle
                    ,
                    freeFlyerScriptPath.getNativeData()
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromFile2DynamicAsync(
                    self._EngineHandle
                    ,
                    freeFlyerScriptPath.getNativeData()
                    ,
                    timeSpanMode.getNativeData()
                )
            )

    def loadFreeFlyerScriptFromString(
            self
            ,
            freeFlyerScript
            ,
            initialCurrentDirectory
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param freeFlyerScript:             The FreeFlyer Script to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".
        :param timeSpanMode:                Determines whether the specified FreeFlyer script will be run in millisecond mode
                                            or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScript is None:
            raise TypeError("The argument 'freeFlyerScript' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromString(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScript)
                    ,
                    Utilities.encodeString(initialCurrentDirectory)
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromString2(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScript)
                    ,
                    Utilities.encodeString(initialCurrentDirectory)
                    ,
                    timeSpanMode
                )
            )

    def loadFreeFlyerScriptFromStringAsync(
            self
            ,
            freeFlyerScript
            ,
            initialCurrentDirectory
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param freeFlyerScript:             The FreeFlyer Script to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".
        :param timeSpanMode:                Determines whether the specified FreeFlyer script will be run in millisecond mode
                                            or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScript is None:
            raise TypeError("The argument 'freeFlyerScript' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromStringAsync(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScript)
                    ,
                    Utilities.encodeString(initialCurrentDirectory)
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromString2Async(
                    self._EngineHandle
                    ,
                    Utilities.encodeString(freeFlyerScript)
                    ,
                    Utilities.encodeString(initialCurrentDirectory)
                    ,
                    timeSpanMode
                )
            )

    def loadFreeFlyerScriptFromStringDynamicAsync(
            self
            ,
            freeFlyerScript
            ,
            initialCurrentDirectory
            ,
            timeSpanMode=None
    ):
        """
        Attempts to load the specified FreeFlyer Script into the specified engine.

        .. note::

            If another MissionPlan is already loaded, it will be automatically cleaned up.
            When loading a FreeFlyer Script instead of a Mission Plan, the default data files
            that come with the FreeFlyer installation will be used.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param freeFlyerScript:             The FreeFlyer Script to load.
        :param initialCurrentDirectory:     The initial current directory to use when loading and running the Mission Plan.
                                            For example, this would be used to resolve relative paths in an Include statement.
                                            To use the current directory of the host application specify ".".
        :param timeSpanMode:                Determines whether the specified FreeFlyer script will be run in millisecond mode
                                            or nanosecond mode.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorFailedToParseScript - The script of the specified Mission Plan had a syntax error. Some possible reasons are:

                             -   The script contained a syntax error.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if freeFlyerScript is None:
            raise TypeError("The argument 'freeFlyerScript' must not be NoneType.")

        if initialCurrentDirectory is None:
            raise TypeError("The argument 'initialCurrentDirectory' must not be NoneType.")

        overloadIndex = 0

        if timeSpanMode is None:
            overloadIndex = 0
        elif timeSpanMode is not None:
            overloadIndex = 1
        else:
            raise TypeError("NoneType Error! One or more required argument(s) are missing.")


        if overloadIndex == 0:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromStringDynamicAsync(
                    self._EngineHandle
                    ,
                    freeFlyerScript.getNativeData()
                    ,
                    initialCurrentDirectory.getNativeData()
                )
            )
        elif overloadIndex == 1:
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffLoadFreeFlyerScriptFromString2DynamicAsync(
                    self._EngineHandle
                    ,
                    freeFlyerScript.getNativeData()
                    ,
                    initialCurrentDirectory.getNativeData()
                    ,
                    timeSpanMode.getNativeData()
                )
            )

    def setUserInfoArguments(
            self
            ,
            userInfoArguments
    ):
        """
        Attempts to set the user info arguments for the currently loaded Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Loaded state.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param userInfoArguments:       The values to use in the FF_Preference.UserInfo string array.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if userInfoArguments is None:
            raise TypeError("The argument 'userInfoArguments' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetUserInfoArguments(
                self._EngineHandle
                ,
                len(userInfoArguments)
                ,
                Utilities.pythonStringArrayToCStringArray(userInfoArguments)
            )
        )

    def setUserInfoArgumentsAsync(
            self
            ,
            userInfoArguments
    ):
        """
        Attempts to set the user info arguments for the currently loaded Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Loaded state.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param userInfoArguments:       The values to use in the FF_Preference.UserInfo string array.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if userInfoArguments is None:
            raise TypeError("The argument 'userInfoArguments' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetUserInfoArgumentsAsync(
                self._EngineHandle
                ,
                len(userInfoArguments)
                ,
                Utilities.pythonStringArrayToCStringArray(userInfoArguments)
            )
        )

    def setUserInfoArgumentsDynamicAsync(
            self
            ,
            userInfoArguments
    ):
        """
        Attempts to set the user info arguments for the currently loaded Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Loaded state.

        :param engine:                  The handle to the target FreeFlyer engine.
        :param userInfoArguments:       The values to use in the FF_Preference.UserInfo string array.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if userInfoArguments is None:
            raise TypeError("The argument 'userInfoArguments' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetUserInfoArgumentsDynamicAsync(
                self._EngineHandle
                ,
                userInfoArguments.getNativeData()
            )
        )

    def prepareMissionPlan(
            self
    ):
        """
        Attempts to prepare the loaded Mission Plan for execution.

        .. note::

            To call this function successfully, the engine must be in the Loaded state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffPrepareMissionPlan(
                self._EngineHandle
            )
        )

    def prepareMissionPlanAsync(
            self
    ):
        """
        Attempts to prepare the loaded Mission Plan for execution.

        .. note::

            To call this function successfully, the engine must be in the Loaded state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffPrepareMissionPlanAsync(
                self._EngineHandle
            )
        )

    def cleanupMissionPlan(
            self
    ):
        """
        Attempts to clean up the currently executing Mission Plan.

        .. note::

            All resources utilitized by the currently executing Mission Plan will be released.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffCleanupMissionPlan(
                self._EngineHandle
            )
        )

    def cleanupMissionPlanAsync(
            self
    ):
        """
        Attempts to clean up the currently executing Mission Plan.

        .. note::

            All resources utilitized by the currently executing Mission Plan will be released.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffCleanupMissionPlanAsync(
                self._EngineHandle
            )
        )

    def executeStatement(
            self
    ):
        """
        Attempts to execute the statement at the current location in the Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
                  -    ErrorNoStatementsToExecute - An attempt was made to execute the next statement, but no statements were left to execute. Some possible reasons are:

                             -   There are no more statements left in the Mission Plan to execute.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteStatement(
                self._EngineHandle
            )
        )

    def executeStatementAsync(
            self
    ):
        """
        Attempts to execute the statement at the current location in the Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
                  -    ErrorNoStatementsToExecute - An attempt was made to execute the next statement, but no statements were left to execute. Some possible reasons are:

                             -   There are no more statements left in the Mission Plan to execute.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteStatementAsync(
                self._EngineHandle
            )
        )

    def executeRemainingStatements(
            self
    ):
        """
        Attempts to execute all remaining statements in the Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteRemainingStatements(
                self._EngineHandle
            )
        )

    def executeRemainingStatementsAsync(
            self
    ):
        """
        Attempts to execute all remaining statements in the Mission Plan.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:      The handle to the target FreeFlyer engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteRemainingStatementsAsync(
                self._EngineHandle
            )
        )

    def executeUntilApiLabel(
            self
            ,
            labelRegularExpression
    ):
        """
        Attempts to execute statements until the API Label with the specified name is reached.

        .. note::

            If a Label matching the specified regular expression does not exist or is never
            reached, then all remaining statements will be executed until the Mission Plan ends.
            To call this function successfully, the engine must be in the Prepared state.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param labelRegularExpression:      A regular expression to match against an ApiLabel statement. When this label is
                                            matched, execution will stop.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if labelRegularExpression is None:
            raise TypeError("The argument 'labelRegularExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteUntilApiLabel(
                self._EngineHandle
                ,
                Utilities.encodeString(labelRegularExpression)
            )
        )

    def executeUntilApiLabelAsync(
            self
            ,
            labelRegularExpression
    ):
        """
        Attempts to execute statements until the API Label with the specified name is reached.

        .. note::

            If a Label matching the specified regular expression does not exist or is never
            reached, then all remaining statements will be executed until the Mission Plan ends.
            To call this function successfully, the engine must be in the Prepared state.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param labelRegularExpression:      A regular expression to match against an ApiLabel statement. When this label is
                                            matched, execution will stop.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if labelRegularExpression is None:
            raise TypeError("The argument 'labelRegularExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteUntilApiLabelAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(labelRegularExpression)
            )
        )

    def executeUntilApiLabelDynamicAsync(
            self
            ,
            labelRegularExpression
    ):
        """
        Attempts to execute statements until the API Label with the specified name is reached.

        .. note::

            If a Label matching the specified regular expression does not exist or is never
            reached, then all remaining statements will be executed until the Mission Plan ends.
            To call this function successfully, the engine must be in the Prepared state.

        :param engine:                      The handle to the target FreeFlyer engine.
        :param labelRegularExpression:      A regular expression to match against an ApiLabel statement. When this label is
                                            matched, execution will stop.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorFailedToExecuteStatement - An error occurred while attempting to execute the statement.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if labelRegularExpression is None:
            raise TypeError("The argument 'labelRegularExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffExecuteUntilApiLabelDynamicAsync(
                self._EngineHandle
                ,
                labelRegularExpression.getNativeData()
            )
        )

    def isMissionPlanComplete(
            self
    ):
        """
        Attempts to determine if there are any statements left to execute.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           A value indicating whether there are any statements left to execute.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        isComplete = ctypes.c_bool()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffIsMissionPlanComplete(
                self._EngineHandle
                ,
                byref(isComplete)
            )
        )

        return isComplete.value

    def getExecutionNumber(
            self
    ):
        """
        Attempts to retrieve the number of statements that have executed with the currently
        executing Mission Plan.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           The current execution number of the specified engine.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        executionNumber = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExecutionNumber(
                self._EngineHandle
                ,
                byref(executionNumber)
            )
        )

        return executionNumber.value

    def getLocation(
            self
    ):
        """
        Attempts to retrieve the location of the current statement in the currently executing
        Mission Plan.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           Returns a :class:'GetLocationResult' object containing the result of the function.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        source = ctypes.c_char_p()
        line = ctypes.c_size_t()
        statement = ctypes.c_char_p()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetLocation(
                self._EngineHandle
                ,
                byref(source)
                ,
                byref(line)
                ,
                byref(statement)
            )
        )

        result = GetLocationResult(
            Utilities.nativeToPythonString(source)
            ,
            line.value
            ,
            Utilities.nativeToPythonString(statement)
        )

        return result

    def getMissionPlanDiagnostics(
            self
            ,
            diagnosticLevel
    ):
        """
        Attempts to retrieve error and warning messages for the currently executing Mission
        Plan.

        :param engine:              The handle to the target FreeFlyer engine.
        :param diagnosticLevel:     The level of detail to use when generating diagnostic messages.

        :returns:                   Returns a :class:'GetMissionPlanDiagnosticsResult' object containing the result of the function.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        errorsCount = ctypes.c_size_t()
        errors = ctypes.c_char_p()
        warningsCount = ctypes.c_size_t()
        warnings = ctypes.c_char_p()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetMissionPlanDiagnostics(
                self._EngineHandle
                ,
                diagnosticLevel
                ,
                byref(errorsCount)
                ,
                byref(errors)
                ,
                byref(warningsCount)
                ,
                byref(warnings)
            )
        )

        result = GetMissionPlanDiagnosticsResult(
            errorsCount.value
            ,
            Utilities.nativeToPythonString(errors)
            ,
            warningsCount.value
            ,
            Utilities.nativeToPythonString(warnings)
        )

        return result

    def evaluateExpression(
            self
            ,
            expression
    ):
        """
        Attempts to evaluate the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression to evaluate.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffEvaluateExpression(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
            )
        )

    def evaluateExpressionAsync(
            self
            ,
            expression
    ):
        """
        Attempts to evaluate the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression to evaluate.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffEvaluateExpressionAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
            )
        )

    def assignExpression(
            self
            ,
            lhsExpression
            ,
            rhsExpression
    ):
        """
        Attempts to assign the expression specified as the second argument to the expression
        specified as the first argument.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:              The handle to the target FreeFlyer engine.
        :param lhsExpression:       The expression to be assigned.
        :param rhsExpression:       The expression to be evaluated.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not a valid expression.
                             -   The expression specified for the right-hand-side of the assignment is not a valid expression.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not writable.
                             -   The object type used in the left-hand-side of the assignment is not allowed in an assignment.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable. Some possible reasons are:

                             -   The expression specified for the right-hand-side of the assignment it is not readable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The type specified by the right-hand-side expression did not match the type specified by the left-hand-side expression.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression. Some possible reasons are:

                             -   An error occurred when setting the value of the left-hand-side expression.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully. Some possible reasons are:

                             -   An error occurred when evaluating the right-hand-side of the assignment.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if lhsExpression is None:
            raise TypeError("The argument 'lhsExpression' must not be NoneType.")

        if rhsExpression is None:
            raise TypeError("The argument 'rhsExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAssignExpression(
                self._EngineHandle
                ,
                Utilities.encodeString(lhsExpression)
                ,
                Utilities.encodeString(rhsExpression)
            )
        )

    def assignExpressionAsync(
            self
            ,
            lhsExpression
            ,
            rhsExpression
    ):
        """
        Attempts to assign the expression specified as the second argument to the expression
        specified as the first argument.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:              The handle to the target FreeFlyer engine.
        :param lhsExpression:       The expression to be assigned.
        :param rhsExpression:       The expression to be evaluated.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not a valid expression.
                             -   The expression specified for the right-hand-side of the assignment is not a valid expression.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not writable.
                             -   The object type used in the left-hand-side of the assignment is not allowed in an assignment.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable. Some possible reasons are:

                             -   The expression specified for the right-hand-side of the assignment it is not readable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The type specified by the right-hand-side expression did not match the type specified by the left-hand-side expression.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression. Some possible reasons are:

                             -   An error occurred when setting the value of the left-hand-side expression.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully. Some possible reasons are:

                             -   An error occurred when evaluating the right-hand-side of the assignment.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if lhsExpression is None:
            raise TypeError("The argument 'lhsExpression' must not be NoneType.")

        if rhsExpression is None:
            raise TypeError("The argument 'rhsExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAssignExpressionAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(lhsExpression)
                ,
                Utilities.encodeString(rhsExpression)
            )
        )

    def assignExpressionReference(
            self
            ,
            lhsExpression
            ,
            rhsExpression
    ):
        """
        Attempts to assign the object reference of the expression specified as the second
        argument to the expression specified as the first argument.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:              The handle to the target FreeFlyer engine.
        :param lhsExpression:       The expression to be assigned.
        :param rhsExpression:       The expression to be evaluated.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not a valid expression.
                             -   The expression specified for the right-hand-side of the assignment is not a valid expression.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment it is not writeable.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable. Some possible reasons are:

                             -   The expression specified for the right-hand-side does not return an assignable reference.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The type specified by the right-hand-side expression is not compatible with type of the left-hand-side expression.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression. Some possible reasons are:

                             -   The right-hand-side and left-hand-side of the assignment are incompatible.
                             -   An error was thrown in evaluating the expression on the right-hand-side of the assignment.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if lhsExpression is None:
            raise TypeError("The argument 'lhsExpression' must not be NoneType.")

        if rhsExpression is None:
            raise TypeError("The argument 'rhsExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAssignExpressionReference(
                self._EngineHandle
                ,
                Utilities.encodeString(lhsExpression)
                ,
                Utilities.encodeString(rhsExpression)
            )
        )

    def assignExpressionReferenceAsync(
            self
            ,
            lhsExpression
            ,
            rhsExpression
    ):
        """
        Attempts to assign the object reference of the expression specified as the second
        argument to the expression specified as the first argument.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:              The handle to the target FreeFlyer engine.
        :param lhsExpression:       The expression to be assigned.
        :param rhsExpression:       The expression to be evaluated.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment is not a valid expression.
                             -   The expression specified for the right-hand-side of the assignment is not a valid expression.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable. Some possible reasons are:

                             -   The expression specified for the left-hand-side of the assignment it is not writeable.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable. Some possible reasons are:

                             -   The expression specified for the right-hand-side does not return an assignable reference.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The type specified by the right-hand-side expression is not compatible with type of the left-hand-side expression.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression. Some possible reasons are:

                             -   The right-hand-side and left-hand-side of the assignment are incompatible.
                             -   An error was thrown in evaluating the expression on the right-hand-side of the assignment.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if lhsExpression is None:
            raise TypeError("The argument 'lhsExpression' must not be NoneType.")

        if rhsExpression is None:
            raise TypeError("The argument 'rhsExpression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAssignExpressionReferenceAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(lhsExpression)
                ,
                Utilities.encodeString(rhsExpression)
            )
        )

    def getExpressionVariable(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the numeric scalar value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The numeric scalar value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric scalar.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        value = ctypes.c_double()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionVariable(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(value)
            )
        )

        return value.value

    def getExpressionVariableAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the numeric scalar value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The numeric scalar value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric scalar.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionVariableAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionArray(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the numeric array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The numeric array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        valueNumElements = ctypes.c_size_t()
        valueValue = ctypes.POINTER(ctypes.c_double)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(valueNumElements)
                ,
                byref(valueValue)
            )
        )

        return Utilities.nativeToPythonArray(valueNumElements, valueValue)

    def getExpressionArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the numeric array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The numeric array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionMatrix(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the numeric matrix value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The numeric matrix value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric matrix.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        valueNumRows = ctypes.c_size_t()
        valueNumCols = ctypes.c_size_t()
        valueValue = ctypes.POINTER(ctypes.c_double)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionMatrix(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(valueNumRows)
                ,
                byref(valueNumCols)
                ,
                byref(valueValue)
            )
        )

        return Utilities.nativeToPythonMatrix(valueNumRows, valueNumCols, valueValue)

    def getExpressionMatrixAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the numeric matrix value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The numeric matrix value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric matrix.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionMatrixAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionTimeSpan(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the timespan value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The timespan scalar value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan scalar.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        valueWholeSeconds = ctypes.c_int64()
        valueNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionTimeSpan(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(valueWholeSeconds)
                ,
                byref(valueNanoseconds)
            )
        )

        return FFTimeSpan.fromWholeSecondsAndNanoseconds(valueWholeSeconds.value, valueNanoseconds.value)

    def getExpressionTimeSpanAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the timespan value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The timespan scalar value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan scalar.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionTimeSpanAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionTimeSpanArray(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the timespan array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The timespan array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        valueNumElements = ctypes.c_size_t()
        valueWholeSeconds = ctypes.POINTER(ctypes.c_int64)()
        valueNanoseconds = ctypes.POINTER(ctypes.c_int64)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionTimeSpanArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(valueNumElements)
                ,
                byref(valueWholeSeconds)
                ,
                byref(valueNanoseconds)
            )
        )

        return Utilities.nativeToPythonTimeSpanArray(valueNumElements, valueWholeSeconds, valueNanoseconds)

    def getExpressionTimeSpanArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the timespan array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The timespan array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionTimeSpanArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionString(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the string value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The string value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        value = ctypes.c_char_p()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionString(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(value)
            )
        )

        return Utilities.nativeToPythonString(value)

    def getExpressionStringAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the string value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The string value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionStringAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def getExpressionStringArray(
            self
            ,
            expression
    ):
        """
        Attempts to retrieve the string array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.

        :returns:               The string array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        valueNumElements = ctypes.c_size_t()
        valueValue = ctypes.POINTER(ctypes.c_char_p)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionStringArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                byref(valueNumElements)
                ,
                byref(valueValue)
            )
        )

        return Utilities.nativeToPythonStringArray(valueNumElements, valueValue)

    def getExpressionStringArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to retrieve the string array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in either the Prepared, or
            Mission-Plan-Error state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to retrieve.
        :param value:           The string array value of the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string array.
                  -    ErrorExpressionNotReadable - The value of the specified expression is not readable.
                  -    ErrorExpressionFailedToEvaluate - The specified expression did not evaluate successfully.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetExpressionStringArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionVariable(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionVariable(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value
            )
        )

    def setExpressionVariableAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionVariableAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value
            )
        )

    def setExpressionVariableDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionVariableDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionArray(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonArrayToCArray(value)
            )
        )

    def setExpressionArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonArrayToCArray(value)
            )
        )

    def setExpressionArrayDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionArrayDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionMatrix(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric matrix value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric matrix value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric matrix.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionMatrix(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                0 if not value else len(value[0])
                ,
                Utilities.pythonMatrixToCMatrix(value)
            )
        )

    def setExpressionMatrixAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric matrix value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric matrix value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric matrix.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionMatrixAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                0 if not value else len(value[0])
                ,
                Utilities.pythonMatrixToCMatrix(value)
            )
        )

    def setExpressionMatrixDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the numeric matrix value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The numeric matrix value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a numeric matrix.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionMatrixDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionTimeSpan(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpan(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.wholeSeconds
                ,
                value.nanoseconds
            )
        )

    def setExpressionTimeSpanAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpanAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.wholeSeconds
                ,
                value.nanoseconds
            )
        )

    def setExpressionTimeSpanDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan scalar.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpanDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionTimeSpanArray(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpanArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonArrayToCInt64Array(Utilities.extractWholeSecondsArray(value))
                ,
                Utilities.pythonArrayToCInt64Array(Utilities.extractNanosecondsArray(value))
            )
        )

    def setExpressionTimeSpanArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpanArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonArrayToCInt64Array(Utilities.extractWholeSecondsArray(value))
                ,
                Utilities.pythonArrayToCInt64Array(Utilities.extractNanosecondsArray(value))
            )
        )

    def setExpressionTimeSpanArrayDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the timespan array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The timespan array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a timespan array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionTimeSpanArrayDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionString(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionString(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                Utilities.encodeString(value)
            )
        )

    def setExpressionStringAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionStringAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                Utilities.encodeString(value)
            )
        )

    def setExpressionStringDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionStringDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setExpressionStringArray(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionStringArray(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonStringArrayToCStringArray(value)
            )
        )

    def setExpressionStringArrayAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionStringArrayAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                len(value)
                ,
                Utilities.pythonStringArrayToCStringArray(value)
            )
        )

    def setExpressionStringArrayDynamicAsync(
            self
            ,
            expression
            ,
            value
    ):
        """
        Attempts to set the string array value of the specified expression.

        .. note::

            To call this function successfully, the engine must be in the Prepared state.

        :param engine:          The handle to the target FreeFlyer engine.
        :param expression:      The expression whose value to set.
        :param value:           The string array value with which to assign the specified expression.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorAsyncDataTypeMismatch - The type of the specified async data did not match the expected type. Some possible reasons are:

                             -   The type of the specified async data did not match the expected type.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
                  -    ErrorInvalidExpression - The specified expression is not valid.
                  -    ErrorFailedToSetExpressionValue - An error occurred while attempting to set the value of the specified expression.
                  -    ErrorExpressionNotWriteable - The value of the specified expression is not writeable.
                  -    ErrorExpressionTypeMismatch - The attempt to get or set the value of the specified expression failed because the type of the specified data did not match the type of the expression. Some possible reasons are:

                             -   The specified expression did not evaluate to a string array.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if expression is None:
            raise TypeError("The argument 'expression' must not be NoneType.")

        if value is None:
            raise TypeError("The argument 'value' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetExpressionStringArrayDynamicAsync(
                self._EngineHandle
                ,
                Utilities.encodeString(expression)
                ,
                value.getNativeData()
            )
        )

    def setSyncPointAsync(
            self
    ):
        """
        Attempts to add a sync point to the asynchronous queue of the specified engine.

        :param engine:      The handle to the target FreeFlyer engine.

        :returns:           The value of the created sync point. Use this value in conjunction with the sync
                            point wait functions.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        syncPoint = ctypes.c_uint64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetSyncPointAsync(
                self._EngineHandle
                ,
                byref(syncPoint)
            )
        )

        return syncPoint.value

    def waitForSyncPointAsync(
            self
            ,
            syncPoint
    ):
        """
        Attempts to block the asynchronous execution of the specified engine until the specified
        sync point is cleared.

        :param engine:          The handle to the target FreeFlyer engine.
        :param syncPoint:       The sync point on which to wait.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffWaitForSyncPointAsync(
                self._EngineHandle
                ,
                syncPoint
            )
        )

    def waitForAnySyncPointAsync(
            self
            ,
            syncPoints
    ):
        """
        Attempts to block the asynchronous execution of the specified engine until any of
        the specified sync points is cleared.

        :param engine:          The handle to the target FreeFlyer engine.
        :param syncPoints:      The array of sync points on which to wait.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if syncPoints is None:
            raise TypeError("The argument 'syncPoints' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffWaitForAnySyncPointAsync(
                self._EngineHandle
                ,
                len(syncPoints)
                ,
                Utilities.pythonArrayToCUInt64Array(syncPoints)
            )
        )

    def waitForAllSyncPointsAsync(
            self
            ,
            syncPoints
    ):
        """
        Attempts to block the asynchronous execution of the specified engine until all of
        the specified sync points are cleared.

        :param engine:          The handle to the target FreeFlyer engine.
        :param syncPoints:      The array of sync points on which to wait.

        :raises: RuntimeApiException possible errors include:

                  -    ErrorGeneral - An unspecified error occurred.
                  -    ErrorOutOfMemory - A requested memory allocation failed.
                  -    ErrorInvalidArgumentValue - One or more of the specified argument values are invalid.
                  -    ErrorInvalidEngineStateForOperation - The current engine state is not valid for the requested operation.
                  -    ErrorEngineUnexpectedlyTerminated - The specified engine unexpectedly terminated.
        """
        if self._IsClosed:
            raise RuntimeError("A closed engine cannot be used.")

        if syncPoints is None:
            raise TypeError("The argument 'syncPoints' must not be NoneType.")


        Utilities.checkResult(
            CInterfaceWrapper.lib.ffWaitForAllSyncPointsAsync(
                self._EngineHandle
                ,
                len(syncPoints)
                ,
                Utilities.pythonArrayToCUInt64Array(syncPoints)
            )
        )
