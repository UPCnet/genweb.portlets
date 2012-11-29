from zope.component import adapts
from zope.interface import Interface

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.portlets.browser.interfaces import IHomepagePortletManager

from zope.annotation.interfaces import IAnnotations

SPAN_KEY = 'genweb.portlets.span'


class GenwebPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the Genweb portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomepagePortletManager)
    template = ViewPageTemplateFile('templates/renderer.pt')

    def get_span(self):
        annotations = IAnnotations(self)
        return annotations.setdefault(SPAN_KEY, False)

    def prova(self):
        #import ipdb;ipdb.set_trace()
        pass


class gwContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IHomepagePortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')

    def get_span(self):
        annotations = IAnnotations(self)
        self.span = annotations.setdefault(SPAN_KEY, False)
        return self.span

    def set_span(self, value):
        annotations = IAnnotations(self)
        annotations.setdefault(SPAN_KEY, value)
        annotations[SPAN_KEY] = value

    span = property(get_span, set_span)


class setPortletHomeManagerSpan(BrowserView):
    def __call__(self):
        # import ipdb;ipdb.set_trace()
        pass
