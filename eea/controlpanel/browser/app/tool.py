""" Controllers
"""
import logging
import json
import pickle
from datetime import datetime
from DateTime import DateTime
from eea.controlpanel.browser.app.utils import get_logs_path
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode
from plone import api

LOGINAGENT_PATH = get_logs_path('EEALOGINAGENT_LOG') + "/eealogin.log"
EEACPBINSTANCESAGENT_PATH = get_logs_path('EEACPBINSTANCESAGENT_LOG') +\
    "/eeacpbinstances.log"

LOGGER = logging.getLogger('eea.controlpanel')
LOGINAGENTLOGGER = logging.getLogger("eea.controlpanel.loginagent")
EEACPBAGENTLOGGER = logging.getLogger("eea.controlpanel.eeacpbagent")
LOGINHANDLER = logging.handlers.RotatingFileHandler(LOGINAGENT_PATH,
                                                    maxBytes=52428800,
                                                    backupCount=10)
EEACPBHANDLER = logging.handlers.RotatingFileHandler(EEACPBINSTANCESAGENT_PATH,
                                                     maxBytes=52428800,
                                                     backupCount=10)
LOGINAGENTLOGGER.addHandler(LOGINHANDLER)
LOGINAGENTLOGGER.setLevel(logging.DEBUG)
EEACPBAGENTLOGGER.addHandler(EEACPBHANDLER)
EEACPBAGENTLOGGER.setLevel(logging.DEBUG)


def jsonify(data, response=None, status=None):
    """ Convert obj to JSON
    """
    if response:
        response.setHeader("Content-type", "application/json")
        if status:
            response.setStatus(status)
    try:
        return PythonObjectEncoder(indent=2, sort_keys=True).encode(data)
    except UnicodeDecodeError:
        # Fix case when undoable_transactions send trunkated unicode
        data_safe = []
        for k in data['log']:
            dic_safe = {}
            for m in k.keys():
                dic_safe[m] = safe_unicode(k[m])
            data_safe.append(dic_safe)
        data['log'] = data_safe
        return PythonObjectEncoder(indent=2, sort_keys=True).encode(data)


class PythonObjectEncoder(json.JSONEncoder):
    """ Python Object Encoder
    """
    def default(self, obj):     # pylint: disable=E0202
        o_types = (list, dict, str, unicode, int, float, bool, type(None))
        if isinstance(obj, o_types):
            return json.JSONEncoder.default(self, obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, DateTime):
            return obj.asdatetime().strftime("%Y-%m-%d %H:%M:%S")
        return {'_python_object': pickle.dumps(obj)}


class ControlPanel(BrowserView):
    """ Control Panel view
    """


class ControlPanelDBActivity(BrowserView):
    """ ControlPanel DB Activity view
    """

    def __call__(self, **kwargs):
        """
        """
        result = {"name": "EEA Control Panel API",
                  "log": {}}
        if not api.user.is_anonymous():
            portal = api.portal.get()
            result['log'] = portal.undoable_transactions(first_transaction=0,
                                                        last_transaction=10000)
        return jsonify(result, self.request.response)


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
            LOGINAGENTLOGGER.debug(json.dumps(data))


class ControlPanelLoginStatus(BrowserView):
    """ ControlPanel Login status view
    """

    def load_logs(self, logpath):
        """ Load the log file
        """
        with open(logpath, "r") as f:
            return jsonify({
                "name": "EEA Control Panel Agent log",
                "log": f.readlines()}, None)

    def get_results(self):
        """ Extract login status information
        """
        active_users = {}
        logs = self.load_logs(LOGINAGENT_PATH)
        for log in reversed(json.loads(logs)['log']):
            # quick fix for #22658
            try:
                data = json.loads(log)
            except ValueError:
                continue
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
            if active_users.has_key(data['username']):
                if last_online < active_users[data['username']][2]:
                    last_online = active_users[data['username']][2]

            active_users[data['username']] = (data['fullname'],
                                              status,
                                              last_online)
        return active_users

    def __call__(self, **kwargs):
        """
        """
        result = {'active_users': {}}
        if not api.user.is_anonymous():
            result['active_users'] = self.get_results()
        return jsonify(result, self.request.response)


class ControlPanelEEACPBStatusAgent(BrowserView):
    """ EEA CPB deployments status
    """

    def get_ip(self):
        """ Extract the client IP address from the HTTP request in a
        proxy-compatible way.
        @return: IP address as a string or None if not available
        """
        request = self.request
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            # Virtual host
            ip = request.environ["HTTP_X_FORWARDED_FOR"]
        elif "REMOTE_ADDR" in request.environ:
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
                EEACPBAGENTLOGGER.debug(json.dumps(data))

                return 'OK'


class ControlPanelEEACPBStatus(BrowserView):
    """ ControlPanel EEA CPB status view
    """

    def load_logs(self, logpath):
        """ Load the log file
        """
        with open(logpath, "r") as f:
            return jsonify({
                "name": "EEA Control Panel Agent log",
                "log": f.readlines()}, None)

    def get_results(self):
        """ Extract EEA CPB usage
        """
        active_ips = {}
        logs = self.load_logs(EEACPBINSTANCESAGENT_PATH)

        for log in reversed(json.loads(logs)['log']):
            data = json.loads(log)

            last_active = DateTime() - DateTime(data['date'])
            status = True
            if last_active > 7:
                status = False

            hostnames = data.get('hostnames')

            if active_ips.has_key(data['ip']):
                if not status:
                    if active_ips[data['ip']].get('status'):
                        status = True

                hostnames = list(
                    set(active_ips[data['ip']]['hostnames'] + hostnames)
                )

            last_ping = DateTime(data['date'])

            active_ips[data['ip']] = {
                'hostnames': hostnames,
                'status': status,
                'last_ping': last_ping
            }
        return active_ips

    def __call__(self, **kwargs):
        """
        """
        results = {'active_ips': {}}
        if not api.user.is_anonymous():
            results['active_ips'] = self.get_results()
        return jsonify(results, self.request.response)
