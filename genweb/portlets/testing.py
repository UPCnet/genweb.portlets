from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig

class GenwebPortlets(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import genweb.portlets
        xmlconfig.file('configure.zcml',
                       genweb.portlets,
                       context=configurationContext)
        
    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'genweb.portlets:default')



GENWEB_PORTLETS_FIXTURE = GenwebPortlets()
GENWEB_PORTLETS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GENWEB_PORTLETS_FIXTURE,),
    name="GenwebPortlets:Integration")
GENWEB_PORTLETS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GENWEB_PORTLETS_FIXTURE,),
    name="GenwebPortlets:Functional")
