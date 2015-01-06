""" Controllers
"""
import os
import logging
import json
import pickle
import Globals
from DateTime import DateTime
from datetime import datetime
from zope.component import queryUtility, queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api

LOGINAGENT_PATH = os.environ.get('EEALOGINAGENT_LOG')
if not LOGINAGENT_PATH:
    LOGINAGENT_PATH = Globals.ZOPE_HOME + "/var/log"
LOGINAGENT_PATH += "/loginagent.log"
import pdb; pdb.set_trace()

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
        active_users = {}
        logs = self.load_logs(LOGINAGENT_PATH)
        for log in reversed(json.loads(logs)['log']):
            data = json.loads(log)
            log_date = DateTime(data['date']).asdatetime().date()
            today = datetime.today().date()
            if log_date < today:
                break
            last_active = DateTime() - DateTime(data['date'])

            status = True
            if last_active > 0.004:
                status = False
            if active_users.has_key(data['username']) and not status:
                if active_users[data['username']][1]:
                    status = True

            last_online = DateTime(data['date'])
            if active_users.has_key(data['username']) and last_online < active_users[data['username']][2]:
                last_online = active_users[data['username']][2]

            active_users[data['username']] = (data['fullname'], status, last_online)
        return jsonify({"active_users": active_users }, self.request.response)
