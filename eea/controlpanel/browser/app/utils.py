""" Utils
"""
import os
from App.config import getConfiguration

cfg = getConfiguration()
ZOPEHOME = getattr(cfg, 'zopehome', '')


def get_logs_path(log):
    """ Returns the path for requested log
    """
    dir_path = os.environ.get(log)
    if not dir_path:
        dir_path = ZOPEHOME + "/var/log"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path
