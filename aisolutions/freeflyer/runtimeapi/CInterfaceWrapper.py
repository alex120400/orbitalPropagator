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
"""
    This module interfaces with the Runtime API C-interface.
"""
# aisolutions.freeflyer.runtimeapi package

import sys
import ctypes
from os import path

class CInterfaceWrapper:
    """
        A class which interfaces with the Runtime API C-interface.
    """
    lib = None

    @staticmethod
    def initialize(ffInstallPath):
        """
            Load the shared library and imported functions.
        """
        mes = (
            "The specified FreeFlyer install path '" + ffInstallPath + "' "
            "does not appear to be valid. "
            "Potential reasons include:\n"
            "The path does not exist or does not point to a FreeFlyer installation.\n"
            "The referenced FreeFlyer installation does not match "
            "the 'bitness' of this host application.\n"
            "The referenced FreeFlyer installation is not recent enough.\n"
            "The referenced FreeFlyer installation is corrupt."
        )

        ciw = CInterfaceWrapper

        try:
            if not sys.platform.lower().startswith("win", 0, 3):
                ciw.lib = ctypes.CDLL(path.normpath(path.join(ffInstallPath, "libffrtapi.so")))
            else:
                ciw.lib = ctypes.CDLL(path.normpath(path.join(ffInstallPath, "ffrtapi")))
        except Exception as exc:
            raise RuntimeError(mes) from exc

        ciw.lib.ffGetResultDescription.argtypes = [
            ctypes.c_int32
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetResultDescription.restype = ctypes.c_int32

        ciw.lib.ffGetRuntimeApiVersion.argtypes = [
            ctypes.POINTER(ctypes.c_int32)
            ,
            ctypes.POINTER(ctypes.c_int32)
        ]
        ciw.lib.ffGetRuntimeApiVersion.restype = ctypes.c_int32

        ciw.lib.ffGetFreeFlyerVersion.argtypes = [
            ctypes.POINTER(ctypes.c_int32)
            ,
            ctypes.POINTER(ctypes.c_int32)
            ,
            ctypes.POINTER(ctypes.c_int32)
            ,
            ctypes.POINTER(ctypes.c_int32)
        ]
        ciw.lib.ffGetFreeFlyerVersion.restype = ctypes.c_int32

        ciw.lib.ffCreateEngine.argtypes = [
            ctypes.c_int32
            ,
            ctypes.c_int32
            ,
            ctypes.c_int32
            ,
            ctypes.POINTER(ctypes.c_void_p)
        ]
        ciw.lib.ffCreateEngine.restype = ctypes.c_int32

        ciw.lib.ffCreateEngineWithOutputWindowSupport.argtypes = [
            ctypes.c_int32
            ,
            ctypes.c_int32
            ,
            ctypes.c_int32
            ,
            ctypes.c_int32
            ,
            ctypes.POINTER(ctypes.c_void_p)
        ]
        ciw.lib.ffCreateEngineWithOutputWindowSupport.restype = ctypes.c_int32

        ciw.lib.ffDestroyEngine.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffDestroyEngine.restype = ctypes.c_int32

        ciw.lib.ffKillEngine.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffKillEngine.restype = ctypes.c_int32

        ciw.lib.ffIsEngineIdle.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_bool)
        ]
        ciw.lib.ffIsEngineIdle.restype = ctypes.c_int32

        ciw.lib.ffGetConsoleOutput.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetConsoleOutput.restype = ctypes.c_int32

        ciw.lib.ffFreeMemory.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffFreeMemory.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromFile.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadMissionPlanFromFile.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromFileAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadMissionPlanFromFileAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromFileDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadMissionPlanFromFileDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadMissionPlanFromString.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromStringAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadMissionPlanFromStringAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadMissionPlanFromStringDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadMissionPlanFromStringDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFile.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFile.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFileAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFileAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFileDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFileDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFile2.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int32
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFile2.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFile2Async.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int32
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFile2Async.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromFile2DynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromFile2DynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromString.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromStringAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromStringAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromStringDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromStringDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromString2.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int32
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromString2.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromString2Async.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int32
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromString2Async.restype = ctypes.c_int32

        ciw.lib.ffLoadFreeFlyerScriptFromString2DynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
            ,
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffLoadFreeFlyerScriptFromString2DynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetUserInfoArguments.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffSetUserInfoArguments.restype = ctypes.c_int32

        ciw.lib.ffSetUserInfoArgumentsAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffSetUserInfoArgumentsAsync.restype = ctypes.c_int32

        ciw.lib.ffSetUserInfoArgumentsDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetUserInfoArgumentsDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffPrepareMissionPlan.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffPrepareMissionPlan.restype = ctypes.c_int32

        ciw.lib.ffPrepareMissionPlanAsync.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffPrepareMissionPlanAsync.restype = ctypes.c_int32

        ciw.lib.ffCleanupMissionPlan.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffCleanupMissionPlan.restype = ctypes.c_int32

        ciw.lib.ffCleanupMissionPlanAsync.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffCleanupMissionPlanAsync.restype = ctypes.c_int32

        ciw.lib.ffExecuteStatement.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffExecuteStatement.restype = ctypes.c_int32

        ciw.lib.ffExecuteStatementAsync.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffExecuteStatementAsync.restype = ctypes.c_int32

        ciw.lib.ffExecuteRemainingStatements.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffExecuteRemainingStatements.restype = ctypes.c_int32

        ciw.lib.ffExecuteRemainingStatementsAsync.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffExecuteRemainingStatementsAsync.restype = ctypes.c_int32

        ciw.lib.ffExecuteUntilApiLabel.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffExecuteUntilApiLabel.restype = ctypes.c_int32

        ciw.lib.ffExecuteUntilApiLabelAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffExecuteUntilApiLabelAsync.restype = ctypes.c_int32

        ciw.lib.ffExecuteUntilApiLabelDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffExecuteUntilApiLabelDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffIsMissionPlanComplete.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_bool)
        ]
        ciw.lib.ffIsMissionPlanComplete.restype = ctypes.c_int32

        ciw.lib.ffGetExecutionNumber.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffGetExecutionNumber.restype = ctypes.c_int32

        ciw.lib.ffGetLocation.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_char_p)
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetLocation.restype = ctypes.c_int32

        ciw.lib.ffGetMissionPlanDiagnostics.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_int32
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.c_char_p)
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetMissionPlanDiagnostics.restype = ctypes.c_int32

        ciw.lib.ffEvaluateExpression.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffEvaluateExpression.restype = ctypes.c_int32

        ciw.lib.ffEvaluateExpressionAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffEvaluateExpressionAsync.restype = ctypes.c_int32

        ciw.lib.ffAssignExpression.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffAssignExpression.restype = ctypes.c_int32

        ciw.lib.ffAssignExpressionAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffAssignExpressionAsync.restype = ctypes.c_int32

        ciw.lib.ffAssignExpressionReference.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffAssignExpressionReference.restype = ctypes.c_int32

        ciw.lib.ffAssignExpressionReferenceAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffAssignExpressionReferenceAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionVariable.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffGetExpressionVariable.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionVariableAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionVariableAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        ]
        ciw.lib.ffGetExpressionArray.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionMatrix.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        ]
        ciw.lib.ffGetExpressionMatrix.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionMatrixAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionMatrixAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionTimeSpan.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffGetExpressionTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionTimeSpanAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionTimeSpanAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionTimeSpanArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int64))
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int64))
        ]
        ciw.lib.ffGetExpressionTimeSpanArray.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionTimeSpanArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionTimeSpanArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetExpressionString.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionStringAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionStringAsync.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionStringArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))
        ]
        ciw.lib.ffGetExpressionStringArray.restype = ctypes.c_int32

        ciw.lib.ffGetExpressionStringArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffGetExpressionStringArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionVariable.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_double
        ]
        ciw.lib.ffSetExpressionVariable.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionVariableAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_double
        ]
        ciw.lib.ffSetExpressionVariableAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionVariableDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionVariableDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetExpressionArray.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetExpressionArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionArrayDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionArrayDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionMatrix.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetExpressionMatrix.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionMatrixAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetExpressionMatrixAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionMatrixDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionMatrixDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpan.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
        ]
        ciw.lib.ffSetExpressionTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpanAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
        ]
        ciw.lib.ffSetExpressionTimeSpanAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpanDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionTimeSpanDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpanArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffSetExpressionTimeSpanArray.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpanArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffSetExpressionTimeSpanArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionTimeSpanArrayDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionTimeSpanArrayDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffSetExpressionString.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionStringAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffSetExpressionStringAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionStringDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionStringDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionStringArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffSetExpressionStringArray.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionStringArrayAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffSetExpressionStringArrayAsync.restype = ctypes.c_int32

        ciw.lib.ffSetExpressionStringArrayDynamicAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
            ,
            ctypes.c_void_p
        ]
        ciw.lib.ffSetExpressionStringArrayDynamicAsync.restype = ctypes.c_int32

        ciw.lib.ffAllocateAsyncData.argtypes = [
            ctypes.POINTER(ctypes.c_void_p)
        ]
        ciw.lib.ffAllocateAsyncData.restype = ctypes.c_int32

        ciw.lib.ffFreeAsyncData.argtypes = [
            ctypes.c_void_p
        ]
        ciw.lib.ffFreeAsyncData.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataVariable.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_double
        ]
        ciw.lib.ffSetAsyncDataVariable.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetAsyncDataArray.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataMatrix.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffSetAsyncDataMatrix.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataTimeSpan.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
        ]
        ciw.lib.ffSetAsyncDataTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataTimeSpanArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffSetAsyncDataTimeSpanArray.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_char_p
        ]
        ciw.lib.ffSetAsyncDataString.restype = ctypes.c_int32

        ciw.lib.ffSetAsyncDataStringArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffSetAsyncDataStringArray.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataVariable.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffGetAsyncDataVariable.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        ]
        ciw.lib.ffGetAsyncDataArray.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataMatrix.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
        ]
        ciw.lib.ffGetAsyncDataMatrix.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataTimeSpan.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffGetAsyncDataTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataTimeSpanArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int64))
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int64))
        ]
        ciw.lib.ffGetAsyncDataTimeSpanArray.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataString.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_char_p)
        ]
        ciw.lib.ffGetAsyncDataString.restype = ctypes.c_int32

        ciw.lib.ffGetAsyncDataStringArray.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_size_t)
            ,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))
        ]
        ciw.lib.ffGetAsyncDataStringArray.restype = ctypes.c_int32

        ciw.lib.ffIsValidTimeSpan.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_bool)
        ]
        ciw.lib.ffIsValidTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffIsUndefinedTimeSpan.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_bool)
        ]
        ciw.lib.ffIsUndefinedTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffCompareTimeSpans.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_int32)
        ]
        ciw.lib.ffCompareTimeSpans.restype = ctypes.c_int32

        ciw.lib.ffAddTimeSpans.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffAddTimeSpans.restype = ctypes.c_int32

        ciw.lib.ffSubtractTimeSpans.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffSubtractTimeSpans.restype = ctypes.c_int32

        ciw.lib.ffScaleTimeSpan.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.c_double
            ,
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffScaleTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffGetUndefinedTimeSpan.argtypes = [
            ctypes.POINTER(ctypes.c_int64)
            ,
            ctypes.POINTER(ctypes.c_int64)
        ]
        ciw.lib.ffGetUndefinedTimeSpan.restype = ctypes.c_int32

        ciw.lib.ffGetTimeSpanAsSeconds.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffGetTimeSpanAsSeconds.restype = ctypes.c_int32

        ciw.lib.ffGetTimeSpanAsDays.argtypes = [
            ctypes.c_int64
            ,
            ctypes.c_int64
            ,
            ctypes.POINTER(ctypes.c_double)
        ]
        ciw.lib.ffGetTimeSpanAsDays.restype = ctypes.c_int32

        ciw.lib.ffSynchronize.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_int32
            ,
            ctypes.POINTER(ctypes.c_int32)
        ]
        ciw.lib.ffSynchronize.restype = ctypes.c_int32

        ciw.lib.ffSetSyncPointAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.POINTER(ctypes.c_uint64)
        ]
        ciw.lib.ffSetSyncPointAsync.restype = ctypes.c_int32

        ciw.lib.ffWaitForSyncPointAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_uint64
        ]
        ciw.lib.ffWaitForSyncPointAsync.restype = ctypes.c_int32

        ciw.lib.ffWaitForAnySyncPointAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_uint64)
        ]
        ciw.lib.ffWaitForAnySyncPointAsync.restype = ctypes.c_int32

        ciw.lib.ffWaitForAllSyncPointsAsync.argtypes = [
            ctypes.c_void_p
            ,
            ctypes.c_size_t
            ,
            ctypes.POINTER(ctypes.c_uint64)
        ]
        ciw.lib.ffWaitForAllSyncPointsAsync.restype = ctypes.c_int32
