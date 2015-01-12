""" Utils
"""
import os
import Globals


def get_logs_path(log):
    """ Returns the path for requested log
    """
    dir_path = os.environ.get(log)
    if not dir_path:
        dir_path = Globals.ZOPE_HOME + "/var/log"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path
