""" Controllers
"""
import logging
import json
import Globals
from DateTime import DateTime
from datetime import datetime
from zope.component import queryUtility, queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api

LOGINAGENT_PATH = Globals.ZOPE_HOME + "/var/log/loginagent.log"
logger = logging.getLogger('eea.controlpanel')
loginagentlogger = logging.getLogger("eea.controlpanel.loginagent")
handler = logging.handlers.RotatingFileHandler(LOGINAGENT_PATH, maxBytes=52428800, backupCount=10)
loginagentlogger.addHandler(handler)
loginagentlogger.setLevel(logging.DEBUG)

def jsonify(data, response=None, status=None):
    """ Convert obj to JSON
    """
    if response:
        response.setHeader("Content-type", "application/json")
        if status:
            response.setStatus(status)
    return PythonObjectEncoder(indent=2, sort_keys=True).encode(data)


class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, DateTime):
            return obj.asdatetime().strftime("%Y-%m-%d %H:%M:%S")
        return {'_python_object': pickle.dumps(obj)}


class ControlPanel(BrowserView):
    """
    """


class ControlPanelDBActivity(BrowserView):
    """
    """

    def __call__(self, **kwargs):
        """
        """
        portal = api.portal.get()
        return jsonify({
            "name": "EEA Control Panel API",
            "log": portal.undoable_transactions(first_transaction=0,
                                                last_transaction=10000)
            }, self.request.response)


class ControlPanelLoginStatusAgent(BrowserView):
    """ Report login status
    """

    def __call__(self, **kwargs):
        """
        """
        if not api.user.is_anonymous():
            user = api.user.get_current()
            username = user.id
            fullname = user.getProperty('fullname')
            today = DateTime()
            localized = api.portal.get_localized_time(datetime=today,
                                                      long_format=True)
            data = {
                "date": localized,
                "fullname": fullname,
                "username": username
            }
            loginagentlogger.debug(json.dumps(data))


class ControlPanelLoginStatus(BrowserView):
    """
    """

    def load_logs(self, logpath):
        """ Load the log file
        """
        with open(logpath, "r") as f:
            return jsonify({
                "name": "EEA Control Panel Agent log",
                "log": f.readlines() }, None)

    def __call__(self, **kwargs):
        """
        """
        users = {}
        logs = self.load_logs(LOGINAGENT_PATH)
        for log in reversed(json.loads(logs)['log']):
            data = json.loads(log)
            if DateTime(data['date']).asdatetime().date() < datetime.today().date():
                break
