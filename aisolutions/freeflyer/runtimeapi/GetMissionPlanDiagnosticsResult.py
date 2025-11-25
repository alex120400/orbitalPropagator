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
    Contains a class which represents a Runtime API function result.
"""
class GetMissionPlanDiagnosticsResult:
    """
    Result class for the RuntimeApiEngine.getMissionPlanDiagnostics method.
    """

    def __init__(
            self
            ,
            errorsCount
            ,
            errors
            ,
            warningsCount
            ,
            warnings
    ):
        self.errorsCount = errorsCount
        self.errors = errors
        self.warningsCount = warningsCount
        self.warnings = warnings

    def getErrorsCount(self):
        """
           The number of errors retrieved.
        """

        return self.errorsCount
    def getErrors(self):
        """
           The text of the errors retrieved.
        """

        return self.errors
    def getWarningsCount(self):
        """
           The number of warnings retrieved.
        """

        return self.warningsCount
    def getWarnings(self):
        """
           The text of the warnings retrieved.
        """

        return self.warnings
