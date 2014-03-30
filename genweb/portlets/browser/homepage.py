# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from five import grok
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.contentprovider import interfaces
from zope.interface import alsoProvides
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.contenttypes.interfaces import IDocument
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from genweb.portlets.browser.interfaces import IHomePage
from genweb.portlets.utils import pref_lang
from genweb.portlets.browser.manager import IScreenTypeSpanStorage
from genweb.portlets.browser.interfaces import IHomePageView


class enableHomepage(grok.View):
    grok.context(IDocument)

    def render(self):
        portal = getSite()
        alsoProvides(self.context, IHomePage)
        portal.setDefaultPage('homepage')


class HomePageBase(grok.View):
    """ Base methods for ease the extension of the genweb homePage view. Just
        define a new class inheriting from this one and redefine the basic
        grokkers like:

        class HomePage(HomePageBase):
            grok.implements(IHomePageView)
            grok.context(IPloneSiteRoot)
            grok.require('genweb.authenticated')
            grok.layer(IUlearnTheme)

        Overriding the one in this module (homePage) with a more specific
        interface.
    """
    grok.baseclass()

    def update(self):
        self.portlet_container = self.getPortletContainer()

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

    def renderProviderByName(self, provider_name):
        provider = queryMultiAdapter(
            (self.portlet_container, self.request, self),
            interfaces.IContentProvider, provider_name)

        provider.update()

        return provider.render()

    def getSpanValueForManager(self, manager):
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((self.portlet_container, portletManager), IScreenTypeSpanStorage)
        phone = spanstorage.phone
        tablet = spanstorage.tablet
        desktop = spanstorage.desktop
        klass = ''

        if desktop:
            klass = 'col-lg-{} col-md-{}'.format(desktop, desktop)
        else:
            klass = 'col-lg-4 col-md-4'

        if tablet:
            klass = '{} col-sm-{}'.format(klass, tablet)

        if phone:
            klass = '{} col-xs-{}'.format(klass, phone)

        return klass

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.portlet_container
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible


class View(HomePageBase):
    """ This is the special view for the homepage containing support for the
        portlet managers provided by the package genweb.portlets.
        It's restrained to IGenwebTheme layer to prevent it will interfere with
        the one defined in the Genweb legacy theme (v4).
    """
    grok.implements(IHomePageView)
    grok.context(IHomePage)
