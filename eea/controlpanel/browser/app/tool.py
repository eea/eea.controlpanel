""" Controllers
"""
import logging
from zope.component import queryUtility, queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger('eea.controlpanel')

class ControlPanel(BrowserView):
    """
    """

