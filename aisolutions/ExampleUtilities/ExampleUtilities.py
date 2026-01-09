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
"""This module contains example utilities"""
import sys
import os
import platform
import ctypes
import subprocess

import os.path

class ExampleUtilities:
    """Provides means of getting paths to examples, freeflyer
	install directory and to set working directory"""

    def __init__(self):
        pass

    @staticmethod
    def set_working_directory_to_program_directory():
        """Sets working directory to program directory"""
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


    @staticmethod
    def get_freeflyer_install_directory():
        """Gets path to freeflyer exe"""
        if sys.platform.lower().startswith("win", 0, 3):
            ff_install_dir = ""
            if platform.architecture()[0] == '64bit':
                ff_install_dir = os.environ['FREEFLYER_64_INSTALL_DIRECTORY']
            else:
                raise OSError("Non 64-bit system detected. FreeFlyer is only supported for 64-bit systems.")
            return ff_install_dir
        else:
            active_install_file_path = "/usr/share/a.i. solutions, Inc/FreeFlyer/active_ff_install"
            if os.path.isfile(active_install_file_path):
                with open(active_install_file_path, 'r') as path_file:
                    path = path_file.read()
                    invalid_chars_list = [' ', '\r', '\n']
                    for inval_char in invalid_chars_list:
                        path = path.strip(inval_char)

                    path = path + "/"
                    return path
            else:
                return ""

    @staticmethod
    def get_examples_path():
        """Get the path to examples"""
        if sys.platform.lower().startswith("win", 0, 3):
            from ctypes import wintypes
            
            bitness = platform.architecture()[0].lower()

            #Get FreeFlyer version by running ff.exe with argument '-v'
            file_name = os.path.normpath(os.path.join(ExampleUtilities.get_freeflyer_install_directory(), "ff"))
            argument = "-v"
            get_version_process = subprocess.Popen([file_name, argument], stdout=subprocess.PIPE, \
                                                   shell=False, creationflags=0x08000000)
            get_version_process.wait()
            ff_version = get_version_process.stdout.read().decode("utf-8")

            invalid_chars_list = [' ', '\r', '\n']
            for inval_char in invalid_chars_list:
                ff_version = ff_version.replace(inval_char, "")


            #Get special Home directory. e.g Documents
            csidl_personal = 5
            sh_get_folder_path = ctypes.windll.shell32.SHGetFolderPathW
            psz_path = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            sh_get_folder_path.argtypes = [wintypes.HWND, ctypes.c_int, \
                                       wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR]
            h_result = sh_get_folder_path(0, csidl_personal, 0, 0, psz_path)

            if h_result == 0:
                path_to_home = psz_path.value
            else:
                raise OSError("Documents directory not found.")


            example_path = path_to_home +\
                           "\\FreeFlyer" +\
                           "\\FreeFlyer " + ff_version + " (" + bitness[0:2] + "-Bit" + ")" +\
                           "\\Runtime API" +\
                           "\\examples_common"
            return example_path
        else:
            path_to_home = os.environ['HOME']
            active_install_file_path = "/usr/share/a.i. solutions, Inc/FreeFlyer/active_ff_install"

            if os.path.isfile(active_install_file_path):
                with open(active_install_file_path, 'r') as path_file:
                    path = path_file.read()
                    ff_version = path.replace("/usr/share/a.i. solutions, Inc/", "")

                    invalid_chars_list = [' ', '\r', '\n']
                    for inval_char in invalid_chars_list:
                        ff_version = ff_version.strip(inval_char)

                    example_path = path_to_home + "/FreeFlyer/" + ff_version + \
                                   "/Runtime API/examples_common/"

                    return example_path

        return ""

    @staticmethod
    def combine_paths(*paths):
        """Combines elements in an array to form a path"""
        if len(paths) == 0:
            return ""
        else:
            i = 0
            result = ""

            while i < len(paths):
                if i != 0:
                    result = os.path.join(str(result), str(paths[i]))
                else:
                    result = result + paths[i]
                i += 1

        return result
