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
    Contains a class for interfacing with FreeFlyer timespans.
"""

import ctypes

from ctypes import byref

from .CInterfaceWrapper import CInterfaceWrapper

class FFTimeSpan:
    """
        A class to represent a FreeFlyer timespan value.
    """
    def __init__(self):
        self._wholeSeconds = ctypes.c_int64(0)
        self._nanoseconds = ctypes.c_int64(0)

    @property
    def wholeSeconds(self):
        """ Returns the whole seconds component of the timespan. """
        return self._wholeSeconds.value

    @property
    def nanoseconds(self):
        """ Returns the nanoseconds component of the timespan. """
        return self._nanoseconds.value

    @staticmethod
    def fromWholeSecondsAndNanoseconds(wholeSeconds, nanoseconds):
        """
            Create a timespan from whole seconds and nanoseconds.

            :param wholeSeconds: The whole seconds component of the timespan.
            :param nanoseconds: The nanoseconds component of the timespan.
            :returns: The timespan corresponding to the specified components
        """
        from .Utilities import Utilities

        if wholeSeconds is None:
            raise TypeError("The argument 'wholeSeconds' must not be None.")

        if nanoseconds is None:
            raise TypeError("The argument 'nanoseconds' must not be None.")

        isValidData = ctypes.c_bool()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffIsValidTimeSpan(
                wholeSeconds,
                nanoseconds,
                byref(isValidData)))

        if not isValidData:
            raise ValueError("The specified data does not represent a valid timespan.")

        result = FFTimeSpan()
        result._wholeSeconds.value = wholeSeconds
        result._nanoseconds.value = nanoseconds

        return result

    @staticmethod
    def undefined():
        """
            Returns the undefined timespan value.
        """
        from .Utilities import Utilities

        resultWholeSeconds = ctypes.c_int64()
        resultNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetUndefinedTimeSpan(
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        result = FFTimeSpan()

        result._wholeSeconds.value = resultWholeSeconds.value
        result._nanoseconds.value = resultNanoseconds.value

        return result

    def isUndefined(self):
        """
            Returns true if the timespan represents an undefined value and false otherwise.
        """
        from .Utilities import Utilities

        result = ctypes.c_bool()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffIsUndefinedTimeSpan(
                self._wholeSeconds,
                self._nanoseconds,
                byref(result)))

        return result.value

    def scale(self, scaleFactor):
        """
            Scales the value of the timespan.

            :param scaleFactor: The scale factor to apply.
            :returns: The scaled timespan.
        """
        from .Utilities import Utilities

        if scaleFactor is None:
            raise TypeError("The argument 'scaleFactor' must not be None.")

        resultWholeSeconds = ctypes.c_int64()
        resultNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffScaleTimeSpan(
                self._wholeSeconds,
                self._nanoseconds,
                scaleFactor,
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        result = FFTimeSpan()
        result._wholeSeconds = resultWholeSeconds
        result._nanoseconds = resultNanoseconds

        return result

    def __neg__(self):
        """
            Negates the value of the timespan.

            :returns: The negated timespan.
        """
        if self.isUndefined():
            raise ValueError("An undefined timespan cannot be negated.")

        result = FFTimeSpan()
        result._wholeSeconds.value = -self._wholeSeconds.value
        result._nanoseconds.value = -self._nanoseconds.value

        return result

    def __add__(self, rhs):
        """
            Add the values of the specified timespans.

            :param rhs: The right-hand-side of the addition.
            :returns: The result of the addition.
        """
        from .Utilities import Utilities

        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        resultWholeSeconds = ctypes.c_int64()
        resultNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffAddTimeSpans(
                self._wholeSeconds,
                self._nanoseconds,
                rhs._wholeSeconds,
                rhs._nanoseconds,
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        result = FFTimeSpan()
        result._wholeSeconds.value = resultWholeSeconds.value
        result._nanoseconds.value = resultNanoseconds.value

        return result

    def __sub__(self, rhs):
        """
            Subtract the values of the specified timespans.

            :param rhs: The right-hand-side of the subtraction.
            :returns: The result of the subtraction.
        """
        from .Utilities import Utilities

        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        resultWholeSeconds = ctypes.c_int64()
        resultNanoseconds = ctypes.c_int64()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffSubtractTimeSpans(
                self._wholeSeconds,
                self._nanoseconds,
                rhs._wholeSeconds,
                rhs._nanoseconds,
                byref(resultWholeSeconds),
                byref(resultNanoseconds)))

        result = FFTimeSpan()
        result._wholeSeconds.value = resultWholeSeconds.value
        result._nanoseconds.value = resultNanoseconds.value

        return result

    def __lt__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is less than the specified value.
        """
        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        if self.isUndefined() or rhs.isUndefined():
            raise ValueError("Operator not defined for undefined timespans.")

        return self.compareTo(rhs) < 0

    def __gt__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is greater than the specified value.
        """
        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        if self.isUndefined() or rhs.isUndefined():
            raise ValueError("Operator not defined for undefined timespans.")

        return self.compareTo(rhs) > 0

    def __eq__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is equal to the specified value.
        """
        if rhs is None:
            return False

        return self.compareTo(rhs) == 0

    def __hash__(self):
        """
            Calculates the hash of the object.
        """
        return hash((self.wholeSeconds, self.nanoseconds))

    def __ne__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is not equal to the specified value.
        """
        if rhs is None:
            return True

        return self.compareTo(rhs) != 0

    def __le__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is less than or equal to the specified value.
        """
        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        if self.isUndefined() or rhs.isUndefined():
            raise ValueError("Operator not defined for undefined timespans.")

        return self.compareTo(rhs) <= 0

    def __ge__(self, rhs):
        """
            Returns true if the timespan value of the instance
            is greater than or equal to the specified value.
        """
        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        if self.isUndefined() or rhs.isUndefined():
            raise ValueError("Operator not defined for undefined timespans.")

        return self.compareTo(rhs) >= 0

    def compareTo(self, rhs):
        """
            Returns true if the timespan value of the instance
            is less than the specified value.

            :returns:
                Returns -1 if this instance is less than the specified object,
                0 if this instance is equal to the specified object,
                and 1 if this instance is greater than the specified object.
        """
        from .Utilities import Utilities

        if rhs is None:
            raise TypeError("The argument 'rhs' must not be None.")

        result = ctypes.c_int32()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffCompareTimeSpans(
                self._wholeSeconds,
                self._nanoseconds,
                rhs._wholeSeconds,
                rhs._nanoseconds,
                byref(result)))

        return result.value

    def getValueAsSeconds(self):
        """
            Converts the timespan into a double-precision value in units of
            seconds. Note that precision may be lost in this conversion.
        """
        from .Utilities import Utilities

        result = ctypes.c_double()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetTimeSpanAsSeconds(
                self._wholeSeconds,
                self._nanoseconds,
                byref(result)))

        return result.value

    def getValueAsDays(self):
        """
            Converts the timespan into a double-precision value in units of
            days. Note that precision may be lost in this conversion.
        """
        from .Utilities import Utilities

        result = ctypes.c_double()

        Utilities.checkResult(
            CInterfaceWrapper.lib.ffGetTimeSpanAsDays(
                self._wholeSeconds,
                self._nanoseconds,
                byref(result)))

        return result.value
