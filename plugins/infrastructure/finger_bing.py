'''
finger_bing.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

import core.controllers.outputManager as om
import core.data.kb.knowledgeBase as kb
import core.data.kb.info as info
import core.data.parsers.dpCache as dpCache

from core.controllers.plugins.infrastructure_plugin import InfrastructurePlugin
from core.controllers.w3afException import w3afException, w3afMustStopOnUrlError
from core.controllers.w3afException import w3afRunOnce
from core.controllers.misc.decorators import runonce
from core.controllers.misc.is_private_site import is_private_site

from core.data.search_engines.bing import bing as bing
from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList


class finger_bing(InfrastructurePlugin):
    '''
    Search Bing to get a list of users for a domain.
    @author: Andres Riancho (andres.riancho@gmail.com)
    '''

    def __init__(self):
        InfrastructurePlugin.__init__(self)
        
        # Internal variables
        self._accounts = []

        # User configured 
        self._result_limit = 300

    @runonce(exc_class=w3afRunOnce)
    def discover(self, fuzzable_request):
        '''
        @parameter fuzzable_request: A fuzzable_request instance that contains 
        (among other things) the URL to test.
        '''
        if not is_private_site( fuzzable_request.getURL().getDomain() ):
            bingSE = bing(self._uri_opener)
            self._domain = fuzzable_request.getURL().getDomain()
            self._domain_root = fuzzable_request.getURL().getRootDomain()
        
            results = bingSE.getNResults('@'+self._domain_root, self._result_limit)

            #   Send the requests using threads:
            self._tm.threadpool.map(self._find_accounts, results)            
        
            self.print_uniq(kb.kb.get('finger_bing', 'emails'), None)

    def _find_accounts(self, page):
        '''
        Finds emails in bing result.

        @return: A list of valid accounts
        '''
        try:
            url = page.URL
            om.out.debug('Searching for emails in: %s' % url)
            
            grep = True if self._domain == url.getDomain() else False
            response = self._uri_opener.GET(page.URL, cache=True,
                                           grep=grep)
        except w3afMustStopOnUrlError:
            # Just ignore it
            pass
        except w3afException, w3:
            msg = 'xUrllib exception raised while fetching page in finger_bing,'
            msg += ' error description: ' + str(w3)
            om.out.debug(msg)
        else:
            
            # I have the response object!
            try:
                document_parser = dpCache.dpc.getDocumentParserFor(response)
            except w3afException:
                # Failed to find a suitable parser for the document
                pass
            else:
                # Search for email addresses
                for mail in document_parser.getEmails(self._domain_root):
                    if mail not in self._accounts:
                        self._accounts.append( mail )

                        i = info.info()
                        i.setPluginName(self.get_name())
                        i.setURL(page.URL)
                        i.set_name(mail)
                        msg = 'The mail account: "'+ mail + '" was found in: "' + page.URL + '"'
                        i.set_desc( msg )
                        i['mail'] = mail
                        i['user'] = mail.split('@')[0]
                        i['url_list'] = [page.URL, ]
                        kb.kb.append( 'emails', 'emails', i )
                        kb.kb.append( 'finger_bing', 'emails', i )

    def get_options( self ):
        '''
        @return: A list of option objects for this plugin.
        '''
        ol = OptionList()
        
        d1 = 'Fetch the first "result_limit" results from the Bing search'
        o = opt_factory('result_limit', self._result_limit, d1, 'integer')
        ol.add(o)
        
        return ol

    def set_options( self, options_list ):
        '''
        This method sets all the options that are configured using the user interface
        generated by the framework using the result of get_options().

        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        '''
        self._result_limit = options_list['result_limit'].get_value()

    def get_long_desc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin finds mail addresses in Bing search engine.

        One configurable parameter exist:
            - result_limit

        This plugin searches Bing for : "@domain.com", requests all search results
        and parses them in order to find new mail addresses.
        '''
