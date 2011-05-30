import unittest2 as unittest
from genweb.portlets.testing import GENWEB_PORTLETS_INTEGRATION_TESTING

class IntegrationTest(unittest.TestCase):

    layer = GENWEB_PORTLETS_INTEGRATION_TESTING

    def testInterfaceAvailable(self):
        """
        Is our product-specific interface available?
        """
        from plone.browserlayer import utils
        from genweb.portlets.browser.interfaces import IGenwebPortlets
        self.failUnless(IGenwebPortlets in utils.registered_layers(), 'Cannot find IContentWellPortlets interface')

    def testPortletManagers(self):
        """
        Are our portlet managers available? Test by inserting a calendar portlet
        """
        from zope.component import getUtility, getMultiAdapter
        from plone.app.portlets.portlets import calendar
        from plone.portlets.interfaces import IPortletManager
        from plone.portlets.interfaces import IPortletRenderer
        
        portal = self.layer['portal']
        
        # get the portlet managers we should have created
        manager1 = getUtility(IPortletManager, name='genweb.portlets.HomePortletManager1',context=portal)
        manager2 = getUtility(IPortletManager, name='genweb.portlets.HomePortletManager2',context=portal)
        manager3 = getUtility(IPortletManager, name='genweb.portlets.HomePortletManager3',context=portal)
        
        # try rendering a portlet with it using getMultiAdapter((context, request, view, manager, assignment), Interface)
        renderer = getMultiAdapter((portal, portal.REQUEST, portal.restrictedTraverse('@@plone'), manager1, calendar.Assignment()), IPortletRenderer)
        self.failUnless(isinstance(renderer, calendar.Renderer), 'Cannot render portlet HomePortletManager1')
        
        renderer = getMultiAdapter((portal, portal.REQUEST, portal.restrictedTraverse('@@plone'), manager2, calendar.Assignment()), IPortletRenderer)
        self.failUnless(isinstance(renderer, calendar.Renderer), 'Cannot render portlet HomePortletManager2')
        
        renderer = getMultiAdapter((portal, portal.REQUEST, portal.restrictedTraverse('@@plone'), manager3, calendar.Assignment()), IPortletRenderer)
        self.failUnless(isinstance(renderer, calendar.Renderer), 'Cannot render portlet HomePortletManager3')
