from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName


def pref_lang():
    """ Extracts the current language for the current user
    """
    lt = getToolByName(getSite(), 'portal_languages')
    return lt.getPreferredLanguage()
