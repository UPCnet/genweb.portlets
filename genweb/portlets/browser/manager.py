from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.portlets.browser.interfaces import IHomepagePortletManager


class GenwebPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the Genweb portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomepagePortletManager)
    template = ViewPageTemplateFile('templates/renderer.pt')


class gwContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IHomepagePortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')
