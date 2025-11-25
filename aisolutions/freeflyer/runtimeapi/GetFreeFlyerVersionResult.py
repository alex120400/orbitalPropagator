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
class GetFreeFlyerVersionResult:
    """
    Result class for the RuntimeApiEngine.getFreeFlyerVersion method.
    """

    def __init__(
            self
            ,
            major
            ,
            minor
            ,
            build
            ,
            revision
    ):
        self.major = major
        self.minor = minor
        self.build = build
        self.revision = revision

    def getMajor(self):
        """
           The major version of FreeFlyer.
        """

        return self.major
    def getMinor(self):
        """
           The minor version of FreeFlyer.
        """

        return self.minor
    def getBuild(self):
        """
           The build version of FreeFlyer.
        """

        return self.build
    def getRevision(self):
        """
           The revision version of FreeFlyer.
        """

        return self.revision
