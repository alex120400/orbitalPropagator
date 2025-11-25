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
    Contains a class representing an enumeration.
"""

class WindowedOutputMode:
    """
        Determines whether output windows will be generated and whether or not they are
        used for image generation only.
    """
    NoOutputWindowSupport = 0
    """
    Output windows are not generated at runtime.
    """
    GenerateOutputWindows = 1
    """
    Output windows are generated and shown to the user.
    """
    HideMainOutputWorkspace = 2
    """
    Hides the main output workspace, but shows any unconstrained windows.
    """
    GenerateImagesOnly = 3
    """
    Output windows are generated and can be used to capture images, but not shown to
    the user.
    """
