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
# aisolutions.freeflyer.runtimeapi package

"""
    This module provides an interface for creating, using, and manipulating asynchronous data
"""

import ctypes

from ctypes import byref

import warnings

from .CInterfaceWrapper import CInterfaceWrapper
from .Utilities import Utilities
from .FFTimeSpan import FFTimeSpan

class AsyncData:
    """
        Represents an asynchronous data instance used in asynchronous runtime API calls
    """

    def __init__(self):
        """
            Allocates a new instance of asynchronous data on the specified context.

            :raises: RuntimeApiException
        """
        self._asyncData = ctypes.c_void_p()
        self._isClosed = False

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAllocateAsyncData(byref(self._asyncData)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
            Releases the native resources associated with this instance. After
            this method is called, this instance can no longer be used.
        """

        if not self._isClosed:
            self._isClosed = True
            Utilities.checkResult(
                CInterfaceWrapper.lib.ffFreeAsyncData(self._asyncData))

    def getNativeData(self):
        """
            Get the native async data handle.
        """
        return self._asyncData

    def setDoubleValue(self, value):
        """
            Sets the numeric scalar value of the asynchronous data.

            :param value: The numeric scalar value to set.
        """
        if value is None:
            raise TypeError("The argument 'value' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataVariable(self._asyncData, value))

    def setDoubleArrayValue(self, value_array):
        """
            Sets the numeric array value of the asynchronous data.

            :param value_array: The numeric array value to set.
        """
        if value_array is None:
            raise TypeError("The argument 'value_array' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataArray(
                self._asyncData,
                len(value_array),
                Utilities.pythonArrayToCArray(value_array)))

    def setDoubleMatrixValue(self, value_matrix):
        """
            Sets the numeric matrix value of the asynchronous data.

            :param value_matrix: The numeric matrix value to set.
        """

        if value_matrix is None:
            raise TypeError("The argument 'value_matrix' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataMatrix(
                self._asyncData,
                len(value_matrix),
                0 if not value_matrix else len(value_matrix[0]),
                Utilities.pythonMatrixToCMatrix(value_matrix)))

    def setTimeSpanValue(self, value_timespan):
        """
            Sets the timespan value of the asynchronous data.

            :param value_timespan: The timespan value to set.
        """
        if value_timespan is None:
            raise TypeError("The argument 'value_timespan' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataTimeSpan(
                self._asyncData,
                value_timespan.wholeSeconds,
                value_timespan.nanoseconds))

    def setTimeSpanArrayValue(self, value_timespan_array):
        """
            Sets the timespan array value of the asynchronous data.

            :param value_timespan_array: The timespan array value to set.
        """

        if value_timespan_array is None:
            raise TypeError("The argument 'value_timespan_array' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataTimeSpanArray(
                self._asyncData,
                len(value_timespan_array),
                Utilities.pythonArrayToCInt64Array(
                    Utilities.extractWholeSecondsArray(value_timespan_array)),
                Utilities.pythonArrayToCInt64Array(
                    Utilities.extractNanosecondsArray(value_timespan_array))))

    def setStringValue(self, value_str):
        """
            Sets the string value of the asynchronous data.

            :param value_str: The string value to set.
        """

        if value_str is None:
            raise TypeError("The argument 'value_str' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataString(
                self._asyncData, Utilities.encodeString(value_str)))

    def setStringArrayValue(self, value_str_array):
        """
            Sets the string array value of the asynchronous data.

            :param value_str_array: The string array value to set.
        """
        if value_str_array is None:
            raise TypeError("The argument 'value_str_array' must not be None.")

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSetAsyncDataStringArray(
                self._asyncData,
                len(value_str_array),
                Utilities.pythonStringArrayToCStringArray(value_str_array)))

    def getDoubleValue(self):
        """
            Gets the numeric scalar value of the asynchronous data.

            :returns: The numeric scalar value of the asynchronous data.
        """

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        value = ctypes.c_double()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataVariable(
                self._asyncData,
                byref(value)))

        return value.value

    def getDoubleArrayValue(self):
        """
            Gets the numeric scalar value of the asynchronous data.

            :returns: The numeric scalar value of the asynchronous data.
        """

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        num_of_elements = ctypes.c_size_t()
        value = ctypes.POINTER(ctypes.c_double)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataArray(
                self._asyncData,
                byref(num_of_elements),
                byref(value)))

        return Utilities.nativeToPythonArray(num_of_elements, value)


    def getDoubleMatrixValue(self):
        """
            Gets the numeric matrix value of the asynchronous data.

            :returns: The numeric matrix value of the asynchronous data.
        """

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        num_of_rows = ctypes.c_size_t()
        num_of_cols = ctypes.c_size_t()
        value = ctypes.POINTER(ctypes.c_double)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataMatrix(
                self._asyncData,
                byref(num_of_rows),
                byref(num_of_cols),
                byref(value)))

        return Utilities.nativeToPythonMatrix(num_of_rows, num_of_cols, value)

    def getTimeSpanValue(self):
        """
            Gets the timespan scalar value of the asynchronous data.

            :returns: The timespan scalar value of the asynchronous data.
        """
        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        resultWholeSeconds = ctypes.c_int64()
        resultNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataTimeSpan(
                self._asyncData,
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        result = FFTimeSpan()
        result._wholeSeconds.value = resultWholeSeconds.value
        result._nanoseconds.value = resultNanoseconds.value

        return result

    def getTimeSpanArrayValue(self):
        """
            Gets the timespan array value of the asynchronous data.

            :returns: The timespan array value of the asynchronous data.
        """
        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        resultNumElements = ctypes.c_size_t()
        resultWholeSeconds = ctypes.POINTER(ctypes.c_int64)()
        resultNanoseconds = ctypes.POINTER(ctypes.c_int64)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataTimeSpanArray(
                self._asyncData,
                byref(resultNumElements),
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        return Utilities.nativeToPythonTimeSpanArray(
            resultNumElements,
            resultWholeSeconds,
            resultNanoseconds)


    def getStringValue(self):
        """
            Gets the string value of the asynchronous data.

            :returns: The string value of the asynchronous data.
        """

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        value = ctypes.c_char_p()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataString(
                self._asyncData,
                byref(value)))

        return Utilities.nativeToPythonString(value)

    def getStringArray(self):
        """
            Gets the string array value of the asynchronous data.

            :returns: The string  array value of the asynchronous data.
        """

        warnings.warn(
            "getStringArray is deprecated. Use getStringArrayValue instead.",
            DeprecationWarning)
        return self.getStringArrayValue()

    def getStringArrayValue(self):
        """
            Gets the string array value of the asynchronous data.

            :returns: The string  array value of the asynchronous data.
        """

        if self._isClosed:
            raise RuntimeError("A closed AsyncData instance cannot be used.")

        num_of_elements = ctypes.c_size_t()
        value = ctypes.POINTER(ctypes.c_char_p)()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetAsyncDataStringArray(
                self._asyncData,
                byref(num_of_elements),
                byref(value)))

        return Utilities.nativeToPythonStringArray(num_of_elements, value)
