from zope import schema
from zope.component import adapts, getUtility, getMultiAdapter
from zope.interface import Interface, implements

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.browser.manage import ManageContextualPortlets
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.portlets.browser.interfaces import IHomepagePortletManager

from plone.portlets.interfaces import IPortletManager

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations

SPAN_KEY = 'genweb.portlets.span.'


class GenwebPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the Genweb portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomepagePortletManager)
    template = ViewPageTemplateFile('templates/renderer.pt')

    def prova(self):
        #import ipdb;ipdb.set_trace()
        pass


class gwContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IHomepagePortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')


class gwManageContextualPortlets(ManageContextualPortlets):
    """ Define our very own view for manage portlets """

    def getValue(self, manager):
        portletManager = getUtility(IPortletManager, name=manager)
        spanstorage = getMultiAdapter((self.context, portletManager), ISpanStorage)
        return spanstorage.span


class ISpanStorage(IAttributeAnnotatable):
    """Marker persistent used to store span number for portlet managers"""

    span = schema.TextLine(title=u"Number of spans for this portletManager.")


class SpanStorage(object):
    """Multiadapter that adapts any context and IPortletManager to provide ISpanStorage"""
    implements(ISpanStorage)
    adapts(Interface, IPortletManager)

    def __init__(self, context, manager):
        self.context = context
        self.manager = manager
        self.key_id = SPAN_KEY + manager.__name__

        annotations = IAnnotations(context)
        self._span = annotations.setdefault(self.key_id, '')

    def get_span(self):
        annotations = IAnnotations(self.context)
        self._span = annotations.setdefault(self.key_id, '')
        return self._span

    def set_span(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(self.key_id, value)
        annotations[self.key_id] = value

    span = property(get_span, set_span)


class setPortletHomeManagerSpan(BrowserView):
    """ View that stores the span number assigned to this portletManager for this context
    """
    def __call__(self):
        manager = self.request.form['manager']
        span = self.request.form['span']
        homepage_id = self.request.form['contextId']
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((self.context[homepage_id], portletManager), ISpanStorage)
        spanstorage.span = span
        self.request.RESPONSE.setStatus('200')
        self.request.RESPONSE.setHeader('Content-type', 'application/json')
        return '{"status": "Saved!"}'
        # manportview = getMultiAdapter((self.context, self.request), name='manage-homeportlets')
        # renderer = getMultiAdapter((self.context[homepage_id], self.request, manportview, portletManager), IPortletManagerRenderer)
