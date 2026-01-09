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
    Utilities for marshalling data between python and the exported Runtime API functions.
"""

import ctypes
import sys
import locale

from .FFTimeSpan import FFTimeSpan
from .CInterfaceWrapper import CInterfaceWrapper
from .RuntimeApiException import RuntimeApiException

class Utilities:
    """
        Utilities for marshalling data between python and the exported Runtime API functions.
    """
    @staticmethod
    def nativeToPythonArray(num_elements, p_native_array):
        """
            Convert a native C-array into a python array.
        """
        try:
            if num_elements == 0:
                return []

            return [p_native_array[i] for i in range(num_elements.value)]

        finally:
            CInterfaceWrapper.lib.ffFreeMemory(p_native_array)

    @staticmethod
    def nativeToPythonMatrix(num_rows, num_cols, p_native_matrix):
        """
            Convert a native C-matrix into a python matrix.
        """
        try:
            if num_rows == 0:
                return [[]]

            if num_cols == 0:
                return [[]]

            return [[p_native_matrix[j + i*num_cols.value]
                     for j in range(num_cols.value)] for i in range(num_rows.value)]

        finally:
            CInterfaceWrapper.lib.ffFreeMemory(p_native_matrix)

    @staticmethod
    def nativeToPythonString(native_string):
        """
            Convert a native C-string into a python string.
        """
        try:
            pyString = native_string.value

            if sys.version_info[0] >= 3:
                pyString = pyString.decode(locale.getpreferredencoding(), 'replace')

            return pyString

        finally:
            CInterfaceWrapper.lib.ffFreeMemory(native_string)

    @staticmethod
    def nativeToPythonStringArray(num_elements, native_string_array):
        """
            Convert a native C-string-array into a python string array.
        """
        def nToPSA(pyString):
            """ Local utility function to convert each array value. """
            if sys.version_info[0] >= 3:
                pyString = pyString.decode(locale.getpreferredencoding(), 'replace')

            return pyString

        try:
            if num_elements == 0:
                return []

            return [nToPSA(native_string_array[i])
                    for i in range(num_elements.value)]

        finally:
            CInterfaceWrapper.lib.ffFreeMemory(native_string_array)

    @staticmethod
    def nativeToPythonTimeSpanArray(
            num_elements,
            native_whole_seconds_array,
            native_nanoseconds_array):
        """
            Convert a native C-timespan-array into a python timespan array.
        """
        wholeSeconds = Utilities.nativeToPythonArray(
            num_elements,
            native_whole_seconds_array)

        nanoseconds = Utilities.nativeToPythonArray(
            num_elements,
            native_nanoseconds_array)

        return [
            FFTimeSpan.fromWholeSecondsAndNanoseconds(
                wholeSeconds[i],
                nanoseconds[i]) for i in range(num_elements.value)]

    @staticmethod
    def pythonArrayToCArray(value):
        """
            Convert a list of double into a C-array.
        """
        return (ctypes.c_double * len(value))(*value)

    @staticmethod
    def pythonArrayToCInt64Array(value):
        """
            Convert a list of int into a C-int64-array.
        """
        return (ctypes.c_int64 * len(value))(*value)

    @staticmethod
    def pythonArrayToCUInt64Array(value):
        """
            Convert a list of int into a C-uint64-array.
        """
        return (ctypes.c_uint64 * len(value))(*value)

    @staticmethod
    def pythonMatrixToCMatrix(value):
        """
            Convert a 2d list of double into a C-matrix.
        """
        flat_list = [item for sublist in value for item in sublist]

        num_rows = len(value)
        num_cols = 0 if num_rows == 0 else len(value[0])

        return (ctypes.c_double * (num_rows*num_cols))(*flat_list)

    @staticmethod
    def pythonStringArrayToCStringArray(value):
        """
            Convert a python string array to a c-string-array
        """
        result = (ctypes.c_char_p * len(value))()

        for i, item in enumerate(value):
            result[i] = Utilities.encodeString(item)

        return result

    @staticmethod
    def extractWholeSecondsArray(value):
        """
            Extract an array of whole seconds from an array of timespan
        """
        return [item.wholeSeconds for item in value]

    @staticmethod
    def extractNanosecondsArray(value):
        """
            Extract an array of nanoseconds from an array of timespan
        """
        return [item.nanoseconds for item in value]

    @staticmethod
    def encodeString(theStr):
        """
            Encode the python string into the local codepage
        """
        if sys.version_info[0] >= 3:
            return theStr.encode(locale.getpreferredencoding(), 'replace')

        return theStr #already in preferred encoding

    @staticmethod
    def isComposedResultAnError(composed_result):
        """
            Determine if the specified result is an error.
        """
        return composed_result < 0

    @staticmethod
    def checkResult(composed_result):
        """
            Raise an exception if the result is an error.
        """
        if Utilities.isComposedResultAnError(composed_result):
            raise RuntimeApiException(composed_result)

    @staticmethod
    def getFunctionId(composed_result):
        """
            Extract the function id from the composed result code.
        """
        functionId = 0x0000FFFF & composed_result
        return functionId

    @staticmethod
    def getResult(composed_result):
        """
            Extract the result id from the composed result code.
        """
        result = (composed_result) >> 16
        return result

    @staticmethod
    def createComposedResult(functionId, result):
        """
            Create a composed result from a function id and result id.
        """
        return (result.getNativeValue() << 16) | int(functionId)
