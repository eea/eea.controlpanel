""" Controllers
"""
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

LOGS_DIR = Globals.ZOPE_HOME + "/var/log/"
LOGINAGENT_PATH = LOGS_DIR + "loginagent.log"
EEACPBINSTANCESAGENT_PATH = LOGS_DIR + "eeacpbinstances.log"
logger = logging.getLogger('eea.controlpanel')
loginagentlogger = logging.getLogger("eea.controlpanel.loginagent")
eeacpbagentlogger = logging.getLogger("eea.controlpanel.eeacpbagent")
loginhandler = logging.handlers.RotatingFileHandler(LOGINAGENT_PATH, maxBytes=52428800, backupCount=10)
eeacpbhandler = logging.handlers.RotatingFileHandler(EEACPBINSTANCESAGENT_PATH, maxBytes=52428800, backupCount=10)
loginagentlogger.addHandler(loginhandler)
loginagentlogger.setLevel(logging.DEBUG)
eeacpbagentlogger.addHandler(eeacpbhandler)
eeacpbagentlogger.setLevel(logging.DEBUG)


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


class ControlPanelEEACPBStatusAgent(BrowserView):
    """ EEA CPB deployments status
    """

    def get_ip(self):
        """ Extract the client IP address from the HTTP request in a proxy-compatible way.

        @return: IP address as a string or None if not available
        """
        request = self.request
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            # Virtual host
            ip = request.environ["HTTP_X_FORWARDED_FOR"]
        elif "HTTP_HOST" in request.environ:
            # Non-virtualhost
            ip = request.environ["REMOTE_ADDR"]
        else:
            ip = None

        return ip

    def __call__(self, **kwargs):
        """
        """

        client_ip = self.get_ip()
        if client_ip and self.request.method == 'POST':
            localized = api.portal.get_localized_time(datetime=DateTime(),
                                                      long_format=True)
            hostnames = self.request.form.get('hostnames')
            if hostnames:
                if not isinstance(hostnames, list):
                    hostnames = [hostnames]
                data = {
                    'ip': client_ip,
                    'hostnames': hostnames,
                    'date': localized
                }
                eeacpbagentlogger.debug(json.dumps(data))


class ControlPanelEEACPBStatus(BrowserView):
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
        active_ips = {}
        logs = self.load_logs(EEACPBINSTANCESAGENT_PATH)

        for log in reversed(json.loads(logs)['log']):
            data = json.loads(log)
            log_date = DateTime(data['date']).asdatetime().date()
            today = datetime.today().date()

            last_active = DateTime() - DateTime(data['date'])

            status = True
            if last_active > 0.004:
                status = False

            hostnames = data.get('hostnames')

            if active_ips.has_key(data['ip']):
                if not status:
                    if active_ips[data['ip']].get('status'):
                        status = True

                hostnames = list(
                    set(active_ips[data['ip']]['hostnames'] + hostnames)
                )

            last_online = DateTime(data['date'])

            active_ips[data['ip']] = {
                'hostnames': hostnames,
                'status': status,
                'last_online': last_online
            }

        return jsonify({"active_ips": active_ips }, self.request.response)
