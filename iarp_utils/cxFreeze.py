import os
import sys


def resource_path(filename):
    """ Used in cx_Freeze environments, returns a path to file_name
    local to the root file running as the exe.

    When a cx_freeze exe file runs the os.path is
    "C:/path/to/folder/library.zip" which is incorrect.

    Args:
        filename: filename to be used building the path.

    Returns:
        String containing the full path and filename.
    """
    return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), filename)
