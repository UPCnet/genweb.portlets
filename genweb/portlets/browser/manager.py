from zope import schema
from zope.component import adapts, getUtility, getMultiAdapter
from zope.interface import Interface, implements

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.browser.manage import ManageContextualPortlets
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.portlets.browser.interfaces import IHomepagePortletManager
from genweb.portlets.browser.interfaces import IHomePage
from genweb.portlets.utils import pref_lang

from plone.portlets.interfaces import IPortletManager

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations

from Acquisition import aq_inner

import json

SPAN_KEY = 'genweb.portlets.span.'


class GenwebPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the Genweb portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomepagePortletManager)
    template = ViewPageTemplateFile('templates/renderer.pt')

    def get_grid_portlets(self):
        unordered_portlets = self.allPortlets()

        allportlets = {}
        for portlet in unordered_portlets:
            allportlets[portlet['hash']] = portlet

        portletManager = getUtility(IPortletManager, name='genweb.portlets.HomePortletManager1')

        if IPloneSiteRoot.providedBy(self.context):
            homepage = self.context[self.context.default_page]
            # TODO: Make it multilingual aware
        else:
            homepage = self.context

        spanstorage = getMultiAdapter((homepage, portletManager), ISpanStorage)
        if spanstorage.span:
            positions = json.loads(spanstorage.span)
            index = {}
            # {1: [portlet1, portlet2]}
            for portlet in positions:
                index.setdefault(portlet['row'], [])
                portlet_info = allportlets.get(portlet['id'], False)
                if portlet_info:
                    index[portlet['row']].append(dict(row=portlet['row'],
                                                      col=portlet['col'],
                                                      size_x=portlet['size_x'],
                                                      size_y=portlet['size_y'],
                                                      hash=portlet['id'],
                                                      category=portlet_info['category'],
                                                      available=portlet_info['available'],
                                                      name=portlet_info['name'],
                                                      assignment=portlet_info['assignment'],
                                                      manager=portlet_info['manager'],
                                                      renderer=portlet_info['renderer'],
                                                      key=portlet_info['key']))
            grid_portlets = []
            for k in sorted(index.keys()):
                grid_portlets.append(sorted(index[k], key=lambda x: x['col']))

            return grid_portlets


class gwContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IHomepagePortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')

    def get_position(self, portlet_hash):
        portletManager = getUtility(IPortletManager, name='genweb.portlets.HomePortletManager1')

        if IPloneSiteRoot.providedBy(self.context):
            homepage = self.context[self.context.default_page]
            # TODO: Make it multilingual aware
        else:
            homepage = self.context

        spanstorage = getMultiAdapter((homepage, portletManager), ISpanStorage)
        if spanstorage.span:
            positions = json.loads(spanstorage.span)
            for position in positions:
                if position['id'] == portlet_hash:
                    return position

            # We have a new portlet in the house so update the annotation
            positions.append(dict(id=portlet_hash, row=1, col=1, size_x=1, size_y=1))
            spanstorage.span = json.dumps(positions)
            # And return a faked one for this time only
            return dict(row=1, col=1, size_x=1, size_y=1)

        # Is the first portlet so create the annotation
        spanstorage.span = json.dumps(dict(id=portlet_hash, row=1, col=1, size_x=1, size_y=1))

        # And return a faked one for this time only
        return dict(row=1, col=1, size_x=1, size_y=1)


class gwManageContextualPortlets(ManageContextualPortlets):
    """ Define our very own view for manage portlets """

    def getValue(self, manager):
        portletManager = getUtility(IPortletManager, name=manager)
        spanstorage = getMultiAdapter((self.context, portletManager), ISpanStorage)
        return spanstorage.span

    def get_span_value(self, manager, size):
        portletManager = getUtility(IPortletManager, name=manager)
        spanstorage = getMultiAdapter((self.context, portletManager), IScreenTypeSpanStorage)
        return getattr(spanstorage, size)

    def get_position(self, portlet_hash):
        positions = self.getValue('genweb.portlets.HomePortletManager1')
        for position in positions:
            if position['id'] == portlet_hash:
                return position


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


class IScreenTypeSpanStorage(IAttributeAnnotatable):
    """Marker persistent used to store per screen type column span number for
       portlet managers"""

    phone = schema.TextLine(title=u"Number of spans for this portletManager.")
    tablet = schema.TextLine(title=u"Number of spans for this portletManager.")
    desktop = schema.TextLine(title=u"Number of spans for this portletManager.")


class ScreenTypeSpanStorage(object):
    """Multiadapter that adapts any context and IPortletManager to provide
    IScreenTypeSpanStorage"""

    implements(IScreenTypeSpanStorage)
    adapts(Interface, IPortletManager)

    def __init__(self, context, manager):
        self.context = context
        self.manager = manager
        self.phone_key_id = SPAN_KEY + 'phone.' + manager.__name__
        self.tablet_key_id = SPAN_KEY + 'tablet.' + manager.__name__
        self.desktop_key_id = SPAN_KEY + 'desktop.' + manager.__name__

        annotations = IAnnotations(context)
        self._phone = annotations.setdefault(self.phone_key_id, '')
        self._tablet = annotations.setdefault(self.tablet_key_id, '')
        self._desktop = annotations.setdefault(self.desktop_key_id, '')

    def get_phone(self):
        annotations = IAnnotations(self.context)
        self._phone = annotations.setdefault(self.phone_key_id, '')
        return self._phone

    def set_phone(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(self.phone_key_id, value)
        annotations[self.phone_key_id] = value

    phone = property(get_phone, set_phone)

    def get_tablet(self):
        annotations = IAnnotations(self.context)
        self._tablet = annotations.setdefault(self.tablet_key_id, '')
        return self._tablet

    def set_tablet(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(self.tablet_key_id, value)
        annotations[self.tablet_key_id] = value

    tablet = property(get_tablet, set_tablet)

    def get_desktop(self):
        annotations = IAnnotations(self.context)
        self._desktop = annotations.setdefault(self.desktop_key_id, '')
        return self._desktop

    def set_desktop(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(self.desktop_key_id, value)
        annotations[self.desktop_key_id] = value

    desktop = property(get_desktop, set_desktop)


class setPortletHomeManagerSpan(BrowserView):
    """ View that stores the span number assigned to this portletManager for
        this context.
    """

    def getPortletContainer(self):
        context = aq_inner(self.context)
        container = context

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if IPloneSiteRoot.providedBy(self.context):
            pc = getToolByName(context, 'portal_catalog')
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      Language=pref_lang())
            if result:
                # Return the object without forcing a getObject()
                container = getattr(context, result[0].id, context)
        return container

    def __call__(self):
        position = self.request.form['position']
        portlet_container = self.getPortletContainer()
        portletManager = getUtility(IPortletManager, 'genweb.portlets.HomePortletManager1')
        spanstorage = getMultiAdapter((portlet_container, portletManager), ISpanStorage)
        spanstorage.span = position
        self.request.RESPONSE.setStatus('200')
        self.request.RESPONSE.setHeader('Content-type', 'application/json')
        return '{"status": "Saved!"}'
