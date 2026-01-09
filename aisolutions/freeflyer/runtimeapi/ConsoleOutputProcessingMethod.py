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

class ConsoleOutputProcessingMethod:
    """
        Determines how console output from the engine will be handled.
    """
    RedirectToRuntimeApi = 0
    """
    Console output will be captured and available to be retrieved by the GetConsoleOutput
    function.
    """
    RedirectToHost = 1
    """
    Console output will be merged into the console output of the host application.
    """
    Suppress = 2
    """
    Console output will be captured and discarded.
    """
