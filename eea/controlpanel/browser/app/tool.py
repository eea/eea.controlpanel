""" Controllers
"""
import logging
import json
from zope.component import queryUtility, queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from plone import api


logger = logging.getLogger('eea.controlpanel')

class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, DateTime):
            return obj.asdatetime().strftime("%Y-%m-%d %H:%M:%S")
        return {'_python_object': pickle.dumps(obj)}

def jsonify(data, response=None, status=None):
    """ Convert obj to JSON
    """
    if response:
        response.setHeader("Content-type", "application/json")
        if status:
            response.setStatus(status)
    #return json.dumps(data)
    return PythonObjectEncoder(indent=2, sort_keys=True).encode(data)


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
